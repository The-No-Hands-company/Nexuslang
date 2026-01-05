#!/usr/bin/env python3
"""
NLPL Language Server Entry Point
=================================

Starts the NLPL Language Server for IDE integration.

Usage:
    python -m nlpl_lsp
    or
    python src/nlpl_lsp.py
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from nlpl.lsp.server import NLPLLanguageServer


def main():
    """Start the NLPL Language Server."""
    server = NLPLLanguageServer()
    server.start()


if __name__ == '__main__':
    main()
