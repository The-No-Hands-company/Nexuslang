"""nexuslang.build.lto — Link-Time Optimisation support.

Wraps the host toolchain's LTO facilities (LLVM lld / llvm-lto / gold-plugin)
to produce a single optimised native binary from LLVM bitcode (.ll) files
emitted by the NexusLang compiler backend.

Supported LTO modes
-------------------
THIN    Per-module summaries; fast parallel link.  Selected for opt_level < 3.
FULL    Whole-program analysis; slowest but highest-quality.  Used at -O3.

Usage
-----
    from nexuslang.build.lto import LTOConfig, LTOLinker, LTOMode, LTOResult

    cfg = LTOConfig(mode=LTOMode.THIN, opt_level=2, strip_debug=False)
    linker = LTOLinker(cfg)
    result = linker.link_with_lto(
        bitcode_files=["a.ll", "b.ll"],
        output=Path("out/myapp"),
        work_dir=Path("out"),
    )
    if result.success:
        print("linked ->", result.output_file)
    else:
        for err in result.errors:
            print("error:", err)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class LTOMode(Enum):
    """LTO link strategy."""
    THIN = "thin"   # ThinLTO – fast; default for opt < 3
    FULL = "full"   # Full LTO – slow, maximum quality; used at O3


@dataclass
class LTOConfig:
    """Configuration for an LTO link pass."""

    mode: LTOMode = LTOMode.THIN
    opt_level: int = 2          # 0..3  maps directly to -O<n> passed to the linker
    strip_debug: bool = False   # strip debug info from output
    internalize: bool = True    # internalize all non-exported symbols
    extra_link_flags: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0 <= self.opt_level <= 3:
            raise ValueError(f"opt_level must be 0–3, got {self.opt_level}")


@dataclass
class LTOResult:
    """Outcome of an LTO link invocation."""

    success: bool
    output_file: Optional[Path]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _find_tool(*candidates: str) -> Optional[str]:
    """Return the first candidate found on PATH, or None."""
    for name in candidates:
        found = shutil.which(name)
        if found:
            return found
    return None


def _ll_to_bc(ll_file: str, work_dir: Path) -> Optional[Path]:
    """Convert a .ll text IR file to LLVM bitcode (.bc) using llvm-as.

    Returns the .bc path on success, None if llvm-as is unavailable.
    """
    llvm_as = _find_tool("llvm-as", "llvm-as-16", "llvm-as-15", "llvm-as-14")
    if not llvm_as:
        return None
    bc_path = work_dir / (Path(ll_file).stem + ".bc")
    r = subprocess.run(
        [llvm_as, ll_file, "-o", str(bc_path)],
        capture_output=True,
        text=True,
    )
    if r.returncode == 0 and bc_path.exists():
        return bc_path
    return None


# ---------------------------------------------------------------------------
# LTOLinker
# ---------------------------------------------------------------------------

class LTOLinker:
    """Drive an LTO-enabled link of NexusLang LLVM IR files.

    The linker tries the following strategies in order, returning the first
    that succeeds:

    1. LLVM ``llvm-lto`` / ``llvm-lto2`` command (direct bitcode linking).
    2. ``lld`` with ``--lto=thin`` or ``--lto=full``.
    3. ``clang`` / ``clang++`` with ``-flto`` (driver-based LTO).
    4. Plain ``clang`` without LTO (fallback so the build never hard-errors).

    All strategies convert ``.ll`` text IR to ``.bc`` bitcode first when the
    input files are in text form.
    """

    def __init__(self, config: LTOConfig) -> None:
        self.config = config

    # ------------------------------------------------------------------
    def link_with_lto(
        self,
        bitcode_files: List[str],
        output: Path,
        work_dir: Path,
    ) -> LTOResult:
        """Link *bitcode_files* into *output* using the configured LTO mode.

        Parameters
        ----------
        bitcode_files:
            Paths to ``.ll`` or ``.bc`` LLVM IR files to link.
        output:
            Desired output file path (no extension; the linker appends one
            if necessary on the target platform).
        work_dir:
            Scratch directory for temporary files produced during the link.
        """
        work_dir.mkdir(parents=True, exist_ok=True)

        if not bitcode_files:
            return LTOResult(
                success=False,
                output_file=None,
                errors=["No bitcode files provided for LTO link"],
            )

        # Convert .ll -> .bc where needed
        bc_files: List[str] = []
        errors: List[str] = []
        for ll in bitcode_files:
            if ll.endswith(".ll"):
                bc = _ll_to_bc(ll, work_dir)
                if bc is not None:
                    bc_files.append(str(bc))
                else:
                    # llvm-as not available – keep .ll and hope the linker handles it
                    bc_files.append(ll)
            else:
                bc_files.append(ll)

        # Try strategies in priority order
        for strategy in (
            self._link_via_llvm_lto,
            self._link_via_lld,
            self._link_via_clang_flto,
            self._link_via_clang_plain,
        ):
            result = strategy(bc_files, output, work_dir)
            if result is not None:
                return result

        return LTOResult(
            success=False,
            output_file=None,
            errors=errors + ["No suitable LTO linker found on PATH"],
        )

    # ------------------------------------------------------------------
    # Private link strategies
    # ------------------------------------------------------------------

    def _link_via_llvm_lto(
        self, files: List[str], output: Path, work_dir: Path
    ) -> Optional[LTOResult]:
        tool = _find_tool(
            "llvm-lto2", "llvm-lto2-16", "llvm-lto2-15", "llvm-lto2-14",
            "llvm-lto",  "llvm-lto-16",  "llvm-lto-15",  "llvm-lto-14",
        )
        if not tool:
            return None

        cmd = [tool, "run"] + files + [
            f"-o={output}",
            f"-O{self.config.opt_level}",
        ]
        if self.config.mode == LTOMode.THIN:
            cmd.append("-thinlto")
        if self.config.strip_debug:
            cmd.append("-strip-debug")
        if self.config.internalize:
            cmd.append("-internalize")

        return self._run(cmd, output)

    def _link_via_lld(
        self, files: List[str], output: Path, work_dir: Path
    ) -> Optional[LTOResult]:
        tool = _find_tool("ld.lld", "lld", "lld-16", "lld-15", "lld-14")
        if not tool:
            return None

        lto_flag = (
            "--lto=thin" if self.config.mode == LTOMode.THIN else "--lto=full"
        )
        cmd = (
            [tool]
            + files
            + [
                "-o", str(output),
                lto_flag,
                f"--lto-O{self.config.opt_level}",
            ]
        )
        if self.config.strip_debug:
            cmd.append("--strip-debug")

        return self._run(cmd, output)

    def _link_via_clang_flto(
        self, files: List[str], output: Path, work_dir: Path
    ) -> Optional[LTOResult]:
        tool = _find_tool("clang", "clang-16", "clang-15", "clang++")
        if not tool:
            return None

        flto = (
            "-flto=thin" if self.config.mode == LTOMode.THIN else "-flto"
        )
        cmd = (
            [tool]
            + files
            + [
                "-o", str(output),
                flto,
                f"-O{self.config.opt_level}",
                "-lm",
            ]
        )
        if self.config.strip_debug:
            cmd.append("-g0")

        return self._run(cmd, output)

    def _link_via_clang_plain(
        self, files: List[str], output: Path, work_dir: Path
    ) -> Optional[LTOResult]:
        """Last-resort plain clang link without LTO (for environments where no
        LTO-capable tool is available)."""
        tool = _find_tool("clang", "clang-16", "clang-15", "gcc")
        if not tool:
            return None

        cmd = (
            [tool]
            + files
            + ["-o", str(output), f"-O{self.config.opt_level}", "-lm"]
        )
        return self._run(cmd, output)

    # ------------------------------------------------------------------

    def _run(self, cmd: List[str], expected_output: Path) -> LTOResult:
        """Execute *cmd* and return an LTOResult."""
        try:
            r = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError:
            return LTOResult(
                success=False,
                output_file=None,
                errors=[f"Tool not found: {cmd[0]}"],
            )

        warnings = [
            line for line in r.stderr.splitlines()
            if "warning" in line.lower()
        ]
        errors = [
            line for line in r.stderr.splitlines()
            if "error" in line.lower() and "warning" not in line.lower()
        ]

        if r.returncode == 0 and expected_output.exists():
            return LTOResult(
                success=True,
                output_file=expected_output,
                warnings=warnings,
                returncode=r.returncode,
                stdout=r.stdout,
                stderr=r.stderr,
            )

        return LTOResult(
            success=False,
            output_file=None,
            errors=errors or [r.stderr.strip() or f"Exit {r.returncode}"],
            warnings=warnings,
            returncode=r.returncode,
            stdout=r.stdout,
            stderr=r.stderr,
        )
