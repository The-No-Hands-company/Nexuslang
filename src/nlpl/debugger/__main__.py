"""
NLPL Debug Adapter Protocol Server Entry Point

Run as: python3 -m nlpl.debugger
"""

from .dap_server import main

if __name__ == '__main__':
    main()
