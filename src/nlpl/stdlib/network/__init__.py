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
    
    # Server socket operations
    runtime.register_function("socket_bind", socket_bind)
    runtime.register_function("socket_listen", socket_listen)
    runtime.register_function("socket_accept", socket_accept)
    runtime.register_function("socket_set_option", socket_set_option)

    # UDP datagram operations
    runtime.register_function("udp_send_to", udp_send_to)
    runtime.register_function("udp_receive_from", udp_receive_from)

    # TLS/SSL operations
    runtime.register_function("tls_create_context", tls_create_context)
    runtime.register_function("tls_wrap_socket", tls_wrap_socket)
    runtime.register_function("tls_connect", tls_connect)
    runtime.register_function("tls_wrap_server_socket", tls_wrap_server_socket)

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


def socket_bind(sock_info, host_or_path, port=None):
    """Bind a socket to an address.

    For TCP/UDP sockets pass *host_or_path* as a host string and *port* as an
    integer.  For Unix-domain sockets pass the socket-file path as
    *host_or_path* and omit *port*.
    """
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    sock = sock_info['socket']
    try:
        if sock_info.get('family') == 'unix' or port is None:
            sock.bind(host_or_path)
        else:
            sock.bind((host_or_path, int(port)))
        sock_info['bound'] = True
        return sock_info
    except Exception as e:
        return {'error': str(e)}


def socket_listen(sock_info, backlog=5):
    """Put the socket into listening mode.

    *backlog* is the maximum number of queued connections (default 5).
    """
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    sock = sock_info['socket']
    try:
        sock.listen(int(backlog))
        sock_info['listening'] = True
        return sock_info
    except Exception as e:
        return {'error': str(e)}


def socket_accept(sock_info):
    """Accept an incoming connection on a listening socket.

    Returns a new socket-info dict for the accepted connection together with
    the remote address as ``{'socket': ..., 'address': (host, port), ...}``.
    """
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    sock = sock_info['socket']
    try:
        conn, addr = sock.accept()
        return {
            'socket': conn,
            'family': sock_info.get('family', 'inet'),
            'type': sock_info.get('type', 'stream'),
            'closed': False,
            'address': addr,
        }
    except Exception as e:
        return {'error': str(e)}


def socket_set_option(sock_info, option, value):
    """Set a socket-level option using ``setsockopt``.

    Supported *option* strings:

    - ``'reuse_address'`` / ``'reuseaddr'`` — ``SO_REUSEADDR`` (value: bool/int)
    - ``'reuse_port'`` / ``'reuseport'``   — ``SO_REUSEPORT`` (value: bool/int)
    - ``'timeout'``                         — sets blocking timeout in seconds
    - ``'non_blocking'``                    — makes socket non-blocking (value: bool)
    - ``'keepalive'``                       — ``SO_KEEPALIVE`` (value: bool/int)
    - ``'nodelay'``                         — ``TCP_NODELAY`` (value: bool/int)
    - ``'broadcast'``                       — ``SO_BROADCAST`` (value: bool/int)
    """
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    sock = sock_info['socket']
    opt = option.lower().replace('-', '_')
    try:
        if opt in ('reuse_address', 'reuseaddr'):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, int(bool(value)))
        elif opt in ('reuse_port', 'reuseport'):
            if hasattr(socket, 'SO_REUSEPORT'):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, int(bool(value)))
        elif opt == 'timeout':
            sock.settimeout(float(value) if value else None)
        elif opt == 'non_blocking':
            sock.setblocking(not bool(value))
        elif opt == 'keepalive':
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, int(bool(value)))
        elif opt == 'nodelay':
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, int(bool(value)))
        elif opt == 'broadcast':
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, int(bool(value)))
        else:
            raise ValueError(f"Unknown socket option: '{option}'")
        return sock_info
    except Exception as e:
        return {'error': str(e)}


# ---------------------------------------------------------------------------
# UDP datagram operations
# ---------------------------------------------------------------------------

def udp_send_to(sock_info, data, host, port):
    """Send a datagram to (host, port) using the given UDP socket.

    Returns the number of bytes sent.
    """
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    if sock_info.get('type') not in ('dgram', None) and sock_info.get('type') != 'dgram':
        pass  # allow caller to pass any socket; sendto works on SOCK_DGRAM
    sock = sock_info['socket']
    if isinstance(data, str):
        data = data.encode('utf-8')
    try:
        return sock.sendto(data, (host, int(port)))
    except Exception as e:
        return {'error': str(e)}


def udp_receive_from(sock_info, buffer_size=4096):
    """Receive a datagram from the socket.

    Returns ``{'data': str, 'address': (host, port)}``.
    """
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    sock = sock_info['socket']
    try:
        raw, addr = sock.recvfrom(int(buffer_size))
        return {
            'data': raw.decode('utf-8', errors='replace'),
            'address': addr,
            'bytes': len(raw),
        }
    except Exception as e:
        return {'error': str(e)}


# ---------------------------------------------------------------------------
# TLS/SSL operations
# ---------------------------------------------------------------------------

def tls_create_context(verify=True, cafile=None, certfile=None, keyfile=None,
                       protocol=None, check_hostname=True):
    """Create an SSL context for use with TLS connections.

    Args:
        verify:          Verify peer certificate (default True).
        cafile:          Path to CA certificate bundle (PEM).  Uses system
                         default CAs when None.
        certfile:        Path to client/server certificate (PEM).
        keyfile:         Path to private key (PEM).  Defaults to *certfile*.
        protocol:        Ignored — always uses TLS 1.2+ (SSLContext default).
        check_hostname:  Enforce hostname verification (default True, only
                         meaningful when *verify* is True).

    Returns a dict holding the ``SSLContext`` under the key ``'context'``.
    """
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT if verify else ssl.PROTOCOL_TLS_SERVER)

        if verify:
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.check_hostname = bool(check_hostname)
            if cafile:
                ctx.load_verify_locations(cafile=cafile)
            else:
                ctx.load_default_certs()
        else:
            ctx.verify_mode = ssl.CERT_NONE
            ctx.check_hostname = False

        if certfile:
            ctx.load_cert_chain(certfile=certfile,
                                keyfile=keyfile or certfile)

        return {
            'context': ctx,
            'verify': verify,
            'cafile': cafile,
            'certfile': certfile,
        }
    except Exception as e:
        return {'error': str(e)}


def tls_wrap_socket(sock_info, context_info, server_hostname=None):
    """Wrap an existing connected socket with TLS (client side).

    Args:
        sock_info:        A socket dict as returned by ``socket_create``.
        context_info:     An SSL-context dict from ``tls_create_context``.
        server_hostname:  Hostname for SNI / certificate verification.

    Returns an updated socket dict whose ``'socket'`` key holds the wrapped
    ``SSLSocket`` so all other socket helpers continue to work.
    """
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        return {'error': "Expected a socket dict from socket_create()"}
    if not isinstance(context_info, dict) or 'context' not in context_info:
        return {'error': "Expected an SSL context dict from tls_create_context()"}
    ctx: ssl.SSLContext = context_info['context']
    sock = sock_info['socket']
    try:
        wrapped = ctx.wrap_socket(sock, server_hostname=server_hostname)
        result = dict(sock_info)
        result['socket'] = wrapped
        result['tls'] = True
        result['server_hostname'] = server_hostname
        result['cipher'] = wrapped.cipher()
        result['tls_version'] = wrapped.version()
        return result
    except Exception as e:
        return {'error': str(e)}


def tls_connect(host, port, cafile=None, certfile=None, keyfile=None, verify=True,
                timeout=30):
    """Open a TLS-secured TCP connection to *host*:*port*.

    Convenience wrapper that creates a socket, connects, and wraps with TLS in
    one call.

    Returns a socket dict (same shape as ``socket_create`` + TLS metadata) on
    success, or ``{'error': str}`` on failure.
    """
    try:
        ctx_info = tls_create_context(verify=verify, cafile=cafile,
                                      certfile=certfile, keyfile=keyfile,
                                      check_hostname=verify)
        if 'error' in ctx_info:
            return ctx_info

        raw_sock = socket.create_connection((host, int(port)), timeout=timeout)
        sock_info = {
            'socket': raw_sock,
            'family': 'inet',
            'type': 'stream',
            'closed': False,
        }
        wrapped = tls_wrap_socket(sock_info, ctx_info, server_hostname=host)
        return wrapped
    except Exception as e:
        return {'error': str(e)}


def tls_wrap_server_socket(sock_info, certfile, keyfile, cafile=None,
                           require_client_cert=False):
    """Wrap a bound/listening socket with TLS for use as a TLS server.

    Args:
        sock_info:            Server socket dict (already bound + listening).
        certfile:             Path to the server certificate (PEM).
        keyfile:              Path to the server private key (PEM).
        cafile:               Path to CA bundle for client-cert verification.
        require_client_cert:  Require and verify client certificates when True.

    Returns an updated socket dict.  Call ``socket_accept`` on the returned
    dict to get TLS-enabled client connections.
    """
    if not isinstance(sock_info, dict) or 'socket' not in sock_info:
        raise TypeError("Expected a socket object")
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)

        if require_client_cert and cafile:
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(cafile=cafile)
        elif cafile:
            ctx.load_verify_locations(cafile=cafile)

        # Wrap the raw server socket so accept() yields TLS connections
        wrapped_server = ctx.wrap_socket(sock_info['socket'], server_side=True)
        result = dict(sock_info)
        result['socket'] = wrapped_server
        result['tls'] = True
        result['certfile'] = certfile
        return result
    except Exception as e:
        return {'error': str(e)}


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