"""
NLPL Safety and Error Handling System
======================================

Provides production-ready error handling:
- Result<T, E> type for recoverable errors
- Panic system for unrecoverable errors
- Null safety with Optional<T>
- Basic ownership and borrow checking
"""

from nlpl.safety.result import Result, Ok, Err
from nlpl.safety.panic import Panic, PanicHandler, set_panic_handler
from nlpl.safety.null_safety import NullSafetyChecker
from nlpl.safety.ownership import OwnershipTracker, MoveSemantics

__all__ = [
    'Result', 'Ok', 'Err',
    'Panic', 'PanicHandler', 'set_panic_handler',
    'NullSafetyChecker',
    'OwnershipTracker', 'MoveSemantics'
]
