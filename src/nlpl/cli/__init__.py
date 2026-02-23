"""NLPL command-line toolchain.

Subcommands
-----------
new       Create a new project in a new directory
init      Initialise a project in the current directory
build     Compile the project
run       Build and execute the project
check     Parse/type-check without producing output
clean     Remove the build output directory
test      Discover and run tests from tests/
coverage  Run a file with coverage collection and report
profile   Run a file with CPU/memory profiling and report
add       Add a dependency to nlpl.toml
remove    Remove a dependency from nlpl.toml
lock      Regenerate nlpl.lock from the current nlpl.toml
deps      List all dependencies and their lock status
search    Search the package registry for packages
publish   Publish this package to the registry
workspace Manage multi-package workspaces (init/list/build/clean/test)
"""

import os
import sys
import argparse
from pathlib import Path

from ..tooling.config import ConfigLoader
from ..tooling.builder import BuildSystem

__all__ = ["main", "nlpllint"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_project(manifest: str = "nlpl.toml"):
    """Load project config or exit with a helpful message."""
    path = Path(manifest)
    if not path.exists():
        print(f"error: {manifest} not found. Are you in an NLPL project root?")
        sys.exit(1)
    try:
        return ConfigLoader.load(manifest)
    except Exception as exc:
        print(f"error: failed to parse {manifest}: {exc}")
        sys.exit(1)


def _scaffold_project(root: Path, name: str) -> None:
    """Write initial nlpl.toml, src/main.nlpl, tests/.gitkeep, and .gitignore."""
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)

    toml_content = (
        f'[package]\n'
        f'name = "{name}"\n'
        f'version = "0.1.0"\n'
        f'authors = []\n'
        f'description = ""\n'
        f'\n'
        f'[build]\n'
        f'source_dir = "src"\n'
        f'output_dir = "build"\n'
        f'target = "c"\n'
        f'optimization = 0\n'
        f'headers = false\n'
        f'\n'
        f'[dependencies]\n'
        f'\n'
        f'[dev-dependencies]\n'
        f'\n'
        f'[features]\n'
        f'default = []\n'
    )
    (root / "nlpl.toml").write_text(toml_content)

    main_content = (
        f'function main\n'
        f'    print text "Hello from {name}!"\n'
        f'end\n'
    )
    (root / "src" / "main.nlpl").write_text(main_content)

    (root / "tests" / ".gitkeep").write_text("")

    gitignore_content = "/build/\nnlpl.lock\n*.o\n*.ll\n"
    gi = root / ".gitignore"
    if not gi.exists():
        gi.write_text(gitignore_content)


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_new(args):
    """Create a new NLPL project in a new directory."""
    name = args.name
    root = Path(name)
    if root.exists():
        print(f"error: directory '{name}' already exists.")
        sys.exit(1)
    root.mkdir(parents=True)
    _scaffold_project(root, name)
    print(f"     Created NLPL project `{name}`")
    print(f"       Enter the project:  cd {name}")
    print(f"       Build:              nlpl build")
    print(f"       Run:                nlpl run")


def cmd_init(args):
    """Initialise a new NLPL project in the current directory."""
    cwd = Path.cwd()
    if (cwd / "nlpl.toml").exists():
        print("error: nlpl.toml already exists in the current directory.")
        sys.exit(1)
    name = args.name or cwd.name
    _scaffold_project(cwd, name)
    print(f"     Initialised NLPL project `{name}` in {cwd}")


def cmd_build(args):
    """Compile the project."""
    config = _load_project()
    builder = BuildSystem(config)
    features = args.features or []
    ok = builder.build(
        release=args.release,
        profile=args.profile,
        features=features,
        jobs=args.jobs,
        clean=args.clean,
        optimize_bounds_checks=args.optimize_bounds_checks,
    )
    sys.exit(0 if ok else 1)


def cmd_run(args):
    """Build and run the project executable."""
    config = _load_project()
    builder = BuildSystem(config)
    features = args.features or []
    run_args = args.run_args or []
    code = builder.run(
        release=args.release,
        features=features,
        run_args=run_args,
    )
    sys.exit(code)


def cmd_check(args):
    """Parse and type-check without producing output."""
    config = _load_project()
    builder = BuildSystem(config)
    features = args.features or []
    ok = builder.check(features=features)
    sys.exit(0 if ok else 1)


def cmd_clean(args):
    """Remove the build output directory and clear build cache."""
    config = _load_project()
    builder = BuildSystem(config)
    builder.clean()


def cmd_test(args):
    """Discover and run tests from the tests/ directory."""
    config = _load_project()
    builder = BuildSystem(config)
    features = args.features or []
    filter_names = args.filter or []
    code = builder.test(
        filter_names=filter_names if filter_names else None,
        release=args.release,
        features=features,
        coverage=getattr(args, 'coverage', False),
        coverage_output=getattr(args, 'coverage_output', None),
        jobs=getattr(args, 'jobs', None),
    )
    sys.exit(code)


def cmd_coverage(args):
    """Run a NLPL file (or test suite) and generate a coverage report."""
    from ..tooling.coverage import run_with_coverage
    source = args.source
    output_dir = args.output or "coverage"
    report = run_with_coverage(
        source_path=source,
        output_dir=output_dir,
        report_json=True,
        report_html=True,
    )
    if report.total_pct() < (args.fail_under or 0):
        print(f"error: coverage {report.total_pct():.1f}% is below required {args.fail_under}%")
        sys.exit(1)


def cmd_profile(args):
    """Run a NLPL file with CPU and memory profiling."""
    from ..tooling.profiler import run_with_profiling
    source = args.source
    output_dir = args.output or "profile"
    run_with_profiling(
        source_path=source,
        output_dir=output_dir,
        cpu=not args.no_cpu,
        memory=not args.no_memory,
    )


def cmd_add(args):
    """Add a dependency to nlpl.toml and update nlpl.lock."""
    from ..tooling.dependency_manager import add_dependency
    try:
        add_dependency(
            Path.cwd(),
            args.spec,
            dev=args.dev,
            path=args.path,
            git=args.git,
            branch=args.branch,
            tag=args.tag,
            rev=args.rev,
        )
    except Exception as exc:
        print(f"error: {exc}")
        sys.exit(1)


def cmd_remove(args):
    """Remove a dependency from nlpl.toml and update nlpl.lock."""
    from ..tooling.dependency_manager import remove_dependency
    try:
        remove_dependency(Path.cwd(), args.name, dev=args.dev)
    except Exception as exc:
        print(f"error: {exc}")
        sys.exit(1)


def cmd_lock(args):
    """Regenerate nlpl.lock from the current nlpl.toml."""
    from ..tooling.dependency_manager import update_lockfile
    offline = getattr(args, "offline", False)
    try:
        update_lockfile(Path.cwd(), offline=offline)
    except Exception as exc:
        print(f"error: {exc}")
        sys.exit(1)


def cmd_deps(args):
    """List all dependencies and their lock status."""
    from ..tooling.dependency_manager import list_dependencies
    try:
        list_dependencies(Path.cwd())
    except Exception as exc:
        print(f"error: {exc}")
        sys.exit(1)


def cmd_search(args):
    """Search the package registry for packages."""
    from ..tooling.registry import RegistryConfig, RegistryClient, RegistryError

    config = RegistryConfig.from_project(Path.cwd())
    client = RegistryClient(config)

    try:
        results = client.search(args.query, limit=args.limit or 20)
    except RegistryError as exc:
        print(f"error: {exc}")
        sys.exit(1)

    if not results:
        print(f"No packages found matching '{args.query}'.")
        return

    print(f"Registry: {config.url}")
    print(f"Results for '{args.query}':\n")
    for r in results:
        dl = f"  ({r.downloads:,} downloads)" if r.downloads else ""
        desc = f"  {r.description}" if r.description else ""
        print(f"  {r.name} {r.version}{dl}")
        if desc:
            print(f"  {r.description}")
        print()


def cmd_publish(args):
    """Publish this package to the registry."""
    from ..tooling.registry import (
        RegistryConfig,
        RegistryClient,
        RegistryError,
        AuthError,
    )

    config = RegistryConfig.from_project(Path.cwd())
    client = RegistryClient(config)
    dry_run = getattr(args, "dry_run", False)

    if dry_run:
        print("  Dry run mode: package will not be uploaded.")

    try:
        client.publish(Path.cwd(), dry_run=dry_run)
    except AuthError as exc:
        print(f"error: {exc}")
        print("Hint: Set NLPL_REGISTRY_TOKEN or add token to nlpl.toml [registry].")
        sys.exit(1)
    except RegistryError as exc:
        print(f"error: {exc}")
        sys.exit(1)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}")
        sys.exit(1)


def cmd_workspace(args):
    """Dispatch workspace sub-subcommands."""
    from ..tooling.workspace import (
        WorkspaceManifest,
        WorkspaceResolver,
        WorkspaceBuilder,
        WorkspaceError,
        init_workspace,
        load_workspace,
    )

    subcmd = getattr(args, "ws_command", None)

    if subcmd is None or subcmd == "init":
        _ws_init(args, init_workspace)
    elif subcmd == "list":
        _ws_list(args, load_workspace)
    elif subcmd == "build":
        _ws_build(args, load_workspace)
    elif subcmd == "clean":
        _ws_clean(args, load_workspace)
    elif subcmd == "test":
        _ws_test(args, load_workspace)
    elif subcmd == "lock":
        _ws_lock(args, load_workspace)
    else:
        print(f"error: unknown workspace subcommand '{subcmd}'")
        print("Available: init, list, build, clean, test, lock")
        sys.exit(1)


def _ws_init(args, init_workspace):
    from ..tooling.workspace import WorkspaceError
    members = getattr(args, "members", None)
    description = getattr(args, "description", "") or ""
    try:
        init_workspace(
            Path.cwd(),
            members=members,
            description=description,
        )
    except FileExistsError as exc:
        print(f"error: {exc}")
        sys.exit(1)
    except WorkspaceError as exc:
        print(f"error: {exc}")
        sys.exit(1)


def _ws_list(args, load_workspace):
    from ..tooling.workspace import WorkspaceError
    try:
        manifest, resolver = load_workspace(Path.cwd())
    except (FileNotFoundError, WorkspaceError) as exc:
        print(f"error: {exc}")
        sys.exit(1)

    print(f"Workspace: {manifest.root}")
    if manifest.description:
        print(f"  {manifest.description}")
    print(f"\nMembers ({len(resolver.members)}):")
    for info in resolver.status():
        deps_str = ""
        if info["intra_deps"]:
            deps_str = f"  -> {', '.join(info['intra_deps'])}"
        print(f"  {info['name']} {info['version']}{deps_str}")
        if info["description"]:
            print(f"    {info['description']}")
    print(f"\nBuild order: {' -> '.join(resolver.build_order)}")


def _ws_build(args, load_workspace):
    from ..tooling.workspace import WorkspaceError
    try:
        manifest, resolver = load_workspace(Path.cwd())
    except (FileNotFoundError, WorkspaceError) as exc:
        print(f"error: {exc}")
        sys.exit(1)

    builder = WorkspaceBuilder(resolver)
    member_name = getattr(args, "member", None)
    features = getattr(args, "features", None) or []
    release = getattr(args, "release", False)
    jobs = getattr(args, "jobs", None)

    if member_name:
        try:
            ok = builder.build_member(
                member_name, release=release, features=features, jobs=jobs
            )
        except KeyError as exc:
            print(f"error: {exc}")
            sys.exit(1)
    else:
        ok = builder.build_all(release=release, features=features, jobs=jobs)
    sys.exit(0 if ok else 1)


def _ws_clean(args, load_workspace):
    from ..tooling.workspace import WorkspaceError
    try:
        manifest, resolver = load_workspace(Path.cwd())
    except (FileNotFoundError, WorkspaceError) as exc:
        print(f"error: {exc}")
        sys.exit(1)
    WorkspaceBuilder(resolver).clean_all()


def _ws_test(args, load_workspace):
    from ..tooling.workspace import WorkspaceError
    try:
        manifest, resolver = load_workspace(Path.cwd())
    except (FileNotFoundError, WorkspaceError) as exc:
        print(f"error: {exc}")
        sys.exit(1)

    filter_names = getattr(args, "filter", None) or []
    release = getattr(args, "release", False)
    features = getattr(args, "features", None) or []

    code = WorkspaceBuilder(resolver).test_all(
        filter_names=filter_names if filter_names else None,
        release=release,
        features=features,
    )
    sys.exit(code)


def _ws_lock(args, load_workspace):
    from ..tooling.workspace import WorkspaceError
    try:
        manifest, resolver = load_workspace(Path.cwd())
    except (FileNotFoundError, WorkspaceError) as exc:
        print(f"error: {exc}")
        sys.exit(1)
    try:
        resolver.regenerate_shared_lock()
    except WorkspaceError as exc:
        print(f"error: {exc}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nlpl",
        description="NLPL Compiler & Toolchain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # ---- new ----------------------------------------------------------------
    p_new = sub.add_parser("new", help="Create a new project")
    p_new.add_argument("name", help="Project name (also the new directory name)")

    # ---- init ---------------------------------------------------------------
    p_init = sub.add_parser("init", help="Initialise a project in the current directory")
    p_init.add_argument("name", nargs="?", default=None,
                        help="Package name (defaults to current directory name)")

    # ---- build --------------------------------------------------------------
    p_build = sub.add_parser("build", help="Compile the project")
    p_build.add_argument("--release", action="store_true",
                         help="Build with release profile (optimised, no debug info)")
    p_build.add_argument("--profile", metavar="PROFILE",
                         help="Use a named build profile (overrides --release)")
    p_build.add_argument("--features", nargs="+", metavar="FEATURE",
                         help="Enable additional named features")
    p_build.add_argument("--jobs", "-j", type=int, metavar="N",
                         help="Number of parallel compilation workers")
    p_build.add_argument("--clean", action="store_true",
                         help="Remove cached artefacts before building")
    p_build.add_argument("--optimize-bounds-checks", action="store_true",
                         help="Enable compile-time bounds check elimination")
    p_build.add_argument("--verbose", "-v", action="store_true",
                         help="Show verbose compiler output")
    p_build.add_argument("--quiet", "-q", action="store_true",
                         help="Suppress informational output")
    p_build.add_argument("--target", metavar="TRIPLE",
                         help="Target triple for cross-compilation (e.g. x86_64-linux-gnu)")

    # ---- run ----------------------------------------------------------------
    p_run = sub.add_parser("run", help="Build and run the project")
    p_run.add_argument("--release", action="store_true",
                       help="Build with release profile before running")
    p_run.add_argument("--features", nargs="+", metavar="FEATURE",
                       help="Enable additional named features")
    p_run.add_argument("run_args", nargs=argparse.REMAINDER, metavar="-- [ARGS...]",
                       help="Arguments to pass to the compiled program (after --)")

    # ---- check --------------------------------------------------------------
    p_check = sub.add_parser("check", help="Type-check without producing output")
    p_check.add_argument("--features", nargs="+", metavar="FEATURE",
                         help="Enable additional named features")

    # ---- clean --------------------------------------------------------------
    sub.add_parser("clean", help="Remove build output directory and cache")

    # ---- test ---------------------------------------------------------------
    p_test = sub.add_parser("test", help="Run tests from the tests/ directory")
    p_test.add_argument("filter", nargs="*", metavar="NAME",
                        help="Only run tests whose filename contains this string")
    p_test.add_argument("--release", action="store_true",
                        help="Build tests with release profile")
    p_test.add_argument("--features", nargs="+", metavar="FEATURE",
                        help="Enable additional named features")
    p_test.add_argument("--coverage", action="store_true",
                        help="Collect line coverage and write report to coverage/")
    p_test.add_argument("--coverage-output", metavar="DIR",
                        help="Directory to write coverage report (default: coverage/)")
    p_test.add_argument("--jobs", "-j", type=int, metavar="N",
                        help="Number of parallel test jobs (default: CPU count)")

    # ---- coverage -----------------------------------------------------------
    p_cov = sub.add_parser("coverage", help="Run a file with coverage collection")
    p_cov.add_argument("source", metavar="FILE", help="NLPL source file to run")
    p_cov.add_argument("--output", "-o", metavar="DIR",
                       help="Output directory for coverage report (default: coverage/)")
    p_cov.add_argument("--fail-under", type=float, metavar="PCT",
                       help="Exit 1 if coverage is below this percentage")

    # ---- profile ------------------------------------------------------------
    p_prof = sub.add_parser("profile", help="Run a file with CPU/memory profiling")
    p_prof.add_argument("source", metavar="FILE", help="NLPL source file to profile")
    p_prof.add_argument("--output", "-o", metavar="DIR",
                        help="Output directory for profile report (default: profile/)")
    p_prof.add_argument("--no-cpu", action="store_true",
                        help="Disable CPU profiling")
    p_prof.add_argument("--no-memory", action="store_true",
                        help="Disable memory profiling")

    # ---- add ----------------------------------------------------------------
    p_add = sub.add_parser("add", help="Add a dependency")
    p_add.add_argument("spec", metavar="PACKAGE[@VERSION]",
                       help="Package name with optional version constraint (e.g. mylib@^1.2)")
    p_add.add_argument("--dev", action="store_true",
                       help="Add as a dev-dependency")
    p_add.add_argument("--path", metavar="PATH",
                       help="Local filesystem path to an NLPL project")
    p_add.add_argument("--git", metavar="URL",
                       help="Git repository URL")
    p_add.add_argument("--branch", metavar="BRANCH",
                       help="Git branch (used with --git)")
    p_add.add_argument("--tag", metavar="TAG",
                       help="Git tag (used with --git)")
    p_add.add_argument("--rev", metavar="SHA",
                       help="Exact git commit SHA (used with --git)")

    # ---- remove -------------------------------------------------------------
    p_remove = sub.add_parser("remove", help="Remove a dependency")
    p_remove.add_argument("name", help="Package name to remove")
    p_remove.add_argument("--dev", action="store_true",
                          help="Remove from dev-dependencies")

    # ---- lock ---------------------------------------------------------------
    p_lock = sub.add_parser("lock", help="Regenerate nlpl.lock from nlpl.toml")
    p_lock.add_argument("--offline", action="store_true",
                        help="Skip registry network calls (use cached/fallback data)")

    # ---- deps ---------------------------------------------------------------
    sub.add_parser("deps", help="List dependencies and lock status")

    # ---- search -------------------------------------------------------------
    p_search = sub.add_parser("search", help="Search the package registry")
    p_search.add_argument("query", help="Search term")
    p_search.add_argument("--limit", "-n", type=int, default=20, metavar="N",
                          help="Maximum number of results (default: 20)")

    # ---- publish ------------------------------------------------------------
    p_publish = sub.add_parser("publish", help="Publish this package to the registry")
    p_publish.add_argument("--dry-run", action="store_true",
                           help="Create archive and validate metadata but do not upload")

    # ---- workspace ----------------------------------------------------------
    p_ws = sub.add_parser("workspace", help="Manage multi-package workspaces",
                          aliases=["ws"])
    ws_sub = p_ws.add_subparsers(dest="ws_command", metavar="<subcommand>")

    p_ws_init = ws_sub.add_parser("init", help="Create a workspace manifest in the current directory")
    p_ws_init.add_argument("--members", nargs="+", metavar="GLOB",
                           help="Member glob patterns (default: packages/*)")
    p_ws_init.add_argument("--description", metavar="TEXT",
                           help="Optional workspace description")

    ws_sub.add_parser("list", help="List all workspace members and build order")

    p_ws_build = ws_sub.add_parser("build", help="Build all (or a single) workspace member")
    p_ws_build.add_argument("member", nargs="?", metavar="NAME",
                             help="Build only this member (default: build all)")
    p_ws_build.add_argument("--release", action="store_true",
                             help="Build with release profile")
    p_ws_build.add_argument("--features", nargs="+", metavar="FEATURE",
                             help="Enable named features")
    p_ws_build.add_argument("--jobs", "-j", type=int, metavar="N",
                             help="Parallel compilation workers")

    ws_sub.add_parser("clean", help="Clean all workspace members")

    p_ws_test = ws_sub.add_parser("test", help="Run tests across all workspace members")
    p_ws_test.add_argument("filter", nargs="*", metavar="NAME",
                           help="Only run tests whose filename contains this string")
    p_ws_test.add_argument("--release", action="store_true",
                           help="Run tests with release profile")
    p_ws_test.add_argument("--features", nargs="+", metavar="FEATURE",
                           help="Enable named features")

    ws_sub.add_parser("lock", help="Regenerate the shared workspace nlpl.lock")

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = _build_parser()
    # Strip the '--' separator before REMAINDER args so argparse handles them cleanly
    argv = sys.argv[1:]
    if "run" in argv:
        run_idx = argv.index("run")
        if "--" in argv[run_idx:]:
            sep = argv.index("--", run_idx)
            argv = argv[:sep] + argv[sep + 1:]

    args = parser.parse_args(argv)

    dispatch = {
        "new":       cmd_new,
        "init":      cmd_init,
        "build":     cmd_build,
        "run":       cmd_run,
        "check":     cmd_check,
        "clean":     cmd_clean,
        "test":      cmd_test,
        "add":       cmd_add,
        "remove":    cmd_remove,
        "lock":      cmd_lock,
        "deps":      cmd_deps,
        "search":    cmd_search,
        "publish":   cmd_publish,
        "workspace": cmd_workspace,
        "ws":        cmd_workspace,  # Short alias
        "coverage":  cmd_coverage,
        "profile":   cmd_profile,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(0)

    handler(args)


if __name__ == "__main__":
    main()
