#!/usr/bin/env python3
"""
NLPL Language Server Entry Point
=================================

Starts the NexusLang Language Server for IDE integration.

Usage:
    python -m nxl_lsp
    or
    python src/nxl_lsp.py
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from nexuslang.lsp.server import NLPLLanguageServer


def main():
    """Start the NexusLang Language Server."""
    server = NLPLLanguageServer()
    server.start()


if __name__ == '__main__':
    main()
