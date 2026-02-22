"""
NLPL Build System

Modern build system for NLPL projects with package management,
incremental compilation, parallel builds, LTO, and cross-compilation.
"""

from .project import Project
from .builder import Builder
from .cache import BuildCache
from .manifest import (
    Manifest,
    PackageMetadata,
    Dependency,
    BuildProfile,
    BinaryTarget,
    LibraryTarget,
    Workspace,
    CrateType,
    PanicStrategy,
    load_manifest
)
from .parallel import (
    ParallelCompiler,
    CompilationTask,
    DependencyGraph,
    TaskResult,
    build_tasks_from_sources,
)
from .lto import (
    LTOMode,
    LTOConfig,
    LTOResult,
    LTOLinker,
    LLVMTools,
    lto_flags_for_profile,
)
from .cross import (
    TargetArch,
    TargetOS,
    TargetABI,
    TargetTriple,
    ToolchainInfo,
    ToolchainDetector,
    CrossCompiler,
    CrossCompileResult,
    KNOWN_TARGETS,
    get_cross_compiler,
)

__all__ = [
    # Core
    "Project",
    "Builder",
    "BuildCache",
    # Manifest
    "Manifest",
    "PackageMetadata",
    "Dependency",
    "BuildProfile",
    "BinaryTarget",
    "LibraryTarget",
    "Workspace",
    "CrateType",
    "PanicStrategy",
    "load_manifest",
    # Parallel compilation
    "ParallelCompiler",
    "CompilationTask",
    "DependencyGraph",
    "TaskResult",
    "build_tasks_from_sources",
    # LTO
    "LTOMode",
    "LTOConfig",
    "LTOResult",
    "LTOLinker",
    "LLVMTools",
    "lto_flags_for_profile",
    # Cross-compilation
    "TargetArch",
    "TargetOS",
    "TargetABI",
    "TargetTriple",
    "ToolchainInfo",
    "ToolchainDetector",
    "CrossCompiler",
    "CrossCompileResult",
    "KNOWN_TARGETS",
    "get_cross_compiler",
]

