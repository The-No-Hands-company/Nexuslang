"""
NLPL Cross-Compilation Support

Provides target triple parsing/construction, toolchain detection, and
cross-compilation orchestration for common NLPL target architectures.

Supported target families:
    x86_64-linux-gnu       64-bit Linux (desktop, server)
    aarch64-linux-gnu      64-bit ARM Linux (Raspberry Pi 4+, servers)
    arm-linux-gnueabihf    32-bit ARM Linux (hard float)
    riscv64-linux-gnu      RISC-V 64-bit Linux
    riscv32-none-elf       RISC-V 32-bit bare-metal
    arm-none-eabi          Bare-metal ARM (embedded MCUs)
    wasm32-unknown-wasi    WebAssembly (WASI runtime)
    wasm32-unknown-unknown WebAssembly (no OS — browser/custom)
    x86_64-windows-gnu     64-bit Windows via MinGW
    x86_64-windows-msvc    64-bit Windows MSVC ABI (requires MSVC sysroot)
    aarch64-apple-darwin   Apple Silicon macOS
"""

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class TargetArch(Enum):
    """Processor architecture."""
    X86_64   = "x86_64"
    AARCH64  = "aarch64"
    ARM      = "arm"
    RISCV32  = "riscv32"
    RISCV64  = "riscv64"
    WASM32   = "wasm32"
    WASM64   = "wasm64"

    @classmethod
    def from_str(cls, s: str) -> "TargetArch":
        s = s.lower()
        for member in cls:
            if member.value == s:
                return member
        aliases = {
            "x86-64": cls.X86_64,
            "amd64": cls.X86_64,
            "arm64": cls.AARCH64,
        }
        if s in aliases:
            return aliases[s]
        raise ValueError(f"Unknown architecture: {s!r}")


class TargetOS(Enum):
    """Operating system / execution environment."""
    LINUX   = "linux"
    WINDOWS = "windows"
    MACOS   = "darwin"
    NONE    = "none"   # bare-metal
    WASI    = "wasi"   # WebAssembly System Interface
    UNKNOWN = "unknown"

    @classmethod
    def from_str(cls, s: str) -> "TargetOS":
        s = s.lower()
        for member in cls:
            if member.value == s:
                return member
        aliases = {
            "win32": cls.WINDOWS,
            "win64": cls.WINDOWS,
            "macos": cls.MACOS,
        }
        if s in aliases:
            return aliases[s]
        return cls.UNKNOWN


class TargetABI(Enum):
    """ABI / environment component of a triple."""
    GNU         = "gnu"
    GNU_EABI    = "gnueabi"
    GNU_EABIHF  = "gnueabihf"
    MUSL        = "musl"
    MSVC        = "msvc"
    ELF         = "elf"   # bare-metal
    EABI        = "eabi"  # ARM embedded
    NONE        = "none"
    UNKNOWN     = "unknown"

    @classmethod
    def from_str(cls, s: str) -> "TargetABI":
        s = s.lower()
        for member in cls:
            if member.value == s:
                return member
        return cls.UNKNOWN


# ---------------------------------------------------------------------------
# TargetTriple
# ---------------------------------------------------------------------------

@dataclass
class TargetTriple:
    """
    LLVM-style target triple: arch-vendor-os(-abi).

    Examples::

        TargetTriple.parse("x86_64-unknown-linux-gnu")
        TargetTriple.parse("aarch64-unknown-linux-gnu")
        TargetTriple.parse("wasm32-unknown-wasi")
        TargetTriple.parse("arm-none-eabi")
    """
    arch:   TargetArch
    vendor: str        # "unknown", "pc", "apple", "none", …
    os:     TargetOS
    abi:    TargetABI

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        has_abi = self.abi not in (TargetABI.NONE, TargetABI.UNKNOWN)

        # Bare-metal with vendor="none": collapses to arch-none-abi
        # (e.g. arm-none-eabi, riscv32-none-elf)
        if self.os == TargetOS.NONE and self.vendor == "none" and has_abi:
            return f"{self.arch.value}-none-{self.abi.value}"

        # Standard arch-vendor-os[-abi]
        base = f"{self.arch.value}-{self.vendor}-{self.os.value}"
        if has_abi:
            base += f"-{self.abi.value}"
        return base

    # ------------------------------------------------------------------

    @classmethod
    def parse(cls, triple: str) -> "TargetTriple":
        """
        Parse an LLVM-style target triple string.

        Accepts 3- or 4-component triples.  Unknown components are
        mapped to the UNKNOWN/NONE enum members rather than raising.

        Args:
            triple: e.g. ``"x86_64-unknown-linux-gnu"``

        Returns:
            TargetTriple instance.

        Raises:
            ValueError: If fewer than 2 components are found.
        """
        parts = triple.strip().split("-")
        if len(parts) < 2:
            raise ValueError(f"Invalid target triple: {triple!r}")

        arch = TargetArch.from_str(parts[0])

        if len(parts) == 2:
            # e.g. "arm-none"
            vendor = "none"
            os_str = parts[1]
            abi_str = "none"
        elif len(parts) == 3:
            # e.g. "wasm32-unknown-wasi"  OR  "arm-none-eabi"
            vendor = parts[1]
            os_str = parts[2]
            abi_str = "none"

            # Detect bare-metal arch-none-abi pattern:
            # if the third component is not a known OS but IS a known ABI,
            # treat it as the ABI with an implicit OS of "none".
            parsed_os = TargetOS.from_str(os_str)
            if parsed_os == TargetOS.UNKNOWN:
                abi_candidate = TargetABI.from_str(os_str)
                if abi_candidate != TargetABI.UNKNOWN:
                    abi_str = os_str
                    os_str = "none"
        else:
            # 4+ component: arch-vendor-os-abi
            vendor = parts[1]
            os_str = parts[2]
            abi_str = "-".join(parts[3:])

        return cls(
            arch=arch,
            vendor=vendor,
            os=TargetOS.from_str(os_str),
            abi=TargetABI.from_str(abi_str),
        )

    # ------------------------------------------------------------------

    @property
    def is_embedded(self) -> bool:
        """True for bare-metal / embedded targets (no OS)."""
        return self.os in (TargetOS.NONE, TargetOS.UNKNOWN) and self.arch not in (
            TargetArch.WASM32, TargetArch.WASM64
        )

    @property
    def is_wasm(self) -> bool:
        """True for WebAssembly targets."""
        return self.arch in (TargetArch.WASM32, TargetArch.WASM64)

    @property
    def is_linux(self) -> bool:
        return self.os == TargetOS.LINUX

    @property
    def is_windows(self) -> bool:
        return self.os == TargetOS.WINDOWS

    @property
    def pointer_width(self) -> int:
        """Address size in bits (32 or 64)."""
        if self.arch in (TargetArch.RISCV32, TargetArch.ARM, TargetArch.WASM32):
            return 32
        return 64


# ---------------------------------------------------------------------------
# Well-known presets
# ---------------------------------------------------------------------------

KNOWN_TARGETS: Dict[str, TargetTriple] = {
    triple_str: TargetTriple.parse(triple_str)
    for triple_str in [
        "x86_64-unknown-linux-gnu",
        "aarch64-unknown-linux-gnu",
        "arm-unknown-linux-gnueabihf",
        "riscv64-unknown-linux-gnu",
        "riscv32-unknown-none-elf",
        "arm-none-eabi",
        "wasm32-unknown-wasi",
        "wasm32-unknown-unknown",
        "x86_64-pc-windows-gnu",
        "aarch64-apple-darwin",
    ]
}


# ---------------------------------------------------------------------------
# Toolchain detection
# ---------------------------------------------------------------------------

@dataclass
class ToolchainInfo:
    """
    Describes a cross-compilation toolchain for a specific target.

    Attributes:
        target: The target triple this toolchain targets.
        clang: Path to clang/clang++ (preferred over GCC cross-toolchain).
        gcc: Path to a target-specific GCC (e.g. aarch64-linux-gnu-gcc).
        linker: Path to lld or target ld.
        ar: Path to llvm-ar or target ar.
        sysroot: Path to the target sysroot (headers + libraries).
        objcopy: Path to llvm-objcopy or target objcopy.
        strip_tool: Path to llvm-strip or target strip.
        wasm_pack: Path to wasm-pack (WASM targets only).
    """
    target: TargetTriple
    clang:     Optional[Path] = None
    gcc:       Optional[Path] = None
    linker:    Optional[Path] = None
    ar:        Optional[Path] = None
    sysroot:   Optional[Path] = None
    objcopy:   Optional[Path] = None
    strip_tool: Optional[Path] = None
    wasm_pack:  Optional[Path] = None

    @property
    def compiler(self) -> Optional[Path]:
        """Return clang if available, else gcc."""
        return self.clang or self.gcc

    @property
    def is_complete(self) -> bool:
        """True if at least a compiler and linker were found."""
        return self.compiler is not None


class ToolchainDetector:
    """
    Detects available cross-compilation toolchains on the host.

    Detection strategy:
    1. Prefer clang with ``--target=<triple>`` (unified toolchain).
    2. Fall back to target-prefixed GCC (``aarch64-linux-gnu-gcc``).
    3. Detect sysroot from common distribution paths.
    """

    # Common sysroot search paths per arch/os
    _SYSROOT_HINTS: Dict[str, List[str]] = {
        "aarch64-linux": [
            "/usr/aarch64-linux-gnu",
            "/usr/lib/aarch64-linux-gnu",
        ],
        "arm-linux":  ["/usr/arm-linux-gnueabihf"],
        "riscv64-linux": ["/usr/riscv64-linux-gnu"],
        "arm-none":   [
            "/usr/lib/arm-none-eabi",
            "/usr/arm-none-eabi",
        ],
    }

    def detect(self, target: TargetTriple) -> ToolchainInfo:
        """
        Detect the cross-compilation toolchain for *target* on this host.

        Returns:
            ToolchainInfo (may have None fields if tools not found).
        """
        info = ToolchainInfo(target=target)
        triple_str = str(target)

        # 1. clang with --target flag
        clang = shutil.which("clang") or shutil.which("clang-18") or shutil.which("clang-17")
        if clang and self._clang_supports_target(Path(clang), triple_str):
            info.clang = Path(clang)

        # 2. target-prefixed GCC
        gcc_name = f"{triple_str}-gcc"
        gcc = shutil.which(gcc_name)
        if gcc:
            info.gcc = Path(gcc)

        # 3. Linker — prefer lld
        lld = shutil.which("lld") or shutil.which("ld.lld")
        if lld:
            info.linker = Path(lld)
        else:
            ld = shutil.which(f"{triple_str}-ld")
            if ld:
                info.linker = Path(ld)

        # 4. ar
        ar = shutil.which("llvm-ar") or shutil.which(f"{triple_str}-ar")
        if ar:
            info.ar = Path(ar)

        # 5. objcopy / strip
        objcopy = shutil.which("llvm-objcopy") or shutil.which(f"{triple_str}-objcopy")
        if objcopy:
            info.objcopy = Path(objcopy)

        strip = shutil.which("llvm-strip") or shutil.which(f"{triple_str}-strip")
        if strip:
            info.strip_tool = Path(strip)

        # 6. Sysroot
        info.sysroot = self._find_sysroot(target)

        # 7. wasm-pack (WASM only)
        if target.is_wasm:
            wp = shutil.which("wasm-pack")
            if wp:
                info.wasm_pack = Path(wp)

        return info

    def list_available(self) -> List[ToolchainInfo]:
        """
        Return toolchain info for all well-known targets that have at least
        a compiler available on this host.
        """
        results = []
        for target in KNOWN_TARGETS.values():
            info = self.detect(target)
            if info.is_complete:
                results.append(info)
        return results

    # ------------------------------------------------------------------

    @staticmethod
    def _clang_supports_target(clang: Path, triple: str) -> bool:
        """Quick probe: clang --target=<triple> --print-target-triple."""
        try:
            proc = subprocess.run(
                [str(clang), f"--target={triple}", "-print-target-triple"],
                capture_output=True, text=True, timeout=5,
            )
            return proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    def _find_sysroot(self, target: TargetTriple) -> Optional[Path]:
        """Search well-known distribution sysroot paths."""
        key = f"{target.arch.value}-{target.os.value}"
        for hint_key, paths in self._SYSROOT_HINTS.items():
            if hint_key in key:
                for p in paths:
                    sysroot = Path(p)
                    if sysroot.exists():
                        return sysroot
        return None


# ---------------------------------------------------------------------------
# CrossCompiler
# ---------------------------------------------------------------------------

@dataclass
class CrossCompileResult:
    """Result of a cross-compilation operation."""
    success: bool
    output_file: Optional[Path] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    command: List[str] = field(default_factory=list)


class CrossCompiler:
    """
    Drives cross-compilation for a specific target toolchain.

    Wraps the detected toolchain to provide a unified interface for
    compiling NLPL-generated C/LLVM IR to target native code.

    Args:
        toolchain: Detected ToolchainInfo for the target.
        verbose: Print invoked commands.
    """

    def __init__(
        self,
        toolchain: ToolchainInfo,
        verbose: bool = False,
    ) -> None:
        self.toolchain = toolchain
        self.verbose = verbose

    # ------------------------------------------------------------------
    # Flag builders
    # ------------------------------------------------------------------

    def get_compiler_flags(self) -> List[str]:
        """
        Return the flags needed to cross-compile with clang.

        Includes ``--target``, ``--sysroot``, and ABI flags.
        """
        flags: List[str] = []
        triple = self.toolchain.target

        if self.toolchain.clang:
            flags.append(f"--target={triple}")

        if self.toolchain.sysroot:
            flags.append(f"--sysroot={self.toolchain.sysroot}")

        if self.toolchain.linker:
            flags.append(f"-fuse-ld={self.toolchain.linker}")

        # ABI-specific flags
        if triple.arch == TargetArch.ARM:
            if triple.abi == TargetABI.GNU_EABIHF:
                flags.extend(["-march=armv7-a", "-mfpu=neon-vfpv4", "-mfloat-abi=hard"])
            else:
                flags.extend(["-march=armv7-a", "-mfloat-abi=soft"])

        if triple.is_wasm:
            flags.extend([
                "-nostdlib",
                "--no-standard-libraries",
            ])
            if triple.os == TargetOS.WASI:
                wasi_sdk = self._find_wasi_sdk()
                if wasi_sdk:
                    flags.append(f"--sysroot={wasi_sdk}")

        if triple.is_embedded:
            flags.extend(["-nostdlib", "-fno-exceptions", "-fno-rtti"])

        return flags

    def get_linker_flags(self) -> List[str]:
        """Extra flags for the link step."""
        flags: List[str] = []
        triple = self.toolchain.target
        if triple.is_wasm:
            flags.extend([
                "-Wl,--export-dynamic",
                "-Wl,--no-entry",
            ])
        if triple.is_embedded:
            flags.append("-nostartfiles")
        return flags

    # ------------------------------------------------------------------
    # Compilation
    # ------------------------------------------------------------------

    def compile(
        self,
        source: Path,
        output: Path,
        extra_args: Optional[List[str]] = None,
    ) -> CrossCompileResult:
        """
        Compile a single source file to the target.

        Args:
            source: Input source file (.c, .ll, .bc).
            output: Output object file.
            extra_args: Additional flags (optimization, etc.).

        Returns:
            CrossCompileResult.
        """
        compiler = self.toolchain.compiler
        if not compiler:
            return CrossCompileResult(
                success=False,
                errors=[
                    f"No compiler found for target {self.toolchain.target}"
                ],
            )

        cmd = (
            [str(compiler)]
            + self.get_compiler_flags()
            + (extra_args or [])
            + ["-c", str(source), "-o", str(output)]
        )
        return self._run(cmd, output)

    def link(
        self,
        objects: List[Path],
        output: Path,
        extra_args: Optional[List[str]] = None,
    ) -> CrossCompileResult:
        """
        Link object files into a target executable or library.

        Args:
            objects: Object files to link.
            output: Output executable/library path.
            extra_args: Additional flags.

        Returns:
            CrossCompileResult.
        """
        compiler = self.toolchain.compiler
        if not compiler:
            return CrossCompileResult(
                success=False,
                errors=[
                    f"No linker found for target {self.toolchain.target}"
                ],
            )

        cmd = (
            [str(compiler)]
            + self.get_compiler_flags()
            + self.get_linker_flags()
            + (extra_args or [])
            + [str(o) for o in objects]
            + ["-o", str(output)]
        )
        return self._run(cmd, output)

    def compile_and_link(
        self,
        sources: List[Path],
        output: Path,
        extra_args: Optional[List[str]] = None,
    ) -> CrossCompileResult:
        """Convenience: compile sources and link in one clang invocation."""
        compiler = self.toolchain.compiler
        if not compiler:
            return CrossCompileResult(
                success=False,
                errors=[f"No compiler for target {self.toolchain.target}"],
            )

        cmd = (
            [str(compiler)]
            + self.get_compiler_flags()
            + self.get_linker_flags()
            + (extra_args or [])
            + [str(s) for s in sources]
            + ["-o", str(output)]
        )
        return self._run(cmd, output)

    # ------------------------------------------------------------------

    def _run(self, cmd: List[str], output: Path) -> CrossCompileResult:
        if self.verbose:
            print(f"  CC: {' '.join(cmd)}")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            errors: List[str] = []
            warnings: List[str] = []
            for line in (proc.stderr or "").splitlines():
                if "error" in line.lower():
                    errors.append(line)
                elif "warning" in line.lower():
                    warnings.append(line)
            return CrossCompileResult(
                success=proc.returncode == 0,
                output_file=output if proc.returncode == 0 else None,
                errors=errors,
                warnings=warnings,
                command=cmd,
            )
        except OSError as exc:
            return CrossCompileResult(
                success=False,
                errors=[f"Cannot execute {cmd[0]}: {exc}"],
                command=cmd,
            )

    @staticmethod
    def _find_wasi_sdk() -> Optional[Path]:
        """Locate WASI SDK sysroot."""
        candidates = [
            Path("/opt/wasi-sdk"),
            Path(os.environ.get("WASI_SDK_PATH", "/nonexistent")),
        ]
        for p in candidates:
            sysroot = p / "share" / "wasi-sysroot"
            if sysroot.exists():
                return sysroot
        return None


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def get_cross_compiler(
    triple: str,
    verbose: bool = False,
) -> Tuple["CrossCompiler", ToolchainInfo]:
    """
    Parse a target triple string, detect the toolchain, and return a
    ready-to-use CrossCompiler.

    Args:
        triple: Target triple string (e.g. ``"aarch64-unknown-linux-gnu"``).
        verbose: Enable verbose output.

    Returns:
        (CrossCompiler, ToolchainInfo) tuple.

    Example::

        cc, info = get_cross_compiler("aarch64-unknown-linux-gnu")
        if info.is_complete:
            result = cc.compile(Path("main.c"), Path("build/main.o"))
    """
    target = TargetTriple.parse(triple)
    detector = ToolchainDetector()
    toolchain = detector.detect(target)
    compiler = CrossCompiler(toolchain, verbose=verbose)
    return compiler, toolchain


from typing import Tuple  # noqa: E402
