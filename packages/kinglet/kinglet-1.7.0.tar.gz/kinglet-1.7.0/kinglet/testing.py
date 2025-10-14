"""
Kinglet Testing Utilities - TestClient and Mock classes
"""

import json


class TestClient:
    """Simple sync wrapper for testing Kinglet apps without HTTP/Wrangler overhead"""

    __test__ = False  # Tell pytest this is not a test class

    def __init__(self, app, base_url="https://testserver", env=None):
        self.app = app
        self.base_url = base_url.rstrip("/")
        self.env = env or {}

        # Enable test mode on the app if it's a Kinglet instance
        if hasattr(app, "test_mode"):
            app.test_mode = True

    def request(
        self, method: str, path: str, json_data=None, data=None, headers=None, **kwargs
    ):
        """Make a test request and return (status, headers, body)"""
        import asyncio

        return asyncio.run(
            self._async_request(method, path, json_data, data, headers, **kwargs)
        )

    def _prepare_request_data(self, json_data, data, headers, kwargs):
        """Prepare request headers and body content"""
        # Handle 'json' keyword argument (common in test APIs)
        if "json" in kwargs and json_data is None:
            json_data = kwargs.pop("json")

        # Prepare headers
        test_headers = {"content-type": "application/json"} if json_data else {}
        if headers:
            test_headers.update({k.lower(): v for k, v in headers.items()})

        # Prepare body
        body_content = ""
        if json_data is not None:
            body_content = json.dumps(json_data)
            test_headers["content-type"] = "application/json"
        elif data is not None:
            body_content = str(data)

        return test_headers, body_content

    def _serialize_response_content(self, content):
        """Serialize response content for test consumption"""
        if isinstance(content, dict | list):
            return json.dumps(content)
        return str(content) if content is not None else ""

    def _handle_kinglet_response(self, response):
        """Handle Kinglet Response objects"""
        if hasattr(response, "status") and hasattr(response, "content"):
            status = response.status
            headers = response.headers
            content = response.content
            body = self._serialize_response_content(content)
            return status, headers, body
        return None

    def _handle_raw_response(self, response):
        """Handle raw response objects (dict, string, etc.)"""
        if isinstance(response, dict):
            return 200, {}, json.dumps(response)
        elif isinstance(response, str):
            return 200, {}, response
        else:
            return 200, {}, str(response)

    async def _async_request(
        self, method: str, path: str, json_data=None, data=None, headers=None, **kwargs
    ):
        """Internal async request handler"""
        test_headers, body_content = self._prepare_request_data(
            json_data, data, headers, kwargs
        )
        url = f"{self.base_url}{path}"

        # Create mock objects
        mock_request = MockRequest(method, url, test_headers, body_content)
        mock_env = MockEnv(self.env)

        try:
            response = await self.app(mock_request, mock_env)

            # Try to handle as Kinglet Response first
            kinglet_result = self._handle_kinglet_response(response)
            if kinglet_result:
                return kinglet_result

            # Handle as raw response
            return self._handle_raw_response(response)

        except Exception as e:
            error_body = json.dumps({"error": str(e)})
            return 500, {}, error_body


class MockRequest:
    """Mock request object for testing that matches Workers request interface"""

    def __init__(self, method: str, url: str, headers: dict, body: str = ""):
        self.method = method
        self.url = url
        self.headers = MockHeaders(headers)
        self._body = body

    async def text(self):
        return self._body

    async def json(self):
        if self._body:
            return json.loads(self._body)
        return None


class MockHeaders:
    """Mock headers object that matches Workers headers interface"""

    def __init__(self, headers_dict):
        self._headers = {k.lower(): v for k, v in (headers_dict or {}).items()}

    def get(self, key, default=None):
        return self._headers.get(key.lower(), default)

    def items(self):
        return self._headers.items()

    def __iter__(self):
        return iter(self._headers.items())


class MockEnv:
    """Mock environment object for testing"""

    def __init__(self, env_dict):
        # Set defaults for common Cloudflare bindings
        self.DB = env_dict.get("DB", MockDatabase())
        self.ENVIRONMENT = env_dict.get("ENVIRONMENT", "test")

        # Add any additional environment variables
        for key, value in env_dict.items():
            setattr(self, key, value)


class MockDatabase:
    """Mock D1 database for testing"""

    def __init__(self):
        self._data = {}

    def prepare(self, sql: str):
        return MockQuery(sql, self._data)


class MockQuery:
    """Mock D1 prepared statement"""

    def __init__(self, sql: str, data: dict):
        self.sql = sql
        self.data = data
        self.bindings = []

    def bind(self, *args):
        self.bindings = args
        return self

    async def run(self):
        return MockResult({"changes": 1, "last_row_id": 1})

    async def first(self):
        return MockRow({"id": 1, "name": "Test"})

    async def all(self):
        return MockResult([{"id": 1, "name": "Test"}])


class MockRow:
    """Mock D1 row result with to_py() method"""

    def __init__(self, data):
        self.data = data

    def to_py(self):
        return self.data


class MockResult:
    """Mock D1 query result"""

    def __init__(self, data):
        if isinstance(data, dict):
            self.meta = data
            self.results = []
        else:
            self.results = data
            self.meta = {"changes": len(data)}
