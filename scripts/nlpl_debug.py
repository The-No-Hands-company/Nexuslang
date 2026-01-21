#!/usr/bin/env python3
"""
NLPL Debugger Entry Point

Convenience script to launch the NLPL debugger.

Usage:
    python nlpl_debug.py program.nlpl [--break 10 --break 25]
    
Or make executable and run directly:
    chmod +x nlpl_debug.py
    ./nlpl_debug.py program.nlpl
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nlpl.debugger.debugger import main

if __name__ == '__main__':
    main()
