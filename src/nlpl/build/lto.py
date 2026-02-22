"""
NLPL Link-Time Optimization (LTO)

Orchestrates LLVM-based LTO: bitcode emission, llvm-link, opt passes, and
final native code generation via llc.

Supported modes:
- THIN  — ThinLTO: fast parallel LTO using summaries (recommended for dev)
- FULL  — Full LTO: maximum optimization, slower link step
"""

import subprocess
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class LTOMode(Enum):
    """Link-time optimization mode."""
    DISABLED = "disabled"
    THIN = "thin"    # ThinLTO — faster, good for incremental workflows
    FULL = "full"    # Full LTO — maximum whole-program optimization


@dataclass
class LTOConfig:
    """Configuration for LTO pipeline.

    Attributes:
        mode: LTO mode (disabled/thin/full).
        opt_level: LLVM opt level passed to ``opt`` (0-3).
        strip_debug: Strip debug symbols from final output.
        internalize: Internalize non-exported symbols (enables more inlining).
        passes: Additional LLVM pass pipeline string (e.g. ``"default<O3>"``).
            When empty, a sensible default is used based on ``opt_level``.
    """
    mode: LTOMode = LTOMode.DISABLED
    opt_level: int = 2
    strip_debug: bool = False
    internalize: bool = True
    passes: str = ""


@dataclass
class LTOResult:
    """Outcome of an LTO pipeline run."""
    success: bool
    output_file: Optional[Path] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    # Names and paths of LLVM tools that were invoked
    tools_used: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Tool discovery
# ---------------------------------------------------------------------------

class LLVMTools:
    """
    Locates LLVM command-line tools required for LTO.

    Searches ``PATH`` and a set of versioned suffixes
    (e.g. ``llvm-link-18``, ``llvm-link-17``, …).
    """

    _CANDIDATES = [
        "",        # bare name — e.g. llvm-link
        "-18", "-17", "-16", "-15", "-14", "-13",
    ]

    def __init__(self) -> None:
        self._cache: Dict[str, Optional[Path]] = {}

    def find(self, tool: str) -> Optional[Path]:
        """Return the first available path for *tool*, or None."""
        if tool in self._cache:
            return self._cache[tool]

        for suffix in self._CANDIDATES:
            candidate = shutil.which(f"{tool}{suffix}")
            if candidate:
                result = Path(candidate)
                self._cache[tool] = result
                return result

        self._cache[tool] = None
        return None

    def check_lto_tools(self) -> Dict[str, Optional[Path]]:
        """
        Return a dict of required LTO tool names to their paths (or None).

        Required tools: llvm-link, opt, llc, llvm-strip (optional).
        """
        return {
            "llvm-link": self.find("llvm-link"),
            "opt":        self.find("opt"),
            "llc":        self.find("llc"),
            "llvm-strip": self.find("llvm-strip"),  # optional
        }

    def all_required_available(self) -> bool:
        """Return True if llvm-link, opt, and llc are all present."""
        tools = self.check_lto_tools()
        return all(
            tools[t] is not None for t in ("llvm-link", "opt", "llc")
        )


# ---------------------------------------------------------------------------
# LTO pipeline
# ---------------------------------------------------------------------------

class LTOLinker:
    """
    Runs the LLVM LTO pipeline.

    Pipeline (per-mode):

    **Full LTO**
    ::

        llvm-link <bitcode files> -o linked.bc
        opt [--lto-internalize] -passes=<passes> linked.bc -o optimized.bc
        llc -O<n> [-filetype=obj | -filetype=asm] optimized.bc -o output

    **ThinLTO**  (uses clang's ThinLTO orchestration via -flto=thin when
    available, falls back to the Full pipeline with thin-specific passes)
    ::

        llvm-link --only-needed <bitcode files> -o linked.bc
        opt -passes="thinlto<O2>" linked.bc -o optimized.bc
        llc optimized.bc -o output

    Args:
        config: LTO configuration.
        tools: LLVMTools instance (created automatically if not provided).
    """

    def __init__(
        self,
        config: LTOConfig,
        tools: Optional[LLVMTools] = None,
    ) -> None:
        self.config = config
        self.tools = tools or LLVMTools()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def link_with_lto(
        self,
        bitcode_files: List[Path],
        output: Path,
        work_dir: Optional[Path] = None,
    ) -> LTOResult:
        """
        Run the complete LTO pipeline on a list of LLVM bitcode files.

        Args:
            bitcode_files: Paths to ``.ll`` (text IR) or ``.bc`` (bitcode) files.
            output: Final native output path (object file or executable).
            work_dir: Scratch directory for intermediate files (defaults to
                      ``output.parent``).

        Returns:
            LTOResult with success status and diagnostics.
        """
        if not bitcode_files:
            return LTOResult(
                success=False,
                errors=["No bitcode files provided for LTO"],
            )

        if not self.tools.all_required_available():
            missing = [
                t for t, p in self.tools.check_lto_tools().items()
                if p is None and t != "llvm-strip"
            ]
            return LTOResult(
                success=False,
                errors=[
                    f"LTO requires LLVM tools not found on PATH: {missing}. "
                    f"Install llvm (e.g. apt install llvm)."
                ],
            )

        scratch = work_dir or output.parent
        scratch.mkdir(parents=True, exist_ok=True)

        linked_bc = scratch / "_lto_linked.bc"
        opt_bc = scratch / "_lto_optimized.bc"
        errors: List[str] = []
        warnings: List[str] = []
        tools_used: List[str] = []

        # Step 1: link bitcode
        ok, errs, warns, tool = self._run_llvm_link(
            bitcode_files, linked_bc
        )
        errors.extend(errs)
        warnings.extend(warns)
        tools_used.append(tool)
        if not ok:
            return LTOResult(
                success=False,
                errors=errors,
                warnings=warnings,
                tools_used=tools_used,
            )

        # Step 2: optimize
        ok, errs, warns, tool = self._run_opt(linked_bc, opt_bc)
        errors.extend(errs)
        warnings.extend(warns)
        tools_used.append(tool)
        if not ok:
            return LTOResult(
                success=False,
                errors=errors,
                warnings=warnings,
                tools_used=tools_used,
            )

        # Step 3: native code generation
        ok, errs, warns, tool = self._run_llc(opt_bc, output)
        errors.extend(errs)
        warnings.extend(warns)
        tools_used.append(tool)
        if not ok:
            return LTOResult(
                success=False,
                errors=errors,
                warnings=warnings,
                tools_used=tools_used,
            )

        # Step 4 (optional): strip debug symbols
        if self.config.strip_debug:
            strip_tool = self.tools.find("llvm-strip")
            if strip_tool:
                self._run_tool([str(strip_tool), "--strip-debug", str(output)])
                tools_used.append("llvm-strip")

        return LTOResult(
            success=True,
            output_file=output,
            errors=errors,
            warnings=warnings,
            tools_used=tools_used,
        )

    def emit_bitcode_flags(self) -> List[str]:
        """
        Return compiler flags required to emit LLVM bitcode for LTO.

        Add these to every per-file compilation invocation so the compiler
        emits ``.bc``.  Returns an empty list when LTO is disabled.
        """
        if self.config.mode == LTOMode.DISABLED:
            return []
        flags = ["-emit-llvm"]
        if self.config.mode == LTOMode.THIN:
            flags.append("-flto=thin")
        elif self.config.mode == LTOMode.FULL:
            flags.append("-flto")
        return flags

    # ------------------------------------------------------------------
    # Internal step runners
    # ------------------------------------------------------------------

    def _run_llvm_link(
        self,
        inputs: List[Path],
        output: Path,
    ) -> Tuple:
        """Run llvm-link to merge bitcode files."""
        tool = str(self.tools.find("llvm-link"))
        cmd = [tool]

        if self.config.mode == LTOMode.THIN:
            cmd.append("--only-needed")

        cmd.extend(str(f) for f in inputs)
        cmd.extend(["-o", str(output)])

        ok, errs, warns = self._run_tool(cmd)
        return ok, errs, warns, "llvm-link"

    def _run_opt(self, input_bc: Path, output_bc: Path) -> Tuple:
        """Run opt to apply LTO optimization passes."""
        tool = str(self.tools.find("opt"))
        level = self.config.opt_level

        if self.config.passes:
            passes = self.config.passes
        elif self.config.mode == LTOMode.THIN:
            passes = f"thinlto<O{level}>"
        else:
            passes = f"default<O{level}>"

        cmd = [tool, f"-passes={passes}"]

        if self.config.internalize:
            cmd.append("--internalize")

        cmd.extend([str(input_bc), "-o", str(output_bc)])

        # Fallback: older LLVM versions use -O<n> syntax instead of -passes
        ok, errs, warns = self._run_tool(cmd)
        if not ok and "-passes" in " ".join(errs):
            cmd_legacy = [tool, f"-O{level}"]
            if self.config.internalize:
                cmd_legacy.append("--internalize")
            cmd_legacy.extend([str(input_bc), "-o", str(output_bc)])
            ok, errs, warns = self._run_tool(cmd_legacy)

        return ok, errs, warns, "opt"

    def _run_llc(self, input_bc: Path, output: Path) -> Tuple:
        """Run llc for native code generation."""
        tool = str(self.tools.find("llc"))
        level = self.config.opt_level
        cmd = [
            tool,
            f"-O{level}",
            "-filetype=obj",
            str(input_bc),
            "-o", str(output),
        ]
        ok, errs, warns = self._run_tool(cmd)
        return ok, errs, warns, "llc"

    @staticmethod
    def _run_tool(cmd: List[str]) -> Tuple:
        """Execute a subprocess and classify its output."""
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            errors: List[str] = []
            warnings: List[str] = []
            for line in (proc.stderr or "").splitlines():
                if "error" in line.lower():
                    errors.append(line)
                elif "warning" in line.lower():
                    warnings.append(line)
            return proc.returncode == 0, errors, warnings
        except OSError as exc:
            return False, [f"Failed to run {cmd[0]}: {exc}"], []


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def lto_flags_for_profile(
    mode: LTOMode,
    opt_level: int = 2,
    strip: bool = False,
) -> List[str]:
    """
    Return a list of clang/NLPL compiler flags that activate LTO at link time.

    These are suitable for single-invocation builds where the compiler
    also drives the linker (rather than using the separate pipeline above).
    """
    flags: List[str] = []
    if mode == LTOMode.THIN:
        flags.append("-flto=thin")
    elif mode == LTOMode.FULL:
        flags.append("-flto")
    if flags:
        flags.append(f"-O{opt_level}")
        if strip:
            flags.append("-s")
    return flags


# Required tuple type hint (kept at module level to avoid circular imports)
from typing import Tuple  # noqa: E402 (placed after class bodies intentionally)
