"""
Collections for NLPL: Vec<T>, HashMap<K,V>, Set<T>

Production-ready implementations - NO SHORTCUTS.
"""

from typing import TypeVar, Generic, Optional, Iterator as PyIterator
from ..option_result import Option, Some, NoneValue

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


class Vec(Generic[T]):
    """Vec<T> - dynamic array/vector.
    
    Production-ready implementation with:
    - Dynamic resizing
    - Iterator integration
    - Bounds checking
    - Full error handling
    """
    
    def __init__(self, initial_capacity: int = 10):
        """Create a new Vec with optional initial capacity."""
        if initial_capacity < 0:
            raise ValueError(f"Capacity must be non-negative, got {initial_capacity}")
        
        self._data = []
        self._capacity = initial_capacity
    
    def push(self, value: T) -> None:
        """Add element to end of vector."""
        self._data.append(value)
    
    def pop(self) -> Option[T]:
        """Remove and return last element.
        
        Returns:
            Some(value) if vector not empty
            None if vector is empty
        """
        if len(self._data) == 0:
            return NoneValue()
        return Some(self._data.pop())
    
    def get(self, index: int) -> Option[T]:
        """Get element at index.
        
        Returns:
            Some(value) if index valid
            None if index out of bounds
        """
        if 0 <= index < len(self._data):
            return Some(self._data[index])
        return NoneValue()
    
    def set(self, index: int, value: T) -> bool:
        """Set element at index.
        
        Returns:
            True if successful
            False if index out of bounds
        """
        if 0 <= index < len(self._data):
            self._data[index] = value
            return True
        return False
    
    def len(self) -> int:
        """Return number of elements."""
        return len(self._data)
    
    def capacity(self) -> int:
        """Return current capacity."""
        return self._capacity
    
    def is_empty(self) -> bool:
        """Check if vector is empty."""
        return len(self._data) == 0
    
    def clear(self) -> None:
        """Remove all elements."""
        self._data.clear()
    
    def __iter__(self) -> PyIterator[T]:
        """Python iterator protocol."""
        return iter(self._data)
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __repr__(self) -> str:
        return f"Vec({self._data})"


class HashMap(Generic[K, V]):
    """HashMap<K,V> - hash map/dictionary.
    
    Production-ready implementation with:
    - O(1) average insert/get/remove
    - Iterator integration
    - Full error handling
    """
    
    def __init__(self):
        """Create a new HashMap."""
        self._data = {}
    
    def insert(self, key: K, value: V) -> Option[V]:
        """Insert key-value pair.
        
        Returns:
            Some(old_value) if key existed
            None if key was new
        """
        old_value = self._data.get(key)
        self._data[key] = value
        
        if old_value is not None:
            return Some(old_value)
        return NoneValue()
    
    def get(self, key: K) -> Option[V]:
        """Get value for key.
        
        Returns:
            Some(value) if key exists
            None if key not found
        """
        value = self._data.get(key)
        if value is not None:
            return Some(value)
        return NoneValue()
    
    def remove(self, key: K) -> Option[V]:
        """Remove key-value pair.
        
        Returns:
            Some(value) if key existed
            None if key not found
        """
        value = self._data.pop(key, None)
        if value is not None:
            return Some(value)
        return NoneValue()
    
    def contains_key(self, key: K) -> bool:
        """Check if key exists."""
        return key in self._data
    
    def len(self) -> int:
        """Return number of key-value pairs."""
        return len(self._data)
    
    def is_empty(self) -> bool:
        """Check if map is empty."""
        return len(self._data) == 0
    
    def clear(self) -> None:
        """Remove all key-value pairs."""
        self._data.clear()
    
    def keys(self):
        """Return iterator over keys."""
        return iter(self._data.keys())
    
    def values(self):
        """Return iterator over values."""
        return iter(self._data.values())
    
    def items(self):
        """Return iterator over (key, value) pairs."""
        return iter(self._data.items())
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __repr__(self) -> str:
        return f"HashMap({self._data})"


class Set(Generic[T]):
    """Set<T> - unordered set.
    
    Production-ready implementation with:
    - O(1) average add/contains/remove
    - Set operations (union, intersection, difference)
    - Iterator integration
    """
    
    def __init__(self):
        """Create a new Set."""
        self._data = set()
    
    def add(self, value: T) -> bool:
        """Add element to set.
        
        Returns:
            True if element was new
            False if element already existed
        """
        if value in self._data:
            return False
        self._data.add(value)
        return True
    
    def remove(self, value: T) -> bool:
        """Remove element from set.
        
        Returns:
            True if element was removed
            False if element not found
        """
        if value in self._data:
            self._data.remove(value)
            return True
        return False
    
    def contains(self, value: T) -> bool:
        """Check if element exists in set."""
        return value in self._data
    
    def len(self) -> int:
        """Return number of elements."""
        return len(self._data)
    
    def is_empty(self) -> bool:
        """Check if set is empty."""
        return len(self._data) == 0
    
    def clear(self) -> None:
        """Remove all elements."""
        self._data.clear()
    
    def union(self, other: 'Set[T]') -> 'Set[T]':
        """Return union of two sets."""
        result = Set()
        result._data = self._data.union(other._data)
        return result
    
    def intersection(self, other: 'Set[T]') -> 'Set[T]':
        """Return intersection of two sets."""
        result = Set()
        result._data = self._data.intersection(other._data)
        return result
    
    def difference(self, other: 'Set[T]') -> 'Set[T]':
        """Return difference of two sets."""
        result = Set()
        result._data = self._data.difference(other._data)
        return result
    
    def __iter__(self) -> PyIterator[T]:
        """Python iterator protocol."""
        return iter(self._data)
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __repr__(self) -> str:
        return f"Set({self._data})"




def list_append(target, value):
    """Append a value to a list or collection.
    
    Args:
        target: List, Vec, or any collection with an append/push method
        value: Value to append
        
    Returns:
        None (modifies target in-place)
    """
    if isinstance(target, list):
        target.append(value)
    elif isinstance(target, Vec):
        target.push(value)
    elif hasattr(target, 'append'):
        target.append(value)
    elif hasattr(target, 'push'):
        target.push(value)
    else:
        raise TypeError(f"Cannot append to type {type(target).__name__}")
    return None


def register_collections_functions(runtime):
    """Register collection constructors with runtime."""
    runtime.register_function("Vec", Vec)
    runtime.register_function("HashMap", HashMap)
    runtime.register_function("Set", Set)
    runtime.register_function("list_append", list_append)
    runtime.register_function("append", list_append)  # Alias
