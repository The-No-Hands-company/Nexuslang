"""
Algorithm utilities (C++ STL <algorithm> equivalent).

Provides standard algorithms for searching, sorting, and transforming data.

Features:
- Sorting algorithms (sort, stable_sort, partial_sort)
- Searching algorithms (find, binary_search, lower_bound, upper_bound)
- Mutating algorithms (reverse, rotate, shuffle, unique)
- Aggregation (accumulate, reduce, min/max)
- Transformation (transform, map, filter)

Example usage in NLPL:
    # Sorting
    set data to [3, 1, 4, 1, 5, 9, 2, 6]
    set sorted to algo_sort with data
    
    # Searching
    set index to algo_find with sorted and 5
    set found to algo_binary_search with sorted and 5
    
    # Transformation
    set doubled to algo_transform with data and double_func
    set evens to algo_filter with data and is_even_func
    
    # Aggregation
    set sum to algo_accumulate with data and 0
    set max_val to algo_max_element with data
"""

from ...runtime.runtime import Runtime
import random
import bisect


def algo_sort(lst, reverse=False):
    """
    Sort list in ascending order (or descending if reverse=True).
    
    Args:
        lst: List to sort
        reverse: If True, sort in descending order
    
    Returns:
        Sorted list (new list)
    """
    if not isinstance(lst, list):
        return []
    
    return sorted(lst, reverse=bool(reverse))


def algo_stable_sort(lst, reverse=False):
    """
    Stable sort (preserves relative order of equal elements).
    
    Args:
        lst: List to sort
        reverse: If True, sort in descending order
    
    Returns:
        Sorted list (new list)
    """
    # Python's sorted() is stable by default
    return algo_sort(lst, reverse)


def algo_partial_sort(lst, n, reverse=False):
    """
    Partially sort list (only first n elements are sorted).
    
    Args:
        lst: List to sort
        n: Number of elements to sort
        reverse: If True, sort in descending order
    
    Returns:
        Partially sorted list
    """
    if not isinstance(lst, list) or not lst:
        return []
    
    n = min(int(n), len(lst))
    result = lst.copy()
    
    # Sort and take first n elements, keep rest unsorted
    sorted_part = sorted(result[:n], reverse=bool(reverse))
    
    # For partial sort, we want smallest/largest n elements sorted
    # Get all elements, sort, take n, then append unsorted remainder
    all_sorted = sorted(result, reverse=bool(reverse))
    return all_sorted[:n] + result[n:]


def algo_find(lst, value):
    """
    Find first occurrence of value in list.
    
    Args:
        lst: List to search
        value: Value to find
    
    Returns:
        Index of first occurrence, or -1 if not found
    """
    if not isinstance(lst, list):
        return -1
    
    try:
        return lst.index(value)
    except ValueError:
        return -1


def algo_find_if(lst, predicate_func):
    """
    Find first element satisfying predicate.
    
    Args:
        lst: List to search
        predicate_func: Function that returns True for matching element
    
    Returns:
        Index of first matching element, or -1
    """
    if not isinstance(lst, list):
        return -1
    
    for i, item in enumerate(lst):
        try:
            if predicate_func(item):
                return i
        except:
            continue
    
    return -1


def algo_binary_search(lst, value):
    """
    Binary search in sorted list.
    
    Args:
        lst: Sorted list
        value: Value to find
    
    Returns:
        True if found, False otherwise
    """
    if not isinstance(lst, list):
        return False
    
    index = bisect.bisect_left(lst, value)
    return index < len(lst) and lst[index] == value


def algo_lower_bound(lst, value):
    """
    Find first position where value could be inserted to maintain sorted order.
    
    Args:
        lst: Sorted list
        value: Value to search for
    
    Returns:
        Index for insertion
    """
    if not isinstance(lst, list):
        return 0
    
    return bisect.bisect_left(lst, value)


def algo_upper_bound(lst, value):
    """
    Find last position where value could be inserted to maintain sorted order.
    
    Args:
        lst: Sorted list
        value: Value to search for
    
    Returns:
        Index for insertion
    """
    if not isinstance(lst, list):
        return 0
    
    return bisect.bisect_right(lst, value)


def algo_reverse(lst):
    """
    Reverse list order.
    
    Args:
        lst: List to reverse
    
    Returns:
        Reversed list (new list)
    """
    if not isinstance(lst, list):
        return []
    
    return list(reversed(lst))


def algo_rotate(lst, n):
    """
    Rotate list elements.
    
    Args:
        lst: List to rotate
        n: Number of positions to rotate (positive = left, negative = right)
    
    Returns:
        Rotated list (new list)
    """
    if not isinstance(lst, list) or not lst:
        return []
    
    n = int(n) % len(lst)
    return lst[n:] + lst[:n]


def algo_shuffle(lst):
    """
    Randomly shuffle list elements.
    
    Args:
        lst: List to shuffle
    
    Returns:
        Shuffled list (new list)
    """
    if not isinstance(lst, list):
        return []
    
    result = lst.copy()
    random.shuffle(result)
    return result


def algo_unique(lst):
    """
    Remove consecutive duplicate elements.
    
    Args:
        lst: List to process
    
    Returns:
        List with consecutive duplicates removed
    """
    if not isinstance(lst, list) or not lst:
        return []
    
    result = [lst[0]]
    for item in lst[1:]:
        if item != result[-1]:
            result.append(item)
    
    return result


def algo_unique_all(lst):
    """
    Remove all duplicate elements (keeping first occurrence).
    
    Args:
        lst: List to process
    
    Returns:
        List with all duplicates removed
    """
    if not isinstance(lst, list):
        return []
    
    seen = set()
    result = []
    
    for item in lst:
        # Handle unhashable types
        try:
            if item not in seen:
                seen.add(item)
                result.append(item)
        except TypeError:
            # Unhashable type - check manually
            if item not in result:
                result.append(item)
    
    return result


def algo_partition(lst, predicate_func):
    """
    Partition list based on predicate.
    
    Args:
        lst: List to partition
        predicate_func: Function returning True for first partition
    
    Returns:
        Dictionary with 'true' and 'false' partitions
    """
    if not isinstance(lst, list):
        return {"true": [], "false": []}
    
    true_partition = []
    false_partition = []
    
    for item in lst:
        try:
            if predicate_func(item):
                true_partition.append(item)
            else:
                false_partition.append(item)
        except:
            false_partition.append(item)
    
    return {"true": true_partition, "false": false_partition}


def algo_accumulate(lst, init=0, func=None):
    """
    Accumulate values using binary operation.
    
    Args:
        lst: List to accumulate
        init: Initial value
        func: Binary function (default: addition)
    
    Returns:
        Accumulated result
    """
    if not isinstance(lst, list):
        return init
    
    result = init
    
    if func is None:
        # Default: addition
        for item in lst:
            result = result + item
    else:
        # Custom function
        for item in lst:
            try:
                result = func(result, item)
            except:
                continue
    
    return result


def algo_reduce(lst, func, init=None):
    """
    Reduce list to single value using binary function.
    
    Args:
        lst: List to reduce
        func: Binary reduction function
        init: Initial value (if None, use first element)
    
    Returns:
        Reduced value
    """
    if not isinstance(lst, list) or not lst:
        return init
    
    if init is None:
        result = lst[0]
        start = 1
    else:
        result = init
        start = 0
    
    for item in lst[start:]:
        try:
            result = func(result, item)
        except:
            continue
    
    return result


def algo_transform(lst, func):
    """
    Transform each element using function.
    
    Args:
        lst: List to transform
        func: Transformation function
    
    Returns:
        Transformed list
    """
    if not isinstance(lst, list):
        return []
    
    result = []
    for item in lst:
        try:
            result.append(func(item))
        except:
            result.append(item)
    
    return result


def algo_map(lst, func):
    """
    Map function over list (alias for transform).
    
    Args:
        lst: List to map
        func: Mapping function
    
    Returns:
        Mapped list
    """
    return algo_transform(lst, func)


def algo_filter(lst, predicate_func):
    """
    Filter list elements by predicate.
    
    Args:
        lst: List to filter
        predicate_func: Predicate function
    
    Returns:
        Filtered list
    """
    if not isinstance(lst, list):
        return []
    
    result = []
    for item in lst:
        try:
            if predicate_func(item):
                result.append(item)
        except:
            continue
    
    return result


def algo_count(lst, value):
    """
    Count occurrences of value.
    
    Args:
        lst: List to search
        value: Value to count
    
    Returns:
        Number of occurrences
    """
    if not isinstance(lst, list):
        return 0
    
    return lst.count(value)


def algo_count_if(lst, predicate_func):
    """
    Count elements satisfying predicate.
    
    Args:
        lst: List to search
        predicate_func: Predicate function
    
    Returns:
        Count of matching elements
    """
    if not isinstance(lst, list):
        return 0
    
    count = 0
    for item in lst:
        try:
            if predicate_func(item):
                count += 1
        except:
            continue
    
    return count


def algo_min_element(lst):
    """
    Find minimum element.
    
    Args:
        lst: List to search
    
    Returns:
        Minimum value, or None if empty
    """
    if not isinstance(lst, list) or not lst:
        return None
    
    return min(lst)


def algo_max_element(lst):
    """
    Find maximum element.
    
    Args:
        lst: List to search
    
    Returns:
        Maximum value, or None if empty
    """
    if not isinstance(lst, list) or not lst:
        return None
    
    return max(lst)


def algo_minmax_element(lst):
    """
    Find both minimum and maximum elements.
    
    Args:
        lst: List to search
    
    Returns:
        Dictionary with 'min' and 'max' keys
    """
    if not isinstance(lst, list) or not lst:
        return {"min": None, "max": None}
    
    return {"min": min(lst), "max": max(lst)}


def algo_all_of(lst, predicate_func):
    """
    Check if all elements satisfy predicate.
    
    Args:
        lst: List to check
        predicate_func: Predicate function
    
    Returns:
        True if all satisfy predicate
    """
    if not isinstance(lst, list):
        return True
    
    for item in lst:
        try:
            if not predicate_func(item):
                return False
        except:
            return False
    
    return True


def algo_any_of(lst, predicate_func):
    """
    Check if any element satisfies predicate.
    
    Args:
        lst: List to check
        predicate_func: Predicate function
    
    Returns:
        True if any satisfies predicate
    """
    if not isinstance(lst, list):
        return False
    
    for item in lst:
        try:
            if predicate_func(item):
                return True
        except:
            continue
    
    return False


def algo_none_of(lst, predicate_func):
    """
    Check if no elements satisfy predicate.
    
    Args:
        lst: List to check
        predicate_func: Predicate function
    
    Returns:
        True if none satisfy predicate
    """
    return not algo_any_of(lst, predicate_func)


def register_algorithms_functions(runtime: Runtime) -> None:
    """Register algorithm functions with the runtime."""
    
    # Sorting
    runtime.register_function("algo_sort", algo_sort)
    runtime.register_function("algo_stable_sort", algo_stable_sort)
    runtime.register_function("algo_partial_sort", algo_partial_sort)
    
    # Searching
    runtime.register_function("algo_find", algo_find)
    runtime.register_function("algo_find_if", algo_find_if)
    runtime.register_function("algo_binary_search", algo_binary_search)
    runtime.register_function("algo_lower_bound", algo_lower_bound)
    runtime.register_function("algo_upper_bound", algo_upper_bound)
    
    # Mutating
    runtime.register_function("algo_reverse", algo_reverse)
    runtime.register_function("algo_rotate", algo_rotate)
    runtime.register_function("algo_shuffle", algo_shuffle)
    runtime.register_function("algo_unique", algo_unique)
    runtime.register_function("algo_unique_all", algo_unique_all)
    runtime.register_function("algo_partition", algo_partition)
    
    # Aggregation
    runtime.register_function("algo_accumulate", algo_accumulate)
    runtime.register_function("algo_reduce", algo_reduce)
    runtime.register_function("algo_min_element", algo_min_element)
    runtime.register_function("algo_max_element", algo_max_element)
    runtime.register_function("algo_minmax_element", algo_minmax_element)
    
    # Transformation
    runtime.register_function("algo_transform", algo_transform)
    runtime.register_function("algo_map", algo_map)
    runtime.register_function("algo_filter", algo_filter)
    
    # Counting
    runtime.register_function("algo_count", algo_count)
    runtime.register_function("algo_count_if", algo_count_if)
    
    # Predicates
    runtime.register_function("algo_all_of", algo_all_of)
    runtime.register_function("algo_any_of", algo_any_of)
    runtime.register_function("algo_none_of", algo_none_of)
