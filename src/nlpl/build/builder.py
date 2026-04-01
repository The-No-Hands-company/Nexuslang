"""
NLPL Build System

Orchestrates compilation of NLPL projects with dependency resolution,
incremental builds, parallel compilation, LTO, and cross-compilation.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Set
from dataclasses import dataclass

from .project import Project
from .cache import BuildCache
from .parallel import ParallelCompiler, CompilationTask, build_tasks_from_sources
from .lto import LTOLinker, LTOConfig, LTOMode, LTOResult
from .cross import CrossCompiler, ToolchainDetector, TargetTriple, get_cross_compiler


@dataclass
class BuildResult:
    """Result of a build operation."""
    success: bool
    output_file: Optional[Path] = None
    errors: List[str] = None
    warnings: List[str] = None
    build_time: float = 0.0
    files_compiled: int = 0
    files_cached: int = 0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class Builder:
    """
    NLPL project builder.

    Handles compilation with incremental builds, dependency resolution,
    build caching, parallel compilation, LTO, and cross-compilation.
    """

    def __init__(
        self,
        project: Project,
        verbose: bool = False,
        jobs: Optional[int] = None,
    ):
        self.project = project
        self.verbose = verbose
        self.cache = BuildCache(project.get_cache_dir())
        self.compiler_path = self._find_compiler()
        # --jobs CLI override wins; fall back to project config; 0 = auto
        self._jobs = jobs if jobs is not None else project.build.parallel_jobs
    
    def _find_compiler(self) -> Path:
        """Find the NLPL compiler executable."""
        # Check for nlplc_llvm.py in current directory
        candidates = [
            Path("nlplc_llvm.py"),
            Path(__file__).parent.parent.parent.parent / "nlplc_llvm.py",
            Path.cwd() / "nlplc_llvm.py",
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        raise FileNotFoundError("NLPL compiler (nlplc_llvm.py) not found")
    
    def _prepare_build_flags(
        self,
        release: bool,
    ):
        """Compute (opt_level, lto_mode, use_lto, cross_flags, base_flags) for the build.

        Returns:
            Tuple of (opt_level, lto_mode, use_lto, base_flags, error)
            where error is a BuildResult on failure or None on success.
        """
        opt_level = 3 if release else self.project.build.optimization_level

        lto_str = self.project.build.lto
        if release and lto_str == "disabled":
            lto_str = "thin"
        lto_mode = {
            "thin": LTOMode.THIN,
            "full": LTOMode.FULL,
        }.get(lto_str, LTOMode.DISABLED)
        use_lto = lto_mode != LTOMode.DISABLED

        cross_flags: List[str] = []
        if self.project.build.target_triple:
            _, toolchain = get_cross_compiler(
                self.project.build.target_triple,
                verbose=self.verbose,
            )
            if toolchain.is_complete:
                from .cross import CrossCompiler as _CC
                cc = _CC(toolchain, verbose=self.verbose)
                cross_flags = cc.get_compiler_flags()
                if self.verbose:
                    print(f"Cross-compiling for {self.project.build.target_triple}")
            else:
                error = BuildResult(
                    success=False,
                    errors=[
                        f"No toolchain found for target "
                        f"{self.project.build.target_triple}. "
                        f"Install clang or a cross-gcc for that target."
                    ],
                )
                return opt_level, lto_mode, use_lto, [], error

        base_flags: List[str] = []
        if opt_level > 0:
            base_flags.append(f"-O{opt_level}")
        if self.project.build.debug_info and not release:
            base_flags.append("-g")
        if cross_flags:
            base_flags.extend(cross_flags)
        if use_lto:
            lto_cfg = LTOConfig(mode=lto_mode, opt_level=min(opt_level, 3))
            lto_linker = LTOLinker(lto_cfg)
            base_flags.extend(lto_linker.emit_bitcode_flags())

        return opt_level, lto_mode, use_lto, base_flags, None

    def build(self, release: bool = False, clean: bool = False) -> BuildResult:
        """
        Build the project.

        When ``parallel_jobs != 1`` and there are multiple source files,
        compiles them concurrently (each to a separate object file) using
        the configured thread pool, then links the results.

        When ``lto`` is ``"thin"`` or ``"full"``, the compiler is invoked
        with ``-emit-llvm`` and the LTO pipeline (llvm-link → opt → llc)
        handles the final link step.

        When ``target_triple`` is set in the build config, the detected
        cross-compilation toolchain flags (``--target``, ``--sysroot``, …)
        are injected into every compiler invocation.

        Args:
            release: Build with maximum optimizations (overrides project
                     ``optimization_level`` → 3 and enables LTO thin if
                     ``lto`` is not explicitly set to ``"full"``).
            clean:   Ignore build cache and recompile all files.

        Returns:
            BuildResult with compilation status and diagnostics.
        """
        import time
        start_time = time.time()

        if clean:
            self.clean()

        # --- Resolve entry point -----------------------------------------
        main_file = self.project.get_main_file()
        if not main_file.exists():
            return BuildResult(
                success=False,
                errors=[f"Main file not found: {main_file}"],
            )

        # --- Source / incremental ----------------------------------------
        source_files = self.project.get_source_files()
        if self.project.build.incremental and not clean:
            files_to_compile = self.cache.get_files_to_rebuild(source_files)
        else:
            files_to_compile = source_files

        # --- Output dir / name -------------------------------------------
        output_dir = self.project.get_output_dir()
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / self.project.name

        # --- Optimization level, LTO, cross-compilation, base flags ------
        _opt_level, lto_mode, use_lto, base_flags, flag_error = self._prepare_build_flags(release)
        if flag_error is not None:
            return flag_error

        # --- Decide: parallel or serial ----------------------------------
        effective_jobs = self._jobs
        use_parallel = (
            effective_jobs != 1
            and len(files_to_compile) > 1
        )

        if self.verbose:
            print(f"Building {self.project.name} v{self.project.version}")
            print(f"  Files: {len(files_to_compile)}/{len(source_files)} to compile")
            if use_parallel:
                workers = effective_jobs or os.cpu_count() or 4
                print(f"  Parallel: {workers} workers")
            if use_lto:
                print(f"  LTO: {lto_mode.value}")

        # --- Compile step ------------------------------------------------
        try:
            if use_parallel:
                result = self._build_parallel(
                    files_to_compile,
                    output_file,
                    output_dir,
                    base_flags,
                    lto_mode,
                    start_time,
                    len(source_files),
                )
            else:
                result = self._build_serial(
                    main_file,
                    output_file,
                    base_flags,
                    lto_mode,
                    output_dir,
                    files_to_compile,
                    len(source_files),
                    start_time,
                )

            # --- Update incremental cache on success --------------------
            if result.success:
                for f in files_to_compile:
                    self.cache.update(f)
                self.cache.save()

            if self.verbose:
                status = "Build successful" if result.success else "Build failed"
                print(f"  {status} in {result.build_time:.2f}s")
                if result.success:
                    print(f"  Output: {result.output_file}")

            return result

        except Exception as exc:
            return BuildResult(
                success=False,
                errors=[f"Build error: {exc}"],
                build_time=time.time() - start_time,
            )

    # ------------------------------------------------------------------
    # Internal build paths
    # ------------------------------------------------------------------

    def _build_serial(
        self,
        main_file: Path,
        output_file: Path,
        base_flags: List[str],
        lto_mode: LTOMode,
        output_dir: Path,
        files_compiled: List[Path],
        total_files: int,
        start_time: float,
    ) -> BuildResult:
        """Original single-invocation build path."""
        import time

        args = [sys.executable, str(self.compiler_path)]
        args.append(str(main_file))

        if lto_mode != LTOMode.DISABLED:
            # Emit bitcode; LTO pipeline links afterwards
            bc_output = output_dir / (output_file.name + ".bc")
            args.extend(["-o", str(bc_output)])
        else:
            args.extend(["-o", str(output_file)])

        args.extend(base_flags)

        if self.verbose:
            print(f"  Command: {' '.join(args)}")

        proc = subprocess.run(args, capture_output=True, text=True,
                              cwd=self.project.root_dir)
        errors, warnings = self._parse_output(proc.stderr)
        success = proc.returncode == 0

        if success and lto_mode != LTOMode.DISABLED:
            bc_output = output_dir / (output_file.name + ".bc")
            lto_cfg = LTOConfig(mode=lto_mode)
            lto_result = LTOLinker(lto_cfg).link_with_lto(
                [bc_output], output_file, work_dir=output_dir
            )
            errors.extend(lto_result.errors)
            warnings.extend(lto_result.warnings)
            success = lto_result.success

        return BuildResult(
            success=success,
            output_file=output_file if success else None,
            errors=errors,
            warnings=warnings,
            build_time=time.time() - start_time,
            files_compiled=len(files_compiled),
            files_cached=total_files - len(files_compiled),
        )

    def _build_parallel(
        self,
        files_to_compile: List[Path],
        output_file: Path,
        output_dir: Path,
        base_flags: List[str],
        lto_mode: LTOMode,
        start_time: float,
        total_files: int,
    ) -> BuildResult:
        """
        Parallel compilation path.

        Each source file is compiled to a separate object (or bitcode)
        file, then all outputs are linked together.
        """
        import time

        obj_dir = output_dir / "_objects"
        obj_dir.mkdir(exist_ok=True)

        # Add compile-only flag so sources produce .o / .bc files
        compile_flags = base_flags + ["-c"]

        tasks = build_tasks_from_sources(
            source_files=files_to_compile,
            output_dir=obj_dir,
            compiler_path=self.compiler_path,
            compiler_flags=compile_flags,
        )

        workers = self._jobs if self._jobs and self._jobs > 0 else None
        compiler = ParallelCompiler(max_workers=workers, verbose=self.verbose)
        task_results = compiler.compile_all(tasks)

        errors: List[str] = []
        warnings: List[str] = []
        for tr in task_results:
            errors.extend(tr.errors)
            warnings.extend(tr.warnings)

        all_ok = all(tr.success for tr in task_results)
        if not all_ok:
            return BuildResult(
                success=False,
                errors=errors,
                warnings=warnings,
                build_time=time.time() - start_time,
                files_compiled=sum(1 for tr in task_results if tr.success),
                files_cached=total_files - len(files_to_compile),
            )

        # --- Link step ---------------------------------------------------
        obj_files = [tr.task.output_file for tr in task_results]

        if lto_mode != LTOMode.DISABLED:
            lto_cfg = LTOConfig(mode=lto_mode)
            lto_result = LTOLinker(lto_cfg).link_with_lto(
                obj_files, output_file, work_dir=output_dir
            )
            errors.extend(lto_result.errors)
            warnings.extend(lto_result.warnings)
            link_ok = lto_result.success
        else:
            # Simple link: re-invoke the compiler as a linker
            link_args = (
                [sys.executable, str(self.compiler_path)]
                + [str(o) for o in obj_files]
                + ["-o", str(output_file)]
            )
            proc = subprocess.run(link_args, capture_output=True, text=True,
                                  cwd=self.project.root_dir)
            link_errs, link_warns = self._parse_output(proc.stderr)
            errors.extend(link_errs)
            warnings.extend(link_warns)
            link_ok = proc.returncode == 0

        return BuildResult(
            success=link_ok,
            output_file=output_file if link_ok else None,
            errors=errors,
            warnings=warnings,
            build_time=time.time() - start_time,
            files_compiled=len(files_to_compile),
            files_cached=total_files - len(files_to_compile),
        )

    @staticmethod
    def _parse_output(stderr: str):
        """Classify stderr lines as errors or warnings."""
        errors: List[str] = []
        warnings: List[str] = []
        for line in (stderr or "").splitlines():
            low = line.lower()
            if "error" in low:
                errors.append(line)
            elif "warning" in low:
                warnings.append(line)
        return errors, warnings


    
    def clean(self) -> None:
        """Clean build artifacts and cache."""
        if self.verbose:
            print("Cleaning build artifacts...")
        
        # Clear cache
        self.cache.clear()
        
        # Remove build directory
        output_dir = self.project.get_output_dir()
        if output_dir.exists():
            import shutil
            shutil.rmtree(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        if self.verbose:
            print("✅ Clean complete")
    
    def run(self, args: List[str] = None) -> int:
        """
        Build and run the project.
        
        Args:
            args: Command-line arguments to pass to the program
        
        Returns:
            Exit code of the program
        """
        # Build first
        result = self.build()
        if not result.success:
            print("Build failed:")
            for error in result.errors:
                print(f"  {error}")
            return 1
        
        # Run the executable
        run_args = [str(result.output_file)]
        if args:
            run_args.extend(args)
        
        if self.verbose:
            print(f"\nRunning: {' '.join(run_args)}")
            print("-" * 40)
        
        try:
            proc = subprocess.run(run_args, cwd=self.project.root_dir)
            return proc.returncode
        except Exception as e:
            print(f"Runtime error: {e}")
            return 1
    
    def check(self) -> BuildResult:
        """
        Check the project for errors without producing output.
        
        Similar to `cargo check` - faster than full build.
        """
        # For now, just do a regular build
        # In the future, could add a check-only mode to the compiler
        return self.build()
    
    def test(self) -> int:
        """Run project tests."""
        test_dir = self.project.root_dir / "tests"
        if not test_dir.exists():
            print("No tests directory found")
            return 0
        
        test_files = list(test_dir.glob("*.nlpl"))
        if not test_files:
            print("No test files found")
            return 0
        
        print(f"Running {len(test_files)} test(s)...")
        
        passed = 0
        failed = 0
        
        for test_file in test_files:
            print(f"\nTest: {test_file.name}")
            
            # Compile test
            output = self.project.get_output_dir() / f"test_{test_file.stem}"
            args = [
                sys.executable,
                str(self.compiler_path),
                str(test_file),
                "-o",
                str(output)
            ]
            
            result = subprocess.run(args, capture_output=True)
            if result.returncode != 0:
                print(f"  ❌ Compilation failed")
                failed += 1
                continue
            
            # Run test
            result = subprocess.run([str(output)], capture_output=True)
            if result.returncode == 0:
                print(f"  ✅ Passed")
                passed += 1
            else:
                print(f"  ❌ Failed (exit code {result.returncode})")
                failed += 1
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return 0 if failed == 0 else 1
