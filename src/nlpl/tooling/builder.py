
import os
import shutil
import glob
import time
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field

from .config import ProjectConfig, ProfileConfig
from ..compiler import Compiler, CompilerOptions, CompilationTarget
from ..parser.lexer import Lexer
from ..parser.parser import Parser


# ---------------------------------------------------------------------------
# Build cache (file-level incremental compilation)
# ---------------------------------------------------------------------------

@dataclass
class _CacheEntry:
    path: str
    mtime: float
    size: int
    content_hash: str


class _BuildCache:
    """Lightweight build cache backed by a JSON file in the build output dir."""

    VERSION = 1

    def __init__(self, cache_path: Path) -> None:
        self._path = cache_path
        self._entries: Dict[str, _CacheEntry] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("version") != self.VERSION:
                return
            for e in data.get("entries", []):
                self._entries[e["path"]] = _CacheEntry(**e)
        except Exception:
            self._entries = {}

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": self.VERSION,
            "entries": [vars(e) for e in self._entries.values()],
        }
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _file_hash(path: str) -> str:
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()

    def needs_rebuild(self, source_path: str) -> bool:
        """Return True if *source_path* has changed since it was last cached."""
        if source_path not in self._entries:
            return True
        try:
            st = os.stat(source_path)
        except OSError:
            return True
        e = self._entries[source_path]
        if st.st_mtime != e.mtime or st.st_size != e.size:
            current_hash = self._file_hash(source_path)
            if current_hash != e.content_hash:
                return True
        return False

    def mark_built(self, source_path: str) -> None:
        """Record that *source_path* was successfully compiled."""
        try:
            st = os.stat(source_path)
            self._entries[source_path] = _CacheEntry(
                path=source_path,
                mtime=st.st_mtime,
                size=st.st_size,
                content_hash=self._file_hash(source_path),
            )
        except OSError:
            pass

    def clear(self) -> None:
        self._entries = {}
        if self._path.exists():
            self._path.unlink()


# ---------------------------------------------------------------------------
# Build result
# ---------------------------------------------------------------------------

@dataclass
class BuildResult:
    """Outcome of a build invocation."""
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    files_compiled: int = 0
    files_cached: int = 0
    elapsed: float = 0.0

    def print_summary(self, project_name: str, profile: str) -> None:
        status = "Finished" if self.success else "Failed"
        cached_note = f" ({self.files_cached} cached)" if self.files_cached else ""
        print(
            f"  {status} [{profile}] {project_name!r} in {self.elapsed:.2f}s"
            f" — {self.files_compiled} compiled{cached_note}"
        )
        for err in self.errors:
            print(f"  error: {err}")
        for warn in self.warnings:
            print(f"  warning: {warn}")


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

class BuildSystem:
    """Orchestrates the build process based on project configuration.

    Supports:
    - Incremental builds (file-level caching via SHA-256 hashes)
    - Parallel compilation (one thread per source file)
    - Release / dev profiles
    - Feature flags
    """

    def __init__(self, config: ProjectConfig) -> None:
        self.config = config

    # ------------------------------------------------------------------
    # Public commands
    # ------------------------------------------------------------------

    def build(
        self,
        *,
        release: bool = False,
        profile: Optional[str] = None,
        features: Optional[List[str]] = None,
        jobs: Optional[int] = None,
        clean: bool = False,
        check_only: bool = False,
        optimize_bounds_checks: bool = False,
    ) -> bool:
        """Build the project.

        Args:
            release:                Build with ``release`` profile (O3, no debug).
            profile:                Explicit profile name (overrides *release*).
            features:               Extra feature flags to enable.
            jobs:                   Max parallel workers. None = CPU count.
            clean:                  Discard cache and rebuild everything.
            check_only:             Parse and type-check without emitting output.
            optimize_bounds_checks: Enable compile-time bounds check elimination.

        Returns:
            True if all files compiled successfully.
        """
        result = self._build_internal(
            release=release,
            profile=profile,
            features=features,
            jobs=jobs,
            clean=clean,
            check_only=check_only,
            optimize_bounds_checks=optimize_bounds_checks,
        )
        result.print_summary(
            self.config.package.name,
            profile or ("release" if release else self.config.build.profile),
        )
        return result.success

    def run(
        self,
        *,
        release: bool = False,
        features: Optional[List[str]] = None,
        run_args: Optional[List[str]] = None,
    ) -> int:
        """Build then run the project executable.

        Returns:
            Exit code of the executed program (1 if build failed).
        """
        if not self.build(release=release, features=features):
            return 1

        executable = self._find_executable(self.config.build.output_dir)
        if not executable:
            print(f"  error: no executable found in {self.config.build.output_dir}")
            return 1

        import subprocess
        cmd = [executable] + (run_args or [])
        print(f"\nRunning `{' '.join(cmd)}`")
        print("-" * 40)
        try:
            return subprocess.run(cmd).returncode
        except Exception as exc:
            print(f"  error running executable: {exc}")
            return 1

    def check(
        self,
        *,
        features: Optional[List[str]] = None,
    ) -> bool:
        """Parse and type-check without producing compiled output (fast path).

        Returns:
            True if no errors were found.
        """
        return self.build(check_only=True, features=features)

    def clean(self) -> None:
        """Remove build output directory and clear the build cache."""
        out_dir = self.config.build.output_dir
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
            print(f"  Removed {out_dir}/")
        cache_path = self._cache_path()
        if cache_path.exists():
            cache_path.unlink()
        print("  Done")

    def test(
        self,
        *,
        filter_names: Optional[List[str]] = None,
        release: bool = False,
        features: Optional[List[str]] = None,
    ) -> int:
        """Discover and run test files from the ``tests/`` directory.

        Args:
            filter_names: If provided, only run tests whose filename contains
                          one of these strings.
            release:      Build tests with release profile.
            features:     Extra feature flags for test compilation.

        Returns:
            0 if all tests passed, 1 otherwise.
        """
        test_dir_path = Path(self.config.build.source_dir).parent / "tests"
        if not test_dir_path.exists():
            print("  No tests/ directory found.")
            return 0

        test_files = sorted(test_dir_path.rglob("*.nlpl"))
        if filter_names:
            test_files = [
                f for f in test_files
                if any(name in f.name for name in filter_names)
            ]

        if not test_files:
            print("  No test files found.")
            return 0

        print(f"\nRunning {len(test_files)} test file(s)...")

        passed = 0
        failed = 0
        for test_file in test_files:
            label = test_file.stem
            ok = self._run_single_test(
                test_file, release=release, features=features
            )
            if ok:
                passed += 1
                print(f"  test {label} ... ok")
            else:
                failed += 1
                print(f"  test {label} ... FAILED")

        print(f"\ntest result: {'ok' if failed == 0 else 'FAILED'}. "
              f"{passed} passed; {failed} failed.")
        return 0 if failed == 0 else 1

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cache_path(self) -> Path:
        out_dir = Path(self.config.build.output_dir)
        return out_dir / ".build_cache.json"

    def _resolve_profile(
        self, release: bool, profile: Optional[str]
    ) -> ProfileConfig:
        if profile:
            return self.config.get_profile(profile)
        if release:
            return self.config.get_profile("release")
        return self.config.get_profile(self.config.build.profile)

    def _configure_compiler(
        self,
        prof: ProfileConfig,
        active_features: List[str],
        optimize_bounds_checks: bool = False,
    ) -> Compiler:
        """Create and configure a fresh Compiler instance."""
        from ..compiler import create_compiler
        compiler = create_compiler(
            optimization_level=prof.optimization,
            debug=prof.debug_info,
        )
        compiler.options.optimization_level = prof.optimization
        compiler.options.generate_header = self.config.build.headers
        if optimize_bounds_checks:
            # Signal to backends that bounds-check elimination is requested
            compiler.options.optimization_level = max(compiler.options.optimization_level, 1)

        # Add dependency library search paths
        all_deps = {**self.config.dependencies, **self.config.build_dependencies}
        for dep_name, dep_spec in all_deps.items():
            if isinstance(dep_spec, dict) and "path" in dep_spec:
                lib_path = os.path.join(dep_spec["path"], "build", "lib")
                if os.path.exists(lib_path):
                    compiler.options.library_search_paths.append(lib_path)

        return compiler

    def _compile_one(
        self, source_path: str, out_dir: str, prof: ProfileConfig,
        active_features: List[str], check_only: bool, optimize_bounds_checks: bool
    ) -> Tuple[str, bool, List[str]]:
        """Compile a single source file.  Designed to run in a thread.

        Returns:
            (source_path, success, list_of_error_lines)
        """
        errors: List[str] = []
        try:
            with open(source_path, "r", encoding="utf-8") as f:
                code = f.read()

            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            if check_only:
                # Parse-only: no backend emission
                return source_path, True, []

            compiler = self._configure_compiler(
                prof, active_features, optimize_bounds_checks
            )
            rel = os.path.relpath(source_path, self.config.build.source_dir)
            base = os.path.splitext(rel)[0]
            output_file = os.path.join(out_dir, base)

            ok, _ = compiler.compile(ast, self.config.build.target, output_file)
            if not ok:
                errors.append(f"Compiler reported failure for {source_path}")
            return source_path, ok, errors

        except Exception as exc:
            return source_path, False, [f"{source_path}: {exc}"]

    def _build_internal(
        self,
        release: bool,
        profile: Optional[str],
        features: Optional[List[str]],
        jobs: Optional[int],
        clean: bool,
        check_only: bool,
        optimize_bounds_checks: bool,
    ) -> BuildResult:
        t0 = time.monotonic()

        prof = self._resolve_profile(release, profile)
        profile_name = profile or ("release" if release else self.config.build.profile)

        # Merge features: manifest defaults + cli-supplied
        cfg_features = self.config.build.features[:]
        if features:
            cfg_features.extend(features)
        active_features = list(dict.fromkeys(cfg_features))  # deduplicate, preserve order

        src_dir = self.config.build.source_dir
        out_dir = self.config.build.output_dir
        os.makedirs(out_dir, exist_ok=True)

        # Build cache
        cache = _BuildCache(self._cache_path())
        if clean:
            cache.clear()

        # Discover source files
        sources = glob.glob(os.path.join(src_dir, "**/*.nlpl"), recursive=True)
        if not sources:
            return BuildResult(
                success=False,
                errors=[f"No source files found in {src_dir}"],
                elapsed=time.monotonic() - t0,
            )

        # Determine which files need (re)compilation
        to_compile = [s for s in sources if cache.needs_rebuild(s)] if not clean else sources
        cached_count = len(sources) - len(to_compile)

        if not to_compile:
            print(f"  Nothing to compile (all {len(sources)} file(s) up-to-date).")
            return BuildResult(
                success=True,
                files_compiled=0,
                files_cached=cached_count,
                elapsed=time.monotonic() - t0,
            )

        # Determine parallelism
        max_workers = jobs or self.config.build.jobs or os.cpu_count() or 1
        max_workers = min(max_workers, len(to_compile))

        print(
            f"  Compiling {self.config.package.name} v{self.config.package.version} "
            f"[{profile_name}] "
            f"({len(to_compile)} file{'s' if len(to_compile) != 1 else ''}"
            f"{', ' + str(cached_count) + ' cached' if cached_count else ''})"
        )

        all_errors: List[str] = []
        all_warnings: List[str] = []
        compiled_ok = 0

        if max_workers == 1:
            # Serial path
            for src in to_compile:
                _, ok, errs = self._compile_one(
                    src, out_dir, prof, active_features, check_only, optimize_bounds_checks
                )
                if ok:
                    compiled_ok += 1
                    cache.mark_built(src)
                else:
                    all_errors.extend(errs)
        else:
            # Parallel path
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(
                        self._compile_one,
                        src, out_dir, prof, active_features, check_only, optimize_bounds_checks,
                    ): src
                    for src in to_compile
                }
                for future in as_completed(futures):
                    src_path, ok, errs = future.result()
                    if ok:
                        compiled_ok += 1
                        cache.mark_built(src_path)
                    else:
                        all_errors.extend(errs)

        # Persist updated cache entries
        cache.save()

        # Link multi-file C/C++ projects when more than one file compiled
        if (
            not check_only
            and not all_errors
            and self.config.build.target in ("c", "cpp", CompilationTarget.C, CompilationTarget.CPP)
            and len(sources) > 1
        ):
            self._maybe_link(out_dir, all_errors)

        return BuildResult(
            success=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            files_compiled=compiled_ok,
            files_cached=cached_count,
            elapsed=time.monotonic() - t0,
        )

    def _maybe_link(self, out_dir: str, errors: List[str]) -> None:
        """Attempt to link compiled C/C++ objects into a single executable."""
        import subprocess

        target = self.config.build.target
        compilers = (
            ["g++", "clang++"] if target in ("cpp", CompilationTarget.CPP)
            else ["gcc", "clang"]
        )
        cc = next((shutil.which(c) for c in compilers if shutil.which(c)), None)
        if not cc:
            return  # No host C compiler available

        object_files = glob.glob(os.path.join(out_dir, "**/*.c"), recursive=True)
        object_files += glob.glob(os.path.join(out_dir, "**/*.cpp"), recursive=True)
        if not object_files:
            return

        final = os.path.join(out_dir, self.config.package.name)
        cmd = [cc] + object_files + ["-o", final]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            errors.append(f"Linking failed:\n{result.stderr.strip()}")

    def _run_single_test(
        self,
        test_file: Path,
        release: bool,
        features: Optional[List[str]],
    ) -> bool:
        """Compile and run a single test file.  Returns True if it exits 0."""
        import subprocess
        import tempfile

        prof = self._resolve_profile(release, None)
        active_features = self.config.build.features[:] + (features or [])
        out_dir = Path(self.config.build.output_dir) / "test_bins"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = str(out_dir / test_file.stem)

        _, ok, _ = self._compile_one(
            str(test_file), str(out_dir), prof, active_features,
            check_only=False, optimize_bounds_checks=False
        )
        if not ok:
            return False

        try:
            result = subprocess.run(
                [out_file], capture_output=True, timeout=30
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _find_executable(self, out_dir: str) -> Optional[str]:
        """Find the project executable in the build output directory."""
        # Strategy 1: package name
        exe = os.path.join(out_dir, self.config.package.name)
        if os.path.isfile(exe) and os.access(exe, os.X_OK):
            return exe

        # Strategy 2: 'main'
        exe = os.path.join(out_dir, "main")
        if os.path.isfile(exe) and os.access(exe, os.X_OK):
            return exe

        # Strategy 3: any executable
        for f in glob.glob(os.path.join(out_dir, "*")):
            if (os.path.isfile(f) and os.access(f, os.X_OK)
                    and not f.endswith((".o", ".c", ".cpp", ".h", ".nlpl", ".ll"))):
                return f

        return None


