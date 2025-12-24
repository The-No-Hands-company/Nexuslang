"""
HTTP Client for NLPL.
Provides requests-like functionality for HTTP operations.
"""

import urllib.request
import urllib.parse
import urllib.error
import json as json_lib
from typing import Optional, Dict, Any
from ...runtime.runtime import Runtime


class HTTPResponse:
    """HTTP response wrapper."""
    def __init__(self, status_code: int, headers: dict, body: bytes, url: str):
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.url = url
        self._text = None
        self._json = None
    
    @property
    def text(self) -> str:
        """Get response body as text."""
        if self._text is None:
            self._text = self.body.decode('utf-8', errors='replace')
        return self._text
    
    @property
    def json(self) -> Any:
        """Parse response body as JSON."""
        if self._json is None:
            self._json = json_lib.loads(self.text)
        return self._json
    
    @property
    def ok(self) -> bool:
        """Check if request was successful (status 200-299)."""
        return 200 <= self.status_code < 300


def http_request(method: str, url: str, headers: Optional[Dict] = None, 
                 data: Optional[Any] = None, timeout: int = 30) -> HTTPResponse:
    """Make HTTP request."""
    # Prepare headers
    req_headers = headers or {}
    
    # Prepare data
    req_data = None
    if data is not None:
        if isinstance(data, dict):
            req_data = json_lib.dumps(data).encode('utf-8')
            req_headers['Content-Type'] = 'application/json'
        elif isinstance(data, str):
            req_data = data.encode('utf-8')
        elif isinstance(data, bytes):
            req_data = data
    
    # Create request
    request = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = response.status
            headers = dict(response.headers)
            body = response.read()
            return HTTPResponse(status_code, headers, body, url)
    except urllib.error.HTTPError as e:
        # Return error response
        return HTTPResponse(e.code, dict(e.headers), e.read(), url)
    except urllib.error.URLError as e:
        raise RuntimeError(f"HTTP request failed: {e.reason}")


def http_get(url: str, headers: Optional[Dict] = None, timeout: int = 30) -> HTTPResponse:
    """Make HTTP GET request."""
    return http_request("GET", url, headers=headers, timeout=timeout)


def http_post(url: str, data: Optional[Any] = None, headers: Optional[Dict] = None, 
              timeout: int = 30) -> HTTPResponse:
    """Make HTTP POST request."""
    return http_request("POST", url, headers=headers, data=data, timeout=timeout)


def http_put(url: str, data: Optional[Any] = None, headers: Optional[Dict] = None,
             timeout: int = 30) -> HTTPResponse:
    """Make HTTP PUT request."""
    return http_request("PUT", url, headers=headers, data=data, timeout=timeout)


def http_delete(url: str, headers: Optional[Dict] = None, timeout: int = 30) -> HTTPResponse:
    """Make HTTP DELETE request."""
    return http_request("DELETE", url, headers=headers, timeout=timeout)


def http_patch(url: str, data: Optional[Any] = None, headers: Optional[Dict] = None,
               timeout: int = 30) -> HTTPResponse:
    """Make HTTP PATCH request."""
    return http_request("PATCH", url, headers=headers, data=data, timeout=timeout)


def http_head(url: str, headers: Optional[Dict] = None, timeout: int = 30) -> HTTPResponse:
    """Make HTTP HEAD request."""
    return http_request("HEAD", url, headers=headers, timeout=timeout)


def url_encode(params: Dict[str, str]) -> str:
    """URL encode parameters."""
    return urllib.parse.urlencode(params)


def url_decode(query_string: str) -> Dict[str, str]:
    """Decode URL query string."""
    return dict(urllib.parse.parse_qsl(query_string))


def url_parse(url: str) -> dict:
    """Parse URL into components."""
    parsed = urllib.parse.urlparse(url)
    return {
        'scheme': parsed.scheme,
        'netloc': parsed.netloc,
        'path': parsed.path,
        'params': parsed.params,
        'query': parsed.query,
        'fragment': parsed.fragment,
        'hostname': parsed.hostname,
        'port': parsed.port,
        'username': parsed.username,
        'password': parsed.password,
    }


def url_join(base: str, path: str) -> str:
    """Join base URL with path."""
    return urllib.parse.urljoin(base, path)


def download_file(url: str, filepath: str, timeout: int = 30) -> bool:
    """Download file from URL."""
    try:
        urllib.request.urlretrieve(url, filepath)
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def get_response_text(response: HTTPResponse) -> str:
    """Get response body as text."""
    return response.text


def get_response_json(response: HTTPResponse) -> Any:
    """Parse response body as JSON."""
    return response.json


def get_response_status(response: HTTPResponse) -> int:
    """Get response status code."""
    return response.status_code


def get_response_headers(response: HTTPResponse) -> dict:
    """Get response headers."""
    return response.headers


def is_response_ok(response: HTTPResponse) -> bool:
    """Check if response is successful."""
    return response.ok


def register_http_functions(runtime: Runtime) -> None:
    """Register HTTP functions with the runtime."""
    
    # HTTP methods
    runtime.register_function("http_get", http_get)
    runtime.register_function("http_post", http_post)
    runtime.register_function("http_put", http_put)
    runtime.register_function("http_delete", http_delete)
    runtime.register_function("http_patch", http_patch)
    runtime.register_function("http_head", http_head)
    runtime.register_function("http_request", http_request)
    
    # URL utilities
    runtime.register_function("url_encode", url_encode)
    runtime.register_function("url_decode", url_decode)
    runtime.register_function("url_parse", url_parse)
    runtime.register_function("url_join", url_join)
    
    # Download
    runtime.register_function("download_file", download_file)
    
    # Response utilities
    runtime.register_function("get_response_text", get_response_text)
    runtime.register_function("get_response_json", get_response_json)
    runtime.register_function("get_response_status", get_response_status)
    runtime.register_function("get_response_headers", get_response_headers)
    runtime.register_function("is_response_ok", is_response_ok)
    
    # Aliases
    runtime.register_function("GET", http_get)
    runtime.register_function("POST", http_post)
    runtime.register_function("PUT", http_put)
    runtime.register_function("DELETE", http_delete)
