"""nexuslang.build — build pipeline helpers for NexusLang.

Submodules
----------
lto     Link-Time Optimisation driver (ThinLTO / Full LTO via llvm-lto or lld).
"""

from .lto import LTOConfig, LTOLinker, LTOMode, LTOResult

__all__ = ["LTOConfig", "LTOLinker", "LTOMode", "LTOResult"]
