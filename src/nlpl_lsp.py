#!/usr/bin/env python3
"""
Backward-compatible NLPL LSP launcher.

This shim preserves old entrypoints while delegating to nxl_lsp.
"""

from nxl_lsp import main


if __name__ == "__main__":
    main()
