"""
NLPL Static Analyzer
====================

Production-grade static analysis for NLPL code.

Catches bugs before runtime:
- Memory safety violations
- Null pointer dereferences
- Resource leaks
- Uninitialized variables
- Type mismatches
- Race conditions
- Dead code
- Performance issues
"""

from .analyzer import StaticAnalyzer
from .checks import *
from .report import AnalysisReport, Issue

__all__ = [
    'StaticAnalyzer',
    'AnalysisReport',
    'Issue',
]
