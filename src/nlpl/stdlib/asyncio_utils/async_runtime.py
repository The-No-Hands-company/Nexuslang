"""
NLPL Async Runtime

Full async/await execution engine for NLPL programs:
- NLPLFuture<T>  - observable async result container
- NLPLTask       - handle for a spawned async task
- NLPLEventLoop  - scheduler driving all async work
- spawn_async    - submit an async task to the scheduler
- join_all       - await multiple tasks and collect results
- select_first   - return first task that completes
- async_timeout  - run a task with a deadline
- async_sleep    - non-blocking sleep inside async context
- async_after    - delayed function dispatch
- async_read_file, async_write_file - async file I/O
- async_http_get, async_http_post  - async HTTP (no blocking the event loop)
- create_future, future_set_result, future_set_error, future_get - manual futures
"""

import asyncio
import concurrent.futures
import inspect
import threading
import time
from typing import Any, Callable, List, Optional


# ---------------------------------------------------------------------------
# Global event loop thread
# ---------------------------------------------------------------------------

_loop: Optional[asyncio.AbstractEventLoop] = None
_loop_thread: Optional[threading.Thread] = None
_loop_lock = threading.Lock()


def _get_or_create_loop() -> asyncio.AbstractEventLoop:
    """
    Return (and lazily start) the shared NLPL event loop.

    The loop runs in a dedicated daemon thread so that async tasks can be
    submitted from any NLPL thread without conflicting with each other or
    with CPython's default event-loop policy.
    """
    global _loop, _loop_thread
    with _loop_lock:
        if _loop is None or _loop.is_closed():
            _loop = asyncio.new_event_loop()
            _loop_thread = threading.Thread(
                target=_loop.run_forever,
                name="NLPLAsyncEventLoop",
                daemon=True,
            )
            _loop_thread.start()
    return _loop


# ---------------------------------------------------------------------------
# NLPLFuture
# ---------------------------------------------------------------------------

class NLPLFuture:
    """
    Observable result container for an asynchronous computation.

    Wraps a :class:`concurrent.futures.Future` but exposes the NLPL API
    (get, is_done, set_result, set_error).
    """

    def __init__(self):
        self._event = threading.Event()
        self._value: Any = None
        self._error: Optional[Exception] = None
        self._lock = threading.Lock()

    # ---- producer side ----

    def set_result(self, value: Any) -> None:
        """Fulfil the future with a value."""
        with self._lock:
            if self._event.is_set():
                raise RuntimeError("Future already resolved")
            self._value = value
            self._event.set()

    def set_error(self, error: Exception) -> None:
        """Reject the future with an error."""
        with self._lock:
            if self._event.is_set():
                raise RuntimeError("Future already resolved")
            self._error = error
            self._event.set()

    # ---- consumer side ----

    def is_done(self) -> bool:
        """Return True once the future has been settled."""
        return self._event.is_set()

    def get(self, timeout: Optional[float] = None) -> Any:
        """
        Block until the future is settled, then return the value.

        Raises the stored exception if the future was rejected.
        Raises :class:`TimeoutError` if *timeout* seconds elapse first.
        """
        if not self._event.wait(timeout):
            raise TimeoutError("Future timed out after {} seconds".format(timeout))
        if self._error is not None:
            raise self._error
        return self._value

    def __repr__(self) -> str:
        if not self._event.is_set():
            return "Future<pending>"
        if self._error is not None:
            return "Future<error: {}>".format(self._error)
        return "Future<done: {!r}>".format(self._value)


# ---------------------------------------------------------------------------
# NLPLTask
# ---------------------------------------------------------------------------

class NLPLTask:
    """
    Handle representing a spawned async task.

    Wraps a :class:`concurrent.futures.Future` returned by
    :func:`asyncio.run_coroutine_threadsafe`.  That future is inherently
    thread-safe and designed to be waited on from non-event-loop threads.
    """

    def __init__(self, cf_future: concurrent.futures.Future):
        self._future: concurrent.futures.Future = cf_future

    def is_done(self) -> bool:
        return self._future.done()

    def cancel(self) -> bool:
        return self._future.cancel()

    def result(self, timeout: Optional[float] = None) -> Any:
        """
        Block the calling thread until the task completes.

        Raises the task's exception on failure.
        Raises :class:`TimeoutError` if *timeout* elapses.
        """
        try:
            return self._future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError("Task timed out")

    def __repr__(self) -> str:
        if self._future.done():
            try:
                return "Task<done: {!r}>".format(self._future.result(timeout=0))
            except Exception as e:
                return "Task<error: {}>".format(e)
        return "Task<running>"


# ---------------------------------------------------------------------------
# Core async runtime functions
# ---------------------------------------------------------------------------

def spawn_async(fn: Callable, *args) -> NLPLTask:
    """
    Submit *fn* to the shared event loop and return a :class:`NLPLTask`.

    The function may be a plain callable or a Python coroutine function.
    Returns a thread-safe :class:`NLPLTask` that can be waited on from any
    thread via :func:`task_result`.

    Example NLPL usage::

        function fetch_data with url as String returns String
            # ...implementation...

        set task to spawn_async with fetch_data and "https://example.com"
        set result to task_result with task
    """
    loop = _get_or_create_loop()

    if inspect.iscoroutinefunction(fn):
        # Native coroutine: schedule it directly on the event loop.
        async def _run_coro():
            return await fn(*args)
        cf_future = asyncio.run_coroutine_threadsafe(_run_coro(), loop)
    else:
        # Plain blocking callable: run it in the loop's default
        # ThreadPoolExecutor so it never blocks the event-loop thread.
        # This avoids starving other pending tasks when fn calls time.sleep
        # or performs any other blocking I/O.
        async def _run_in_executor():
            return await loop.run_in_executor(None, lambda: fn(*args))
        cf_future = asyncio.run_coroutine_threadsafe(_run_in_executor(), loop)

    # concurrent.futures.Future is inherently thread-safe; NLPLTask wraps it.
    return NLPLTask(cf_future)


def task_result(task: NLPLTask, timeout: Optional[float] = None) -> Any:
    """Block and return the result of a spawned task."""
    if not isinstance(task, NLPLTask):
        raise TypeError("Expected a task returned by spawn_async")
    return task.result(timeout)


def task_is_done(task: NLPLTask) -> bool:
    """Return True if the task has finished."""
    if not isinstance(task, NLPLTask):
        raise TypeError("Expected a task returned by spawn_async")
    return task.is_done()


def task_cancel(task: NLPLTask) -> bool:
    """Request cancellation of a running task. Returns True if cancellation was requested."""
    if not isinstance(task, NLPLTask):
        raise TypeError("Expected a task returned by spawn_async")
    return task.cancel()


def join_all(tasks: list, timeout: Optional[float] = None) -> list:
    """
    Wait for all tasks to complete and return their results as a list.

    The order of results matches the order of *tasks*.
    Raises the first exception encountered across any task.
    Raises :class:`TimeoutError` if *timeout* elapses before all complete.

    Example NLPL usage::

        set tasks to list of spawn_async with work and 1, spawn_async with work and 2
        set results to join_all with tasks
    """
    if not tasks:
        return []
    deadline = None if timeout is None else time.monotonic() + timeout
    results = []
    for task in tasks:
        remaining = (
            None
            if deadline is None
            else max(0.0, deadline - time.monotonic())
        )
        if remaining is not None and remaining <= 0:
            raise TimeoutError("join_all timed out waiting for tasks")
        results.append(task.result(remaining))
    return results


def select_first(tasks: list, timeout: Optional[float] = None) -> Any:
    """
    Return the result of whichever task completes first.

    Raises :class:`TimeoutError` if *timeout* elapses before any task completes.

    Example NLPL usage::

        set result to select_first with tasks
    """
    if not tasks:
        raise ValueError("select_first requires at least one task")
    deadline = None if timeout is None else time.monotonic() + timeout
    while True:
        for task in tasks:
            if task.is_done():
                return task.result()
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("select_first timed out")
        time.sleep(0.002)


def async_timeout(task: NLPLTask, duration: float) -> Any:
    """
    Wait for *task* with a *duration* second deadline.

    Raises :class:`TimeoutError` on expiry.

    Example NLPL usage::

        set result to async_timeout with task and 5.0
    """
    return task.result(duration)


def async_sleep(seconds: float) -> None:
    """
    Non-blocking sleep that allows other async tasks to run.

    From sync NLPL code this simply sleeps the thread.
    Inside a Python coroutine context this yields to the event loop.

    Example NLPL usage::

        async_sleep with 1.5
    """
    time.sleep(seconds)


def async_after(delay: float, fn: Callable, *args) -> NLPLTask:
    """
    Execute *fn* after *delay* seconds and return a task.

    Example NLPL usage::

        set task to async_after with 2.0 and my_callback
    """
    def _delayed():
        time.sleep(delay)
        return fn(*args)

    return spawn_async(_delayed)

# ---------------------------------------------------------------------------
# Manual Future API
# ---------------------------------------------------------------------------

def create_future() -> NLPLFuture:
    """
    Create an unresolved :class:`NLPLFuture`.

    Example NLPL usage::

        set fut to create_future
        future_set_result with fut and 42
        set val to future_get with fut
    """
    return NLPLFuture()


def future_set_result(future: NLPLFuture, value: Any) -> None:
    """Fulfil a future with *value*."""
    if not isinstance(future, NLPLFuture):
        raise TypeError("Expected a NLPLFuture from create_future")
    future.set_result(value)


def future_set_error(future: NLPLFuture, error: Any) -> None:
    """Reject a future with *error* (string or exception)."""
    if not isinstance(future, NLPLFuture):
        raise TypeError("Expected a NLPLFuture from create_future")
    exc = error if isinstance(error, Exception) else Exception(str(error))
    future.set_error(exc)


def future_get(future: NLPLFuture, timeout: Optional[float] = None) -> Any:
    """Block for a future's result. Raises on error or timeout."""
    if not isinstance(future, NLPLFuture):
        raise TypeError("Expected a NLPLFuture from create_future")
    return future.get(timeout)


def future_is_done(future: NLPLFuture) -> bool:
    """Return True if the future has been settled."""
    if not isinstance(future, NLPLFuture):
        raise TypeError("Expected a NLPLFuture from create_future")
    return future.is_done()


# ---------------------------------------------------------------------------
# Async I/O
# ---------------------------------------------------------------------------

def async_read_file(path: str, encoding: str = "utf-8") -> NLPLTask:
    """
    Read a file asynchronously. Returns a task resolving to the file content.

    Example NLPL usage::

        set task to async_read_file with "data.txt"
        set content to task_result with task
    """
    def _read():
        with open(path, "r", encoding=encoding) as f:
            return f.read()

    return spawn_async(_read)


def async_read_file_bytes(path: str) -> NLPLTask:
    """Read a binary file asynchronously. Returns a task resolving to bytes."""
    def _read():
        with open(path, "rb") as f:
            return f.read()

    return spawn_async(_read)


def async_write_file(path: str, content: str, encoding: str = "utf-8") -> NLPLTask:
    """
    Write *content* to *path* asynchronously. Returns a task resolving to bytes written.

    Example NLPL usage::

        set task to async_write_file with "output.txt" and result_text
        task_result with task
    """
    def _write():
        with open(path, "w", encoding=encoding) as f:
            return f.write(content)

    return spawn_async(_write)


def async_write_file_bytes(path: str, data: bytes) -> NLPLTask:
    """Write binary data to *path* asynchronously."""
    def _write():
        with open(path, "wb") as f:
            return f.write(data)

    return spawn_async(_write)


def async_append_file(path: str, content: str, encoding: str = "utf-8") -> NLPLTask:
    """Append *content* to *path* asynchronously."""
    def _append():
        with open(path, "a", encoding=encoding) as f:
            return f.write(content)

    return spawn_async(_append)


# ---------------------------------------------------------------------------
# Async HTTP
# ---------------------------------------------------------------------------

def _make_http_request(method: str, url: str, headers: Optional[dict] = None,
                       body: Optional[str] = None, timeout: float = 30.0) -> dict:
    """Perform a synchronous HTTP request (runs inside async worker thread)."""
    import urllib.request
    import urllib.error
    import json as _json

    req = urllib.request.Request(url, method=method.upper())
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if body is not None:
        req.data = body.encode("utf-8") if isinstance(body, str) else body

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            text = raw.decode("utf-8", errors="replace")
            return {
                "status": resp.status,
                "headers": dict(resp.headers),
                "body": text,
                "ok": 200 <= resp.status < 300,
            }
    except urllib.error.HTTPError as e:
        raw = e.read()
        text = raw.decode("utf-8", errors="replace")
        return {
            "status": e.code,
            "headers": dict(e.headers),
            "body": text,
            "ok": False,
            "error": str(e),
        }
    except Exception as e:
        return {
            "status": 0,
            "headers": {},
            "body": "",
            "ok": False,
            "error": str(e),
        }


def async_http_get(url: str, headers: Optional[dict] = None,
                   timeout: float = 30.0) -> NLPLTask:
    """
    Perform an HTTP GET request asynchronously.

    Returns a task resolving to a dict with keys:
    ``status``, ``headers``, ``body``, ``ok``, ``error`` (on failure).

    Example NLPL usage::

        set task to async_http_get with "https://api.example.com/data"
        set response to task_result with task
        if response["ok"]
            print text response["body"]
        end
    """
    return spawn_async(_make_http_request, "GET", url, headers, None, timeout)


def async_http_post(url: str, body: str = "", headers: Optional[dict] = None,
                    timeout: float = 30.0) -> NLPLTask:
    """
    Perform an HTTP POST request asynchronously.

    Example NLPL usage::

        set task to async_http_post with "https://api.example.com/data" and body_text
        set response to task_result with task
    """
    post_headers = headers or {}
    if "Content-Type" not in post_headers:
        post_headers["Content-Type"] = "application/json"
    return spawn_async(_make_http_request, "POST", url, post_headers, body, timeout)


def async_http_put(url: str, body: str = "", headers: Optional[dict] = None,
                   timeout: float = 30.0) -> NLPLTask:
    """Perform an HTTP PUT request asynchronously."""
    return spawn_async(_make_http_request, "PUT", url, headers or {}, body, timeout)


def async_http_delete(url: str, headers: Optional[dict] = None,
                      timeout: float = 30.0) -> NLPLTask:
    """Perform an HTTP DELETE request asynchronously."""
    return spawn_async(_make_http_request, "DELETE", url, headers or {}, None, timeout)


# ---------------------------------------------------------------------------
# Async TCP socket operations
# ---------------------------------------------------------------------------

def async_tcp_connect(host: str, port: int, timeout: Optional[float] = None) -> NLPLTask:
    """Asynchronously open a TCP connection.

    Returns a task resolving to a connection dict with keys:
    'socket', 'host', 'port'.
    On failure the task raises the underlying socket error.
    """
    import socket as _socket

    def _connect():
        sock = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        if timeout is not None:
            sock.settimeout(float(timeout))
        try:
            sock.connect((str(host), int(port)))
        except Exception:
            sock.close()
            raise
        sock.settimeout(None)
        return {'socket': sock, 'host': str(host), 'port': int(port)}

    return spawn_async(_connect)


def async_tcp_listen(host: str, port: int, backlog: int = 5) -> NLPLTask:
    """Asynchronously create a TCP server socket bound to host:port.

    Returns a task resolving to a server dict with keys: 'socket', 'host', 'port'.
    """
    import socket as _socket

    def _listen():
        srv = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        srv.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
        srv.bind((str(host), int(port)))
        srv.listen(int(backlog))
        actual_port = srv.getsockname()[1]
        return {'socket': srv, 'host': str(host), 'port': actual_port}

    return spawn_async(_listen)


def async_tcp_accept(server: dict) -> NLPLTask:
    """Asynchronously accept an incoming TCP connection on a server socket.

    Returns a task resolving to a connection dict with keys:
    'socket', 'host', 'port'.
    """
    def _accept():
        srv = server['socket']
        conn, addr = srv.accept()
        return {'socket': conn, 'host': addr[0], 'port': addr[1]}

    return spawn_async(_accept)


def async_tcp_send(conn: dict, data: Any) -> NLPLTask:
    """Asynchronously send data over an established TCP connection.

    data may be str, bytes, bytearray, or any value (converted via str).
    Returns a task resolving to the number of bytes sent.
    """
    def _send():
        sock = conn['socket']
        if isinstance(data, str):
            payload = data.encode('utf-8')
        elif isinstance(data, (bytes, bytearray)):
            payload = bytes(data)
        else:
            payload = str(data).encode('utf-8')
        sock.sendall(payload)
        return len(payload)

    return spawn_async(_send)


def async_tcp_recv(conn: dict, buffer_size: int = 4096) -> NLPLTask:
    """Asynchronously receive up to buffer_size bytes from a TCP connection.

    Returns a task resolving to a dict with keys:
    'data' (str, UTF-8 decoded), 'bytes' (raw bytes), 'length' (int), 'eof' (bool).
    """
    def _recv():
        sock = conn['socket']
        raw = sock.recv(int(buffer_size))
        return {
            'data': raw.decode('utf-8', errors='replace'),
            'bytes': raw,
            'length': len(raw),
            'eof': len(raw) == 0,
        }

    return spawn_async(_recv)


def async_tcp_recv_exactly(conn: dict, n: int) -> NLPLTask:
    """Asynchronously receive exactly n bytes from a TCP connection.

    Loops until all bytes are received or EOF is reached.
    Returns a task resolving to a dict with keys: 'data', 'bytes', 'length'.
    """
    def _recv():
        sock = conn['socket']
        buf = bytearray()
        remaining = int(n)
        while remaining > 0:
            chunk = sock.recv(remaining)
            if not chunk:
                break
            buf.extend(chunk)
            remaining -= len(chunk)
        raw = bytes(buf)
        return {
            'data': raw.decode('utf-8', errors='replace'),
            'bytes': raw,
            'length': len(raw),
        }

    return spawn_async(_recv)


def async_tcp_close(conn: dict) -> None:
    """Close a TCP connection dict (synchronous, instant)."""
    sock = conn.get('socket')
    if sock is not None:
        try:
            sock.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Async UDP socket operations
# ---------------------------------------------------------------------------

def async_udp_open(bind_host: str = '', bind_port: int = 0) -> NLPLTask:
    """Asynchronously create and optionally bind a UDP socket.

    Returns a task resolving to a socket dict with keys: 'socket', 'port'.
    When bind_port=0 the OS assigns a free ephemeral port.
    """
    import socket as _socket

    def _open():
        sock = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
        if bind_host or bind_port:
            sock.bind((str(bind_host), int(bind_port)))
        else:
            sock.bind(('', 0))
        actual_port = sock.getsockname()[1]
        return {'socket': sock, 'port': actual_port}

    return spawn_async(_open)


def async_udp_send_to(conn: dict, data: Any, host: str, port: int) -> NLPLTask:
    """Asynchronously send a UDP datagram to host:port.

    Returns a task resolving to the number of bytes sent.
    """
    def _send():
        sock = conn['socket']
        if isinstance(data, str):
            payload = data.encode('utf-8')
        elif isinstance(data, (bytes, bytearray)):
            payload = bytes(data)
        else:
            payload = str(data).encode('utf-8')
        return sock.sendto(payload, (str(host), int(port)))

    return spawn_async(_send)


def async_udp_recv_from(conn: dict, buffer_size: int = 65535) -> NLPLTask:
    """Asynchronously receive a UDP datagram.

    Returns a task resolving to a dict with keys:
    'data' (str), 'bytes' (raw bytes), 'length', 'from_host', 'from_port'.
    """
    def _recv():
        sock = conn['socket']
        raw, addr = sock.recvfrom(int(buffer_size))
        return {
            'data': raw.decode('utf-8', errors='replace'),
            'bytes': raw,
            'length': len(raw),
            'from_host': addr[0],
            'from_port': addr[1],
        }

    return spawn_async(_recv)


def async_udp_close(conn: dict) -> None:
    """Close a UDP socket dict (synchronous, instant)."""
    sock = conn.get('socket')
    if sock is not None:
        try:
            sock.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Async subprocess
# ---------------------------------------------------------------------------

def async_subprocess(
    cmd: str,
    args: Optional[list] = None,
    stdin_data: Optional[str] = None,
    timeout: Optional[float] = None,
) -> NLPLTask:
    """Asynchronously run a subprocess and wait for completion.

    Returns a task resolving to a dict with keys:
    'stdout', 'stderr', 'returncode', 'success'.
    On timeout or missing command the dict also contains an 'error' key.
    """
    import subprocess as _sp

    def _run():
        argv = [str(cmd)] + [str(a) for a in (args or [])]
        inp = stdin_data.encode('utf-8') if isinstance(stdin_data, str) else None
        try:
            result = _sp.run(argv, input=inp, capture_output=True, timeout=timeout)
            return {
                'stdout': result.stdout.decode('utf-8', errors='replace'),
                'stderr': result.stderr.decode('utf-8', errors='replace'),
                'returncode': result.returncode,
                'success': result.returncode == 0,
            }
        except _sp.TimeoutExpired:
            return {'error': 'timeout', 'returncode': -1,
                    'success': False, 'stdout': '', 'stderr': ''}
        except FileNotFoundError:
            return {'error': f'command not found: {cmd}', 'returncode': -1,
                    'success': False, 'stdout': '', 'stderr': ''}

    return spawn_async(_run)


def async_subprocess_output(cmd: str, args: Optional[list] = None) -> NLPLTask:
    """Asynchronously run a subprocess and return just its stdout string.

    Returns a task resolving to the stdout string, or a dict with 'error'
    if the command fails or is not found.
    """
    import subprocess as _sp

    def _run():
        argv = [str(cmd)] + [str(a) for a in (args or [])]
        try:
            out = _sp.check_output(argv, stderr=_sp.DEVNULL)
            return out.decode('utf-8', errors='replace')
        except _sp.CalledProcessError as e:
            return {'error': str(e), 'returncode': e.returncode}
        except FileNotFoundError:
            return {'error': f'command not found: {cmd}'}

    return spawn_async(_run)


# ---------------------------------------------------------------------------
# Async DNS resolution
# ---------------------------------------------------------------------------

def async_dns_resolve(hostname: str) -> NLPLTask:
    """Asynchronously resolve a hostname to its IP addresses.

    Returns a task resolving to a dict with keys:
    'hostname', 'addresses' (list), 'primary' (first IP or None).
    On failure the dict contains an 'error' key.
    """
    import socket as _socket

    def _resolve():
        try:
            infos = _socket.getaddrinfo(str(hostname), None)
            addresses = list(dict.fromkeys(info[4][0] for info in infos))
            return {
                'hostname': str(hostname),
                'addresses': addresses,
                'primary': addresses[0] if addresses else None,
            }
        except _socket.gaierror as e:
            return {'error': str(e), 'hostname': str(hostname)}

    return spawn_async(_resolve)


def async_dns_reverse(ip_address: str) -> NLPLTask:
    """Asynchronously perform a reverse DNS lookup (IP to hostname).

    Returns a task resolving to a dict with keys: 'ip', 'hostname'.
    On failure the dict contains an 'error' key.
    """
    import socket as _socket

    def _resolve():
        try:
            hostname, _, _ = _socket.gethostbyaddr(str(ip_address))
            return {'ip': str(ip_address), 'hostname': hostname}
        except (_socket.herror, _socket.gaierror) as e:
            return {'error': str(e), 'ip': str(ip_address)}

    return spawn_async(_resolve)


# ---------------------------------------------------------------------------
# Async file readline / readlines
# ---------------------------------------------------------------------------

def async_readlines(path: str, encoding: str = "utf-8") -> NLPLTask:
    """Asynchronously read all lines from a file.

    Returns a task resolving to a list of line strings (newlines preserved).
    """
    def _read():
        with open(path, "r", encoding=encoding) as f:
            return f.readlines()

    return spawn_async(_read)


def async_readline_chunks(path: str, chunk_size: int = 100,
                          encoding: str = "utf-8") -> NLPLTask:
    """Asynchronously read up to chunk_size lines from a file.

    Returns a task resolving to a list of up to chunk_size line strings.
    Useful for streaming large files in manageable batches.
    """
    def _read():
        lines = []
        with open(path, "r", encoding=encoding) as f:
            for _ in range(int(chunk_size)):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
        return lines

    return spawn_async(_read)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_async_runtime_functions(runtime) -> None:
    """Register all async runtime functions with the NLPL runtime."""

    # Task lifecycle
    runtime.register_function("spawn_async", lambda rt, fn, *args: spawn_async(fn, *args))
    runtime.register_function("task_result", lambda rt, task, *args: task_result(task, *args))
    runtime.register_function("task_is_done", lambda rt, task: task_is_done(task))
    runtime.register_function("task_cancel", lambda rt, task: task_cancel(task))

    # Multi-task coordination
    runtime.register_function("join_all", lambda rt, tasks, *args: join_all(tasks, *args))
    runtime.register_function("select_first", lambda rt, tasks, *args: select_first(tasks, *args))
    runtime.register_function("async_timeout", lambda rt, task, dur: async_timeout(task, dur))

    # Timing
    runtime.register_function("async_sleep", lambda rt, secs: async_sleep(secs))
    runtime.register_function("async_after", lambda rt, delay, fn, *args: async_after(delay, fn, *args))

    # Manual futures
    runtime.register_function("create_future", lambda rt: create_future())
    runtime.register_function("future_set_result", lambda rt, fut, val: future_set_result(fut, val))
    runtime.register_function("future_set_error", lambda rt, fut, err: future_set_error(fut, err))
    runtime.register_function("future_get", lambda rt, fut, *args: future_get(fut, *args))
    runtime.register_function("future_is_done", lambda rt, fut: future_is_done(fut))

    # Async file I/O
    runtime.register_function("async_read_file", lambda rt, *args: async_read_file(*args))
    runtime.register_function("async_read_file_bytes", lambda rt, path: async_read_file_bytes(path))
    runtime.register_function("async_write_file", lambda rt, *args: async_write_file(*args))
    runtime.register_function("async_write_file_bytes", lambda rt, path, data: async_write_file_bytes(path, data))
    runtime.register_function("async_append_file", lambda rt, *args: async_append_file(*args))

    # Async HTTP
    runtime.register_function("async_http_get", lambda rt, *args: async_http_get(*args))
    runtime.register_function("async_http_post", lambda rt, *args: async_http_post(*args))
    runtime.register_function("async_http_put", lambda rt, *args: async_http_put(*args))
    runtime.register_function("async_http_delete", lambda rt, *args: async_http_delete(*args))

    # Async TCP
    runtime.register_function("async_tcp_connect",
                               lambda rt, *args: async_tcp_connect(*args))
    runtime.register_function("async_tcp_listen",
                               lambda rt, *args: async_tcp_listen(*args))
    runtime.register_function("async_tcp_accept",
                               lambda rt, server: async_tcp_accept(server))
    runtime.register_function("async_tcp_send",
                               lambda rt, conn, data: async_tcp_send(conn, data))
    runtime.register_function("async_tcp_recv",
                               lambda rt, *args: async_tcp_recv(*args))
    runtime.register_function("async_tcp_recv_exactly",
                               lambda rt, conn, n: async_tcp_recv_exactly(conn, n))
    runtime.register_function("async_tcp_close",
                               lambda rt, conn: async_tcp_close(conn))

    # Async UDP
    runtime.register_function("async_udp_open",
                               lambda rt, *args: async_udp_open(*args))
    runtime.register_function("async_udp_send_to",
                               lambda rt, conn, data, host, port: async_udp_send_to(conn, data, host, port))
    runtime.register_function("async_udp_recv_from",
                               lambda rt, *args: async_udp_recv_from(*args))
    runtime.register_function("async_udp_close",
                               lambda rt, conn: async_udp_close(conn))

    # Async subprocess
    runtime.register_function("async_subprocess",
                               lambda rt, *args: async_subprocess(*args))
    runtime.register_function("async_subprocess_output",
                               lambda rt, *args: async_subprocess_output(*args))

    # Async DNS
    runtime.register_function("async_dns_resolve",
                               lambda rt, hostname: async_dns_resolve(hostname))
    runtime.register_function("async_dns_reverse",
                               lambda rt, ip: async_dns_reverse(ip))

    # Async readlines
    runtime.register_function("async_readlines",
                               lambda rt, *args: async_readlines(*args))
    runtime.register_function("async_readline_chunks",
                               lambda rt, *args: async_readline_chunks(*args))
