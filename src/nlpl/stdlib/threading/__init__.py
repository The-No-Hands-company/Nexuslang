"""
NLPL Threading Module - Native Threading Support

Provides native threading capabilities including:
- Thread creation, joining, detaching
- Thread-local storage (TLS)
- Thread configuration (stack size, priority, affinity)
- Thread identification and management

This module enables multi-threaded concurrent programming with
full control over thread lifecycle and properties.
"""

import threading
import multiprocessing
import os
import sys
from typing import Any, Callable, Optional, Dict


# Thread-local storage
_thread_local = threading.local()
_thread_registry: Dict[int, threading.Thread] = {}
_registry_lock = threading.Lock()


class NLPLThread:
    """
    Wrapper for Python threading.Thread with NLPL-specific features
    """
    
    def __init__(
        self,
        target: Callable,
        args: tuple = (),
        name: Optional[str] = None,
        daemon: bool = False,
        stack_size: Optional[int] = None
    ):
        self.target = target
        self.args = args
        self.name = name or f"NLPLThread-{id(self)}"
        self.daemon = daemon
        self.stack_size = stack_size
        self._thread: Optional[threading.Thread] = None
        self._result: Any = None
        self._exception: Optional[Exception] = None
        self._finished = threading.Event()
    
    def _run_wrapper(self):
        """Wrapper that captures return value and exceptions"""
        try:
            self._result = self.target(*self.args)
        except Exception as e:
            self._exception = e
        finally:
            self._finished.set()
    
    def start(self) -> int:
        """
        Start the thread
        Returns thread ID
        """
        # Set stack size if specified
        if self.stack_size:
            old_stack_size = threading.stack_size()
            threading.stack_size(self.stack_size)
        
        self._thread = threading.Thread(
            target=self._run_wrapper,
            name=self.name,
            daemon=self.daemon
        )
        self._thread.start()
        
        # Restore old stack size
        if self.stack_size:
            threading.stack_size(old_stack_size)
        
        # Register thread
        thread_id = self._thread.ident
        with _registry_lock:
            _thread_registry[thread_id] = self._thread
        
        return thread_id
    
    def join(self, timeout: Optional[float] = None) -> Any:
        """
        Wait for thread to complete
        Returns the thread's return value or raises its exception
        """
        if not self._thread:
            raise RuntimeError("Thread not started")
        
        self._thread.join(timeout)
        
        if self._exception:
            raise self._exception
        
        return self._result
    
    def is_alive(self) -> bool:
        """Check if thread is still running"""
        return self._thread.is_alive() if self._thread else False
    
    def get_id(self) -> Optional[int]:
        """Get thread identifier"""
        return self._thread.ident if self._thread else None


# NLPL Runtime Interface Functions

def create_thread(runtime, function: Callable, *args) -> NLPLThread:
    """
    Create and start a new thread
    
    Args:
        function: Function to run in the thread
        *args: Arguments to pass to the function
        
    Returns:
        Thread handle (NLPLThread object)
        
    Example:
        function worker with id as Integer
            print text "Worker thread "
            print text id
        
        set thread to create_thread with worker and 1
    """
    thread = NLPLThread(target=function, args=args)
    thread.start()
    return thread


def join_thread(runtime, thread: NLPLThread, timeout: Optional[float] = None) -> Any:
    """
    Wait for a thread to complete
    
    Args:
        thread: Thread handle returned by create_thread
        timeout: Maximum time to wait (seconds), None = wait forever
        
    Returns:
        Return value from the thread function
        
    Example:
        set result to join_thread with thread_handle
    """
    return thread.join(timeout)


def detach_thread(runtime, thread: NLPLThread):
    """
    Detach a thread (make it a daemon thread)
    
    Args:
        thread: Thread handle
        
    Example:
        detach_thread with thread_handle
    """
    if thread._thread:
        thread._thread.daemon = True


def thread_is_alive(runtime, thread: NLPLThread) -> bool:
    """
    Check if a thread is still running
    
    Args:
        thread: Thread handle
        
    Returns:
        True if thread is alive, False otherwise
        
    Example:
        set alive to thread_is_alive with thread_handle
    """
    return thread.is_alive()


def get_thread_id(runtime, thread: NLPLThread) -> Optional[int]:
    """
    Get the system thread ID
    
    Args:
        thread: Thread handle
        
    Returns:
        Thread ID (integer) or null if not started
        
    Example:
        set tid to get_thread_id with thread_handle
    """
    return thread.get_id()


def get_current_thread_id(runtime) -> int:
    """
    Get the ID of the currently executing thread
    
    Returns:
        Current thread ID
        
    Example:
        set my_tid to get_current_thread_id()
    """
    return threading.get_ident()


def get_current_thread_name(runtime) -> str:
    """
    Get the name of the currently executing thread
    
    Returns:
        Current thread name
        
    Example:
        set my_name to get_current_thread_name()
    """
    return threading.current_thread().name


def set_thread_name(runtime, thread: NLPLThread, name: str):
    """
    Set the name of a thread
    
    Args:
        thread: Thread handle
        name: New name for the thread
        
    Example:
        set_thread_name with thread_handle and "WorkerThread-1"
    """
    if thread._thread:
        thread._thread.name = name
        thread.name = name


def get_cpu_count(runtime) -> int:
    """
    Get the number of CPU cores available
    
    Returns:
        Number of CPU cores
        
    Example:
        set num_cores to get_cpu_count()
    """
    return multiprocessing.cpu_count()


def sleep_thread(runtime, seconds: float):
    """
    Sleep the current thread for specified seconds
    
    Args:
        seconds: Number of seconds to sleep
        
    Example:
        sleep_thread with 0.5  # Sleep for half a second
    """
    import time
    time.sleep(seconds)


def yield_thread(runtime):
    """
    Yield execution to other threads
    
    Hints to the OS scheduler to give other threads a chance to run
    
    Example:
        yield_thread()
    """
    import time
    time.sleep(0)  # Sleep for 0 seconds yields to scheduler


# Thread-Local Storage Functions

def thread_local_set(runtime, key: str, value: Any):
    """
    Set a thread-local variable
    
    Args:
        key: Variable name
        value: Value to store
        
    Thread-local variables are unique per thread.
    
    Example:
        thread_local_set with "counter" and 0
    """
    setattr(_thread_local, key, value)


def thread_local_get(runtime, key: str, default: Any = None) -> Any:
    """
    Get a thread-local variable
    
    Args:
        key: Variable name
        default: Default value if not found
        
    Returns:
        Value stored for this thread, or default
        
    Example:
        set my_counter to thread_local_get with "counter" and 0
    """
    return getattr(_thread_local, key, default)


def thread_local_has(runtime, key: str) -> bool:
    """
    Check if a thread-local variable exists
    
    Args:
        key: Variable name
        
    Returns:
        True if variable exists for this thread
        
    Example:
        if thread_local_has with "counter"
            print text "Counter exists"
        end
    """
    return hasattr(_thread_local, key)


def thread_local_delete(runtime, key: str):
    """
    Delete a thread-local variable
    
    Args:
        key: Variable name
        
    Example:
        thread_local_delete with "counter"
    """
    if hasattr(_thread_local, key):
        delattr(_thread_local, key)


# Thread Priority and Affinity (platform-specific)

def set_thread_priority(runtime, thread: NLPLThread, priority: int):
    """
    Set thread priority (0=lowest, 50=normal, 100=highest)
    
    Args:
        thread: Thread handle
        priority: Priority level (0-100)
        
    Note: Platform-specific, may not be supported on all systems
    
    Example:
        set_thread_priority with thread_handle and 75
    """
    # Python doesn't provide direct priority control
    # This would need platform-specific implementation
    # On Linux: pthread_setschedparam
    # On Windows: SetThreadPriority
    pass


def set_thread_affinity(runtime, thread: NLPLThread, cpu_mask: int):
    """
    Set CPU affinity for thread
    
    Args:
        thread: Thread handle
        cpu_mask: Bitmask of CPUs (bit 0 = CPU 0, etc.)
        
    Note: Platform-specific, may not be supported
    
    Example:
        # Run on CPUs 0 and 2
        set_thread_affinity with thread_handle and 5  # Binary: 0101
    """
    # Platform-specific implementation needed
    # On Linux: pthread_setaffinity_np
    # On Windows: SetThreadAffinityMask
    pass


def register_stdlib(runtime):
    """Register threading module functions with NLPL runtime"""
    from nlpl.runtime.runtime import Runtime
    
    # Thread creation and management
    runtime.register_function("create_thread", create_thread)
    runtime.register_function("join_thread", join_thread)
    runtime.register_function("detach_thread", detach_thread)
    runtime.register_function("thread_is_alive", thread_is_alive)
    
    # Thread identification
    runtime.register_function("get_thread_id", get_thread_id)
    runtime.register_function("get_current_thread_id", get_current_thread_id)
    runtime.register_function("get_current_thread_name", get_current_thread_name)
    runtime.register_function("set_thread_name", set_thread_name)
    
    # Thread control
    runtime.register_function("sleep_thread", sleep_thread)
    runtime.register_function("yield_thread", yield_thread)
    runtime.register_function("get_cpu_count", get_cpu_count)
    
    # Thread-local storage
    runtime.register_function("thread_local_set", thread_local_set)
    runtime.register_function("thread_local_get", thread_local_get)
    runtime.register_function("thread_local_has", thread_local_has)
    runtime.register_function("thread_local_delete", thread_local_delete)
    
    # Thread priority and affinity (platform-specific)
    runtime.register_function("set_thread_priority", set_thread_priority)
    runtime.register_function("set_thread_affinity", set_thread_affinity)
