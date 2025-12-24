"""Async utilities for NLPL."""

from ...stdlib.asyncio_utils.promise import register_promise_functions


def register_async_functions(runtime):
    """Register all async utility functions."""
    register_promise_functions(runtime)


__all__ = [
    "register_async_functions",
]
