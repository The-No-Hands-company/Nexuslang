"""
NLPL Parallel Compilation Engine

Compiles independent source files concurrently using a thread pool,
respecting the dependency order established by the incremental tracker.
"""

import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict, deque
import threading
import time


@dataclass
class CompilationTask:
    """A single file compilation task.

    Attributes:
        source_file: NLPL source file path.
        output_file: Expected output object/IR path.
        compiler_args: Full argument list to invoke the compiler.
        dependencies: Source files that must be compiled before this one.
    """
    source_file: Path
    output_file: Path
    compiler_args: List[str]
    dependencies: List[Path] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.source_file)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CompilationTask):
            return NotImplemented
        return self.source_file == other.source_file


@dataclass
class TaskResult:
    """Result of compiling a single file."""
    task: CompilationTask
    success: bool
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DependencyGraph:
    """
    Directed acyclic graph of compilation tasks.

    Provides topological layering: each layer is a set of tasks whose
    dependencies have all been satisfied, so the entire layer can be
    compiled concurrently.
    """

    def __init__(self) -> None:
        self._tasks: Dict[Path, CompilationTask] = {}
        # edges: source -> set of paths it depends on
        self._deps: Dict[Path, Set[Path]] = defaultdict(set)
        # reverse edges: source -> set of paths that depend on it
        self._rdeps: Dict[Path, Set[Path]] = defaultdict(set)

    def add_task(self, task: CompilationTask) -> None:
        """Register a task and wire up its dependency edges."""
        self._tasks[task.source_file] = task
        for dep in task.dependencies:
            if dep in self._tasks:
                self._deps[task.source_file].add(dep)
                self._rdeps[dep].add(task.source_file)

    def _in_degrees(self) -> Dict[Path, int]:
        degrees: Dict[Path, int] = {}
        for path in self._tasks:
            # Only count intra-graph deps (ignore deps that aren't tasks)
            degrees[path] = sum(
                1 for d in self._deps[path] if d in self._tasks
            )
        return degrees

    def topological_layers(self) -> List[List[CompilationTask]]:
        """
        Return tasks in dependency order as a list of layers.

        Each layer contains tasks that can be compiled in parallel because
        all of their dependencies belong to earlier layers.

        Raises:
            ValueError: If the dependency graph contains a cycle.
        """
        in_deg = self._in_degrees()
        ready: deque = deque(
            path for path, deg in in_deg.items() if deg == 0
        )
        layers: List[List[CompilationTask]] = []
        processed = 0

        while ready:
            layer = list(ready)
            ready.clear()
            layers.append([self._tasks[p] for p in layer])
            processed += len(layer)

            for path in layer:
                for dependent in self._rdeps[path]:
                    if dependent in in_deg:
                        in_deg[dependent] -= 1
                        if in_deg[dependent] == 0:
                            ready.append(dependent)

        if processed != len(self._tasks):
            cyclic = [
                str(p) for p, d in in_deg.items() if d > 0
            ]
            raise ValueError(
                f"Dependency cycle detected among: {cyclic}"
            )

        return layers

    def task_count(self) -> int:
        return len(self._tasks)


class ParallelCompiler:
    """
    Compiles NLPL source files in parallel.

    Uses a ThreadPoolExecutor to compile independent files concurrently
    while respecting the topological order of the dependency graph.

    Args:
        max_workers: Number of parallel workers. Defaults to CPU count.
        verbose: Print progress messages.
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,
        verbose: bool = False,
    ) -> None:
        import os
        self.max_workers = max_workers or os.cpu_count() or 4
        self.verbose = verbose
        self._lock = threading.Lock()
        self._completed: List[TaskResult] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compile_all(self, tasks: List[CompilationTask]) -> List[TaskResult]:
        """
        Compile all tasks in dependency order, parallelizing each layer.

        Returns:
            TaskResult list in completion order.
        """
        if not tasks:
            return []

        graph = DependencyGraph()
        for task in tasks:
            graph.add_task(task)

        try:
            layers = graph.topological_layers()
        except ValueError as exc:
            return [
                TaskResult(
                    task=t,
                    success=False,
                    errors=[str(exc)],
                )
                for t in tasks
            ]

        self._completed = []
        total = sum(len(layer) for layer in layers)
        compiled = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            for layer_idx, layer in enumerate(layers):
                if self.verbose:
                    print(
                        f"  Compiling layer {layer_idx + 1}/{len(layers)}"
                        f" ({len(layer)} file(s))"
                    )

                futures: Dict[Future, CompilationTask] = {
                    pool.submit(self._compile_one, task): task
                    for task in layer
                }

                failed = False
                for future in as_completed(futures):
                    result = future.result()
                    compiled += 1
                    with self._lock:
                        self._completed.append(result)

                    if not result.success:
                        failed = True
                        if self.verbose:
                            print(
                                f"  ERROR: {result.task.source_file.name}"
                            )
                    else:
                        if self.verbose:
                            print(
                                f"  [{compiled}/{total}] OK"
                                f" {result.task.source_file.name}"
                                f" ({result.duration:.2f}s)"
                            )

                if failed:
                    # Cancel remaining layers on first failure
                    break

        return list(self._completed)

    def compile_independent(
        self, tasks: List[CompilationTask]
    ) -> List[TaskResult]:
        """
        Compile a flat list of tasks with no dependency ordering.

        Useful when the caller has already ensured correct ordering and
        just needs parallel execution.
        """
        if not tasks:
            return []

        results: List[TaskResult] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(self._compile_one, t): t for t in tasks}
            for future in as_completed(futures):
                results.append(future.result())
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compile_one(self, task: CompilationTask) -> TaskResult:
        """Invoke the compiler for a single task."""
        start = time.monotonic()
        try:
            proc = subprocess.run(
                task.compiler_args,
                capture_output=True,
                text=True,
            )
            duration = time.monotonic() - start
            errors: List[str] = []
            warnings: List[str] = []
            for line in (proc.stderr or "").splitlines():
                low = line.lower()
                if "error" in low:
                    errors.append(line)
                elif "warning" in low:
                    warnings.append(line)

            return TaskResult(
                task=task,
                success=proc.returncode == 0,
                stdout=proc.stdout or "",
                stderr=proc.stderr or "",
                duration=duration,
                errors=errors,
                warnings=warnings,
            )
        except OSError as exc:
            return TaskResult(
                task=task,
                success=False,
                duration=time.monotonic() - start,
                errors=[f"Failed to launch compiler: {exc}"],
            )


def build_tasks_from_sources(
    source_files: List[Path],
    output_dir: Path,
    compiler_path: Path,
    compiler_flags: List[str],
    dep_graph: Optional[Dict[Path, Set[Path]]] = None,
) -> List[CompilationTask]:
    """
    Convenience factory: build CompilationTask objects for a list of sources.

    Args:
        source_files: NLPL source files to compile.
        output_dir: Directory for output object/IR files.
        compiler_path: Path to the NLPL compiler executable (nlplc or nlplc_llvm.py).
        compiler_flags: Additional flags (optimization, debug, target, etc.).
        dep_graph: Optional mapping of source file -> set of source files it imports.

    Returns:
        List of CompilationTask objects ready for ParallelCompiler.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks = []
    for src in source_files:
        out = output_dir / (src.stem + ".o")
        deps = list(dep_graph.get(src, set())) if dep_graph else []
        args = [sys.executable, str(compiler_path)] + compiler_flags + [
            str(src), "-o", str(out)
        ]
        tasks.append(CompilationTask(
            source_file=src,
            output_file=out,
            compiler_args=args,
            dependencies=deps,
        ))
    return tasks
