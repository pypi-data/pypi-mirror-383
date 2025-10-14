"""
Kinglet Middleware - Base classes and common middleware implementations
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Callable

from .http import Response
from .orm_errors import ERROR_TYPE_MAP, ORMError, orm_problem_response


class Middleware(ABC):
    """Abstract base class for middleware"""

    @abstractmethod
    async def process_request(self, request):
        """Process incoming request, return Response to short-circuit or None to continue"""
        pass

    @abstractmethod
    async def process_response(self, request, response):
        """Process outgoing response, return modified Response"""
        pass


class CorsMiddleware(Middleware):
    """CORS middleware for handling cross-origin requests"""

    def __init__(
        self,
        allow_origin="*",
        allow_methods="GET,POST,PUT,DELETE,OPTIONS",
        allow_headers="Content-Type,Authorization",
    ):
        self.allow_origin = allow_origin
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers

    async def process_request(self, request):
        """Handle OPTIONS preflight requests"""
        if request.method == "OPTIONS":
            return Response("", status=200).cors(
                origin=self.allow_origin,
                methods=self.allow_methods,
                headers=self.allow_headers,
            )
        return None

    async def process_response(self, request, response):
        """Add CORS headers to all responses"""
        if not hasattr(response, "cors"):
            # Handle non-Response objects
            if isinstance(response, dict):
                response = Response(response)
            else:
                return response

        return response.cors(
            origin=self.allow_origin,
            methods=self.allow_methods,
            headers=self.allow_headers,
        )


class TimingMiddleware(Middleware):
    """Middleware to add timing information to responses"""

    async def process_request(self, request):
        """Record start time"""
        request._start_time = time.time()
        return None

    async def process_response(self, request, response):
        """Add timing header"""
        if hasattr(request, "_start_time"):
            duration = time.time() - request._start_time
            if hasattr(response, "header"):
                response.header("X-Response-Time", f"{duration:.3f}s")
        return response


class ORMErrorMiddleware(Middleware):
    """
    Central ORM error handling middleware with RFC7807 problem+json responses

    Catches all ORM errors and converts them to standardized problem+json responses
    with appropriate HTTP status codes and headers. Provides production-safe field
    redaction and correlation ID support.

    Usage:
        app = Kinglet()
        app.add_middleware(ORMErrorMiddleware(is_prod=env.MODE == "prod"))
    """

    def __init__(
        self,
        *,
        is_prod: bool = False,
        error_type_map: dict[str, tuple] | None = None,
        correlation_header: str = "X-Request-Id",
        include_trace: bool = False,
    ):
        self.is_prod = is_prod
        self.error_type_map = error_type_map or ERROR_TYPE_MAP
        self.correlation_header = correlation_header
        self.include_trace = include_trace

    async def process_request(self, request):
        """No request processing needed"""
        return None

    async def process_response(self, request, response):
        """No response processing needed - errors are caught by error boundary"""
        return response

    def _get_correlation_instance(self, request):
        """Extract correlation ID instance for tracing"""
        if hasattr(request, "headers") and self.correlation_header in request.headers:
            return f"/requests/{request.headers[self.correlation_header]}"
        return None

    def _add_trace_if_enabled(self, problem):
        """Add stack trace to problem if trace is enabled and not in prod"""
        if not self.is_prod and self.include_trace:
            import traceback

            problem["trace"] = traceback.format_exc()

    def _handle_orm_error(self, request, error):
        """Handle ORM-specific errors"""
        instance = self._get_correlation_instance(request)
        problem, status, headers = orm_problem_response(
            error, instance=instance, is_prod=self.is_prod
        )
        self._add_trace_if_enabled(problem)
        return Response(problem, status=status, headers=headers)

    def _handle_generic_error(self, request, error):
        """Handle generic non-ORM errors"""
        instance = self._get_correlation_instance(request)

        problem = {
            "type": "https://errors.kinglet.dev/internal",
            "title": "Internal server error",
            "status": 500,
            "detail": "An unexpected error occurred" if self.is_prod else str(error),
            "code": error.__class__.__name__,
        }

        if instance:
            problem["instance"] = instance

        self._add_trace_if_enabled(problem)
        headers = {"Content-Type": "application/problem+json"}
        return Response(problem, status=500, headers=headers)

    def create_error_boundary(self, handler: Callable) -> Callable:
        """
        Create error boundary wrapper for route handlers

        This should be applied to your main route handler to catch and convert
        ORM errors to problem+json responses.

        Args:
            handler: Async route handler function

        Returns:
            Wrapped handler that catches ORM errors

        Example:
            @app.route("/api/users")
            @orm_middleware.create_error_boundary
            async def create_user(request, env):
                # Your handler code here
                user = await User.objects.create(db, **data)
                return {"user": user.to_dict()}
        """

        async def error_boundary_wrapper(request, env):
            try:
                return await handler(request, env)
            except ORMError as e:
                return self._handle_orm_error(request, e)
            except Exception as e:
                return self._handle_generic_error(request, e)

        return error_boundary_wrapper


def create_global_error_boundary(
    *,
    is_prod: bool = False,
    error_type_map: dict[str, tuple] | None = None,
    correlation_header: str = "X-Request-Id",
    include_trace: bool = False,
) -> Callable[[Callable], Callable]:
    """
    Factory function to create a global error boundary decorator

    This is a convenience function for creating error boundaries without
    instantiating the middleware class.

    Args:
        is_prod: Whether running in production mode (affects field redaction)
        error_type_map: Custom error type mapping (status, uri, title)
        correlation_header: Header name for correlation/request ID
        include_trace: Whether to include stack traces in dev mode

    Returns:
        Decorator function that can be applied to route handlers

    Example:
        error_boundary = create_global_error_boundary(is_prod=env.MODE == "prod")

        @app.route("/api/users")
        @error_boundary
        async def create_user(request, env):
            user = await User.objects.create(env.DB, **data)
            return {"user": user.to_dict()}
    """
    middleware = ORMErrorMiddleware(
        is_prod=is_prod,
        error_type_map=error_type_map,
        correlation_header=correlation_header,
        include_trace=include_trace,
    )
    return middleware.create_error_boundary
