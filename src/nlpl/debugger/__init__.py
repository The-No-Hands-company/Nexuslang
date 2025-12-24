"""
NLPL Debugger Integration
==========================

Enables source-level debugging of compiled NLPL programs using GDB/LLDB.

Components:
- DWARF debug info generation (debug_info.py)
- Debug symbol table (symbols.py)
- Debugger adapter protocol (dap_server.py)
"""

from .debug_info import DebugInfoGenerator
from .symbols import SymbolTable, DebugSymbol, SymbolType

__all__ = [
    'DebugInfoGenerator',
    'SymbolTable',
    'DebugSymbol',
    'SymbolType',
]
