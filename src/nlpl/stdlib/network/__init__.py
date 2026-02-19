"""
Network module for the NLPL standard library.
This module provides networking functions and utilities.
"""

import socket
import urllib.request
import urllib.parse
import urllib.error
import json
import ssl
import http.client
from typing import Dict, Any, Optional, Union
from ...runtime.runtime import Runtime

def register_network_functions(runtime: Runtime) -> None:
    """Register network functions with the runtime."""
    # HTTP operations
    runtime.register_function("http_get", http_get)
    runtime.register_function("http_post", http_post)
    runtime.register_function("http_put", http_put)
    runtime.register_function("http_delete", http_delete)
    runtime.register_function("http_head", http_head)
    runtime.register_function("http_request", http_request)
    
    # URL operations
    runtime.register_function("url_encode", url_encode)
    runtime.register_function("url_decode", url_decode)
    runtime.register_function("url_parse", url_parse)
    runtime.register_function("url_join", url_join)
    
    # Socket operations
    runtime.register_function("socket_create", socket_create)
    runtime.register_function("socket_connect", socket_connect)
    runtime.register_function("socket_send", socket_send)
    runtime.register_function("socket_receive", socket_receive)
    runtime.register_function("socket_close", socket_close)
    
    # DNS operations
    runtime.register_function("dns_lookup", dns_lookup)
    runtime.register_function("dns_reverse_lookup", dns_reverse_lookup)
    
    # JSON operations
    runtime.register_function("json_encode", json_encode)
    runtime.register_function("json_decode", json_decode)

# HTTP operations
def http_get(url, headers=None, timeout=30):
    """Send an HTTP GET request to the specified URL."""
    return http_request("GET", url, None, headers, timeout)

def http_post(url, data=None, headers=None, timeout=30):
    """Send an HTTP POST request to the specified URL."""
    return http_request("POST", url, data, headers, timeout)

def http_put(url, data=None, headers=None, timeout=30):
    """Send an HTTP PUT request to the specified URL."""
    return http_request("PUT", url, data, headers, timeout)

def http_delete(url, headers=None, timeout=30):
    """Send an HTTP DELETE request to the specified URL."""
    return http_request("DELETE", url, None, headers, timeout)

def http_head(url, headers=None, timeout=30):
    """Send an HTTP HEAD request to the specified URL."""
    return http_request("HEAD", url, None, headers, timeout)

def http_request(method, url, data=None, headers=None, timeout=30):
    """Send an HTTP request to the specified URL."""
    try:
        # Prepare the request
        headers = headers or {}
        
        # Convert data to bytes if it's a string or dictionary
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
        elif isinstance(data, str):
            data = data.encode('utf-8')
        
        # Create the request
        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method
        )
        
        # Send the request
        context = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            status_code = response.status
            response_headers = dict(response.getheaders())
            content = response.read().decode('utf-8')
            
            # Try to parse JSON response
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                pass
            
            return {
                'status_code': status_code,
                'headers': response_headers,
                'content': content
            }
    except urllib.error.HTTPError as e:
        return {
            'status_code': e.code,
            'headers': dict(e.headers),
            'error': str(e),
            'content': e.read().decode('utf-8')
        }
    except Exception as e:
        return {
            'status_code': 0,
            'error': str(e),
            'content': None
        }

# URL operations
def url_encode(data):
    """Encode data for use in a URL.

    Accepts a string (percent-encodes it) or a dict (encodes as query string).
    """
    if isinstance(data, str):
        return urllib.parse.quote_plus(data)
    if isinstance(data, dict):
        return urllib.parse.urlencode(data)
    raise TypeError("url_encode() expects a string or dictionary")

def url_decode(query_string):
    """Decode a URL-encoded string or query string.

    If the input contains '=' it is treated as a query string and decoded into
    a dictionary.  Otherwise it is treated as a percent-encoded string and the
    decoded plain string is returned.
    """
    if not isinstance(query_string, str):
        raise TypeError("Expected a string")
    # Plain percent-encoded string (no key=value pairs)
    if '=' not in query_string:
        return urllib.parse.unquote_plus(query_string)
    result = dict(urllib.parse.parse_qsl(query_string))
    if result:
        return result
    # Fallback: plain string decode
    return urllib.parse.unquote_plus(query_string)

def url_parse(url):
    """Parse a URL into its components."""
    if not isinstance(url, str):
        raise TypeError("Expected a string")
    
    parsed = urllib.parse.urlparse(url)
    return {
        'scheme': parsed.scheme,
        'netloc': parsed.netloc,
        'path': parsed.path,
        'params': parsed.params,
        'query': parsed.query,
        'fragment': parsed.fragment,
        'username': parsed.username,
        'password': parsed.password,
        'hostname': parsed.hostname,
        'port': parsed.port
    }

def url_join(base, url):
    """Join a base URL and a possibly relative URL to form an absolute URL."""
    if not isinstance(base, str) or not isinstance(url, str):
        raise TypeError("Expected strings")
    
    return urllib.parse.urljoin(base, url)

# Socket operations
def socket_create(family='inet', type='stream'):
    """Create a new socket."""
    family_map = {
        'inet': socket.AF_INET,
        'inet6': socket.AF_INET6,
        'unix': socket.AF_UNIX
    }
    
    type_map = {
        'stream': socket.SOCK_STREAM,
        'dgram': socket.SOCK_DGRAM
    }
    
    if family not in family_map:
        raise ValueError(f"Invalid socket family: {family}")
    
    if type not in type_map:
        raise ValueError(f"Invalid socket type: {type}")
    
    sock = socket.socket(family_map[family], type_map[type])
    return {
        'socket': sock,
        'family': family,
        'type': type,
        'closed': False
    }

def socket_connect(sock_info, host, port):
    """Connect a socket to a remote host."""
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    
    sock = sock_info['socket']
    
    if sock_info.get('closed', True):
        raise ValueError("Socket is closed")
    
    try:
        sock.connect((host, port))
        return sock_info
    except Exception as e:
        return {
            'error': str(e)
        }

def socket_send(sock_info, data):
    """Send data through a socket."""
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    
    sock = sock_info['socket']
    
    if sock_info.get('closed', True):
        raise ValueError("Socket is closed")
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    try:
        bytes_sent = sock.send(data)
        return bytes_sent
    except Exception as e:
        return {
            'error': str(e)
        }

def socket_receive(sock_info, buffer_size=4096):
    """Receive data from a socket."""
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    
    sock = sock_info['socket']
    
    if sock_info.get('closed', True):
        raise ValueError("Socket is closed")
    
    try:
        data = sock.recv(buffer_size)
        return data.decode('utf-8')
    except Exception as e:
        return {
            'error': str(e)
        }

def socket_close(sock_info):
    """Close a socket."""
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    
    sock = sock_info['socket']
    
    if sock_info.get('closed', True):
        return True
    
    try:
        sock.close()
        sock_info['closed'] = True
        return True
    except Exception as e:
        return {
            'error': str(e)
        }

# DNS operations
def dns_lookup(hostname):
    """Look up the IP address for a hostname."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror as e:
        return {
            'error': str(e)
        }

def dns_reverse_lookup(ip_address):
    """Look up the hostname for an IP address."""
    try:
        return socket.gethostbyaddr(ip_address)[0]
    except socket.herror as e:
        return {
            'error': str(e)
        }

# JSON operations
def json_encode(obj, indent=None):
    """Encode an object as a JSON string."""
    try:
        return json.dumps(obj, indent=indent)
    except (TypeError, ValueError) as e:
        return {
            'error': str(e)
        }

def json_decode(json_str):
    """Decode a JSON string into an object."""
    if not isinstance(json_str, str):
        raise TypeError("Expected a string")
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {
            'error': str(e)
        } 