"""Tests for the 5.1 Build System implementation.

Covers:
- _BuildCache  (builder.py)
- BuildResult  (builder.py)
- ConfigLoader (config.py) — profiles, features, dev-deps, effective_features
- LockFile     (lockfile.py) — save/load, atomic write, package management
- _parse_package_spec / add_dependency / remove_dependency (dependency_manager.py)
- BuildSystem.clean / BuildSystem.check (builder.py, integration-ish)
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Make sure the src tree is importable regardless of whether pytest is run from
# the project root or from within src/.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nlpl.tooling.builder import _BuildCache, BuildResult, BuildSystem
from nlpl.tooling.build_script import (
    BuildScriptCache,
    BuildScriptDirectives,
    BuildScriptResult,
    _parse_directives,
    _file_sha256,
    run_build_script,
)
from nlpl.tooling.config import (
    ConfigLoader,
    FeaturesConfig,
    ProfileConfig,
    ProjectConfig,
    PackageConfig,
    BuildConfig,
    _PROFILE_DEV,
    _PROFILE_RELEASE,
)
from nlpl.tooling.lockfile import (
    LockFile,
    LockedPackage,
    LOCKFILE_VERSION,
    compute_file_checksum,
    compute_directory_checksum,
)
from nlpl.tooling.dependency_manager import (
    _parse_package_spec,
    add_dependency,
    remove_dependency,
    list_dependencies,
    update_lockfile,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

MINIMAL_TOML = """\
[package]
name = "myproject"
version = "1.2.3"
authors = ["Alice <alice@example.com>"]
description = "A test project"

[build]
source_dir = "src"
output_dir = "build"
target = "c"
optimization = 0
"""

FULL_TOML = """\
[package]
name = "full"
version = "0.5.0"

[build]
source_dir = "src"
output_dir = "out"
target = "c"
optimization = 1
profile = "dev"

[dependencies]
libmath = "^1.0"
libnet = { path = "../libnet" }

[dev-dependencies]
testlib = "^2.3"

[build-dependencies]
codegen = "^0.1"

[features]
default = ["networking"]
networking = ["dep:libnet"]
logging = []

[profile.fast]
inherits = "release"
opt-level = 2
strip = false

[profile.bench]
inherits = "release"
opt-level = 3
lto = true
"""


def _write_toml(tmp: Path, content: str) -> Path:
    p = tmp / "nlpl.toml"
    p.write_text(content)
    return p


def _make_source_file(path: Path, content: str = "x = 1\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def _minimal_project_config(name: str = "test", src_dir: str = "src",
                             out_dir: str = "build") -> ProjectConfig:
    return ProjectConfig(
        package=PackageConfig(name=name, version="0.1.0"),
        build=BuildConfig(source_dir=src_dir, output_dir=out_dir),
    )


# ---------------------------------------------------------------------------
# _BuildCache tests
# ---------------------------------------------------------------------------

class TestBuildCache:

    def test_new_file_always_needs_rebuild(self, tmp_path):
        cache = _BuildCache(tmp_path / ".build_cache.json")
        src = _make_source_file(tmp_path / "a.nlpl", "set x to 1\n")
        assert cache.needs_rebuild(str(src)) is True

    def test_after_mark_built_no_rebuild(self, tmp_path):
        cache = _BuildCache(tmp_path / ".build_cache.json")
        src = _make_source_file(tmp_path / "a.nlpl")
        cache.mark_built(str(src))
        assert cache.needs_rebuild(str(src)) is False

    def test_rebuild_after_content_change(self, tmp_path):
        cache = _BuildCache(tmp_path / ".build_cache.json")
        src = _make_source_file(tmp_path / "a.nlpl", "set x to 1\n")
        cache.mark_built(str(src))

        # Overwrite with different content, ensure mtime actually differs
        time.sleep(0.01)
        src.write_text("set x to 99\n")
        os.utime(str(src), (time.time() + 1, time.time() + 1))  # force mtime change
        assert cache.needs_rebuild(str(src)) is True

    def test_save_and_reload(self, tmp_path):
        cache_path = tmp_path / ".build_cache.json"
        cache = _BuildCache(cache_path)
        src = _make_source_file(tmp_path / "b.nlpl")
        cache.mark_built(str(src))
        cache.save()

        cache2 = _BuildCache(cache_path)
        assert cache2.needs_rebuild(str(src)) is False

    def test_save_creates_parent_dir(self, tmp_path):
        subdir = tmp_path / "nested" / "build"
        cache = _BuildCache(subdir / ".build_cache.json")
        src = _make_source_file(tmp_path / "c.nlpl")
        cache.mark_built(str(src))
        cache.save()
        assert (subdir / ".build_cache.json").exists()

    def test_clear_removes_all_entries(self, tmp_path):
        cache_path = tmp_path / ".build_cache.json"
        cache = _BuildCache(cache_path)
        src = _make_source_file(tmp_path / "d.nlpl")
        cache.mark_built(str(src))
        cache.save()

        cache.clear()
        cache.save()
        assert cache.needs_rebuild(str(src)) is True

    def test_missing_source_file_needs_rebuild(self, tmp_path):
        cache = _BuildCache(tmp_path / ".build_cache.json")
        assert cache.needs_rebuild(str(tmp_path / "nonexistent.nlpl")) is True

    def test_corrupt_cache_file_recovered_gracefully(self, tmp_path):
        cache_path = tmp_path / ".build_cache.json"
        cache_path.write_text("{{{INVALID JSON}}}")
        cache = _BuildCache(cache_path)
        src = _make_source_file(tmp_path / "e.nlpl")
        assert cache.needs_rebuild(str(src)) is True  # no crash


# ---------------------------------------------------------------------------
# BuildResult tests
# ---------------------------------------------------------------------------

class TestBuildResult:

    def test_success_result(self, capsys):
        result = BuildResult(success=True, files_compiled=5, files_cached=2, elapsed=1.23)
        result.print_summary("myproject", "dev")
        out = capsys.readouterr().out
        assert "Finished" in out
        assert "myproject" in out
        assert "5 compiled" in out
        assert "2 cached" in out

    def test_failure_result_shows_errors(self, capsys):
        result = BuildResult(
            success=False,
            errors=["syntax error on line 3"],
            warnings=["unused variable x"],
        )
        result.print_summary("myproject", "release")
        out = capsys.readouterr().out
        assert "Failed" in out
        assert "syntax error on line 3" in out
        assert "unused variable x" in out

    def test_no_cached_note_when_zero(self, capsys):
        result = BuildResult(success=True, files_compiled=1, files_cached=0, elapsed=0.1)
        result.print_summary("p", "dev")
        out = capsys.readouterr().out
        assert "cached" not in out


# ---------------------------------------------------------------------------
# ConfigLoader tests
# ---------------------------------------------------------------------------

class TestConfigLoader:

    def test_minimal_toml_defaults(self, tmp_path):
        _write_toml(tmp_path, MINIMAL_TOML)
        orig = Path.cwd()
        os.chdir(tmp_path)
        try:
            config = ConfigLoader.load("nlpl.toml")
        finally:
            os.chdir(orig)
        assert config.package.name == "myproject"
        assert config.package.version == "1.2.3"
        assert config.build.source_dir == "src"
        assert config.build.output_dir == "build"
        assert config.build.target == "c"

    def test_full_toml_parsed(self, tmp_path):
        _write_toml(tmp_path, FULL_TOML)
        orig = Path.cwd()
        os.chdir(tmp_path)
        try:
            config = ConfigLoader.load("nlpl.toml")
        finally:
            os.chdir(orig)
        assert config.package.name == "full"
        assert "libmath" in config.dependencies
        assert "testlib" in config.dev_dependencies
        assert "codegen" in config.build_dependencies

    def test_builtin_dev_profile(self, tmp_path):
        _write_toml(tmp_path, MINIMAL_TOML)
        orig = Path.cwd()
        os.chdir(tmp_path)
        try:
            config = ConfigLoader.load("nlpl.toml")
        finally:
            os.chdir(orig)
        prof = config.get_profile("dev")
        assert prof.optimization == 0
        assert prof.debug_info is True
        assert prof.lto is False
        assert prof.strip is False

    def test_builtin_release_profile(self, tmp_path):
        _write_toml(tmp_path, MINIMAL_TOML)
        orig = Path.cwd()
        os.chdir(tmp_path)
        try:
            config = ConfigLoader.load("nlpl.toml")
        finally:
            os.chdir(orig)
        prof = config.get_profile("release")
        assert prof.optimization == 3
        assert prof.debug_info is False
        assert prof.lto is True
        assert prof.strip is True

    def test_custom_profile_fast(self, tmp_path):
        _write_toml(tmp_path, FULL_TOML)
        orig = Path.cwd()
        os.chdir(tmp_path)
        try:
            config = ConfigLoader.load("nlpl.toml")
        finally:
            os.chdir(orig)
        fast = config.get_profile("fast")
        assert fast.optimization == 2
        assert fast.strip is False  # overridden from release default

    def test_custom_profile_bench_inherits_release(self, tmp_path):
        _write_toml(tmp_path, FULL_TOML)
        orig = Path.cwd()
        os.chdir(tmp_path)
        try:
            config = ConfigLoader.load("nlpl.toml")
        finally:
            os.chdir(orig)
        bench = config.get_profile("bench")
        assert bench.optimization == 3
        assert bench.lto is True

    def test_effective_features_includes_defaults(self, tmp_path):
        _write_toml(tmp_path, FULL_TOML)
        orig = Path.cwd()
        os.chdir(tmp_path)
        try:
            config = ConfigLoader.load("nlpl.toml")
        finally:
            os.chdir(orig)
        feats = config.effective_features()
        assert "networking" in feats  # listed in default

    def test_effective_features_transitive(self, tmp_path):
        toml = MINIMAL_TOML + """
[features]
default = ["a"]
a = ["b"]
b = []
"""
        _write_toml(tmp_path, toml)
        orig = Path.cwd()
        os.chdir(tmp_path)
        try:
            config = ConfigLoader.load("nlpl.toml")
        finally:
            os.chdir(orig)
        feats = config.effective_features()
        assert "a" in feats
        assert "b" in feats

    def test_effective_features_no_dep_prefix_expansion(self, tmp_path):
        toml = MINIMAL_TOML + """
[features]
default = ["net"]
net = ["dep:libnet"]
"""
        _write_toml(tmp_path, toml)
        orig = Path.cwd()
        os.chdir(tmp_path)
        try:
            config = ConfigLoader.load("nlpl.toml")
        finally:
            os.chdir(orig)
        feats = config.effective_features()
        # dep: prefixed entries are NOT treated as feature names
        assert "dep:libnet" not in feats
        assert "libnet" not in feats

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load("/tmp/does_not_exist_nlpl.toml")


# ---------------------------------------------------------------------------
# LockFile tests
# ---------------------------------------------------------------------------

class TestLockFile:

    def _sample_package(self, name: str = "mypkg") -> LockedPackage:
        return LockedPackage(
            name=name,
            version="1.0.0",
            source="registry",
            checksum="sha256:abc123",
        )

    def test_empty_lockfile(self):
        lf = LockFile.empty()
        assert lf.version == LOCKFILE_VERSION
        assert lf.packages == {}  # packages is a dict keyed by name

    def test_add_and_retrieve_package(self):
        lf = LockFile.empty()
        pkg = self._sample_package("alpha")
        lf.add_package(pkg)
        assert len(lf.packages) == 1
        assert lf.packages["alpha"].name == "alpha"

    def test_remove_package(self):
        lf = LockFile.empty()
        lf.add_package(self._sample_package("alpha"))
        lf.add_package(self._sample_package("beta"))
        lf.remove_package("alpha")
        assert len(lf.packages) == 1
        assert "alpha" not in lf.packages
        assert lf.packages["beta"].name == "beta"

    def test_remove_nonexistent_is_noop(self):
        lf = LockFile.empty()
        lf.remove_package("ghost")  # should not raise
        assert lf.packages == {}  # packages is a dict

    def test_save_and_load_round_trip(self, tmp_path):
        lf = LockFile.empty()
        pkg = LockedPackage(
            name="roundtrip",
            version="2.3.4",
            source="path",
            checksum="sha256:deadbeef",
            resolved_path="/tmp/roundtrip",
        )
        lf.add_package(pkg)
        lock_path = tmp_path / "nlpl.lock"
        lf.save(lock_path)

        lf2 = LockFile.load(lock_path)
        assert lf2.version == LOCKFILE_VERSION
        assert len(lf2.packages) == 1
        p = lf2.packages["roundtrip"]
        assert p.name == "roundtrip"
        assert p.version == "2.3.4"
        assert p.resolved_path == "/tmp/roundtrip"

    def test_save_is_atomic(self, tmp_path):
        """The lock file should be written atomically (no partial writes visible)."""
        lf = LockFile.empty()
        lock_path = tmp_path / "nlpl.lock"
        lf.save(lock_path)
        # After save, no .tmp file should remain
        assert not (tmp_path / "nlpl.lock.tmp").exists()
        assert lock_path.exists()

    def test_load_wrong_version_raises(self, tmp_path):
        lock_path = tmp_path / "nlpl.lock"
        lock_path.write_text(json.dumps({"version": 999, "package": []}))
        with pytest.raises(ValueError, match="Unsupported lock file version"):
            LockFile.load(lock_path)

    def test_load_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            LockFile.load(tmp_path / "nonexistent.lock")

    def test_verify_paths_valid(self, tmp_path):
        lf = LockFile.empty()
        existing = tmp_path / "lib"
        existing.mkdir()
        pkg = LockedPackage(
            name="local",
            version="0.1.0",
            source="path",
            checksum="sha256:00",
            resolved_path=str(existing),
        )
        lf.add_package(pkg)
        missing = lf.verify_paths()
        assert missing == []

    def test_verify_paths_missing(self, tmp_path):
        lf = LockFile.empty()
        pkg = LockedPackage(
            name="missing_lib",
            version="0.1.0",
            source="path",
            checksum="sha256:00",
            resolved_path="/tmp/__this_does_not_exist_nlpl__",
        )
        lf.add_package(pkg)
        errors = lf.verify_paths()
        # verify_paths returns full error strings; check that the package name appears
        assert len(errors) == 1
        assert "missing_lib" in errors[0]


# ---------------------------------------------------------------------------
# compute_file_checksum / compute_directory_checksum tests
# ---------------------------------------------------------------------------

class TestChecksums:

    def test_file_checksum_format(self, tmp_path):
        f = tmp_path / "data.txt"
        f.write_bytes(b"hello")
        chk = compute_file_checksum(f)
        assert chk.startswith("sha256:")
        assert len(chk) == len("sha256:") + 64

    def test_file_checksum_deterministic(self, tmp_path):
        f = tmp_path / "data.txt"
        f.write_bytes(b"hello world")
        assert compute_file_checksum(f) == compute_file_checksum(f)

    def test_file_checksum_changes_on_content_change(self, tmp_path):
        f = tmp_path / "data.txt"
        f.write_bytes(b"version1")
        c1 = compute_file_checksum(f)
        f.write_bytes(b"version2")
        c2 = compute_file_checksum(f)
        assert c1 != c2

    def test_directory_checksum_only_nlpl_files(self, tmp_path):
        (tmp_path / "a.nlpl").write_text("set x to 1\n")
        (tmp_path / "b.nlpl").write_text("set y to 2\n")
        (tmp_path / "readme.txt").write_text("ignore me\n")
        chk = compute_directory_checksum(tmp_path)
        assert chk.startswith("sha256:")

    def test_directory_checksum_stable(self, tmp_path):
        (tmp_path / "a.nlpl").write_text("set x to 1\n")
        c1 = compute_directory_checksum(tmp_path)
        c2 = compute_directory_checksum(tmp_path)
        assert c1 == c2

    def test_directory_checksum_changes_on_edit(self, tmp_path):
        f = tmp_path / "a.nlpl"
        f.write_text("set x to 1\n")
        c1 = compute_directory_checksum(tmp_path)
        f.write_text("set x to 99\n")
        c2 = compute_directory_checksum(tmp_path)
        assert c1 != c2


# ---------------------------------------------------------------------------
# _parse_package_spec tests
# ---------------------------------------------------------------------------

class TestParsePackageSpec:

    def test_name_only(self):
        name, ver = _parse_package_spec("mylib")
        assert name == "mylib"
        assert ver is None

    def test_name_with_caret_version(self):
        name, ver = _parse_package_spec("mylib@^1.2.3")
        assert name == "mylib"
        assert ver == "^1.2.3"

    def test_name_with_tilde_version(self):
        name, ver = _parse_package_spec("somelib@~2.0")
        assert name == "somelib"
        assert ver == "~2.0"

    def test_name_with_exact_version(self):
        name, ver = _parse_package_spec("pkg@1.0.0")
        assert name == "pkg"
        assert ver == "1.0.0"

    def test_name_with_gte_constraint(self):
        name, ver = _parse_package_spec("pkg@>=0.5")
        assert name == "pkg"
        assert ver == ">=0.5"

    def test_empty_spec_raises(self):
        with pytest.raises((ValueError, SystemExit)):
            _parse_package_spec("")

    def test_name_with_hyphens(self):
        name, ver = _parse_package_spec("my-cool-lib@^3.0")
        assert name == "my-cool-lib"
        assert ver == "^3.0"

    def test_name_with_underscores(self):
        name, ver = _parse_package_spec("my_lib@^1.0")
        assert name == "my_lib"
        assert ver == "^1.0"


# ---------------------------------------------------------------------------
# add_dependency / remove_dependency tests
# ---------------------------------------------------------------------------

def _minimal_project_dir(tmp_path: Path, name: str = "testproj") -> Path:
    """Create a minimal project directory with nlpl.toml."""
    toml = (
        f'[package]\nname = "{name}"\nversion = "0.1.0"\n\n'
        f'[build]\nsource_dir = "src"\noutput_dir = "build"\ntarget = "c"\n\n'
        f'[dependencies]\n\n[dev-dependencies]\n'
    )
    (tmp_path / "nlpl.toml").write_text(toml)
    (tmp_path / "src").mkdir(exist_ok=True)
    return tmp_path


class TestAddDependency:

    def test_add_registry_dependency(self, tmp_path):
        project = _minimal_project_dir(tmp_path)
        add_dependency(project, "mylib@^1.0")
        content = (project / "nlpl.toml").read_text()
        assert "mylib" in content

    def test_add_dev_dependency(self, tmp_path):
        project = _minimal_project_dir(tmp_path)
        add_dependency(project, "testkit@^2.0", dev=True)
        content = (project / "nlpl.toml").read_text()
        assert "testkit" in content

    def test_add_path_dependency(self, tmp_path):
        project = _minimal_project_dir(tmp_path)
        lib_dir = tmp_path / "mylib"
        lib_dir.mkdir()
        (lib_dir / "nlpl.toml").write_text("[package]\nname = \"mylib\"\nversion = \"0.1.0\"\n\n[build]\nsource_dir = \"src\"\noutput_dir = \"build\"\ntarget = \"c\"\n")
        add_dependency(project, "mylib", path=str(lib_dir))
        content = (project / "nlpl.toml").read_text()
        assert "mylib" in content
        assert "path" in content

    def test_add_duplicate_updates(self, tmp_path):
        """Adding a package that already exists updates it in-place."""
        project = _minimal_project_dir(tmp_path)
        add_dependency(project, "alpha@^1.0")
        # Second add with different version should update, not raise
        add_dependency(project, "alpha@^2.0")
        content = (project / "nlpl.toml").read_text()
        assert "alpha" in content
        assert "^2.0" in content

    def test_add_invalid_name_raises(self, tmp_path):
        project = _minimal_project_dir(tmp_path)
        with pytest.raises((ValueError, SystemExit)):
            add_dependency(project, "invalid name with spaces")


class TestRemoveDependency:

    def test_remove_existing_dependency(self, tmp_path):
        project = _minimal_project_dir(tmp_path)
        add_dependency(project, "removeme@^1.0")
        remove_dependency(project, "removeme")
        content = (project / "nlpl.toml").read_text()
        assert "removeme" not in content

    def test_remove_nonexistent_raises(self, tmp_path):
        project = _minimal_project_dir(tmp_path)
        with pytest.raises((ValueError, SystemExit)):
            remove_dependency(project, "ghost")

    def test_remove_dev_dependency(self, tmp_path):
        project = _minimal_project_dir(tmp_path)
        add_dependency(project, "devonly@^1.0", dev=True)
        remove_dependency(project, "devonly", dev=True)
        content = (project / "nlpl.toml").read_text()
        assert "devonly" not in content


# ---------------------------------------------------------------------------
# BuildSystem.clean tests (uses a real temp project dir)
# ---------------------------------------------------------------------------

class TestBuildSystemClean:

    def _make_project(self, tmp_path: Path) -> tuple:
        src_dir = tmp_path / "src"
        out_dir = tmp_path / "build"
        src_dir.mkdir()
        out_dir.mkdir()
        (src_dir / "main.nlpl").write_text("function main\n    print text \"hi\"\nend\n")
        artefact = out_dir / "main.o"
        artefact.write_bytes(b"\x00fake")
        config = _minimal_project_config(
            src_dir=str(src_dir), out_dir=str(out_dir)
        )
        return config, out_dir

    def test_clean_removes_output_directory(self, tmp_path):
        config, out_dir = self._make_project(tmp_path)
        bs = BuildSystem(config)
        bs.clean()
        assert not out_dir.exists()

    def test_clean_idempotent(self, tmp_path):
        config, out_dir = self._make_project(tmp_path)
        bs = BuildSystem(config)
        bs.clean()
        bs.clean()  # second call must not raise

    def test_clean_removes_cache_file(self, tmp_path):
        config, out_dir = self._make_project(tmp_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        cache_file = out_dir / ".build_cache.json"
        cache_file.write_text('{"version":1,"entries":[]}')
        bs = BuildSystem(config)
        bs.clean()
        assert not cache_file.exists()


# ---------------------------------------------------------------------------
# ConfigLoader.load path (using get_profile fallback)
# ---------------------------------------------------------------------------

class TestGetProfileFallback:

    def test_unknown_profile_name_returns_dev(self):
        config = _minimal_project_config()
        prof = config.get_profile("nonexistent_profile")
        assert prof.name == "dev"
        assert prof.optimization == 0

    def test_explicit_release_without_custom_profiles(self):
        config = _minimal_project_config()
        prof = config.get_profile("release")
        assert prof.name == "release"
        assert prof.optimization == 3

    def test_get_profile_uses_build_profile_as_default(self):
        config = _minimal_project_config()
        config.build.profile = "dev"
        prof = config.get_profile()
        assert prof.optimization == 0


# ---------------------------------------------------------------------------
# ProfileConfig constants test
# ---------------------------------------------------------------------------

class TestBuiltinProfiles:

    def test_dev_profile_values(self):
        assert _PROFILE_DEV.optimization == 0
        assert _PROFILE_DEV.debug_info is True
        assert _PROFILE_DEV.debug_assertions is True
        assert _PROFILE_DEV.lto is False
        assert _PROFILE_DEV.incremental is True
        assert _PROFILE_DEV.strip is False

    def test_release_profile_values(self):
        assert _PROFILE_RELEASE.optimization == 3
        assert _PROFILE_RELEASE.debug_info is False
        assert _PROFILE_RELEASE.debug_assertions is False
        assert _PROFILE_RELEASE.lto is True
        assert _PROFILE_RELEASE.incremental is False
        assert _PROFILE_RELEASE.strip is True

    def test_dev_and_release_differ(self):
        assert _PROFILE_DEV.optimization != _PROFILE_RELEASE.optimization
        assert _PROFILE_DEV.debug_info != _PROFILE_RELEASE.debug_info


# ---------------------------------------------------------------------------
# Build script support (build_script.py)
# ---------------------------------------------------------------------------

class TestParseDirectives:
    """Unit tests for _parse_directives() — a pure function."""

    def test_empty_stdout_produces_no_directives(self):
        d, plain = _parse_directives("")
        assert d.rerun_if_changed == []
        assert d.rerun_if_env_changed == []
        assert d.cfg_flags == []
        assert d.warnings == []
        assert d.errors == []
        assert plain == []

    def test_plain_lines_not_classified_as_directives(self):
        stdout = "Hello build\nSome status\n"
        d, plain = _parse_directives(stdout)
        assert plain == ["Hello build", "Some status"]
        assert d.cfg_flags == []

    def test_rerun_if_changed_parsed(self):
        _, _ = _parse_directives("")
        d, _ = _parse_directives("nlpl:rerun-if-changed=config.h\nnlpl:rerun-if-changed=src/gen.c\n")
        assert d.rerun_if_changed == ["config.h", "src/gen.c"]

    def test_rerun_if_env_changed_parsed(self):
        d, _ = _parse_directives("nlpl:rerun-if-env-changed=CC\nnlpl:rerun-if-env-changed=TARGET\n")
        assert d.rerun_if_env_changed == ["CC", "TARGET"]

    def test_cfg_flag_parsed(self):
        d, plain = _parse_directives("nlpl:cfg=simd_avx2\nnlpl:cfg=feature_x\n")
        assert d.cfg_flags == ["simd_avx2", "feature_x"]
        assert plain == []

    def test_warning_parsed(self):
        d, _ = _parse_directives("nlpl:warning=deprecated API used\n")
        assert d.warnings == ["deprecated API used"]

    def test_error_parsed(self):
        d, _ = _parse_directives("nlpl:error=missing header foo.h\n")
        assert d.errors == ["missing header foo.h"]

    def test_mixed_stdout(self):
        stdout = (
            "Starting code generation\n"
            "nlpl:cfg=generated_bindings\n"
            "nlpl:rerun-if-changed=schema.proto\n"
            "Generated 42 binding files\n"
            "nlpl:warning=protobuf v2 used; v3 recommended\n"
        )
        d, plain = _parse_directives(stdout)
        assert d.cfg_flags == ["generated_bindings"]
        assert d.rerun_if_changed == ["schema.proto"]
        assert d.warnings == ["protobuf v2 used; v3 recommended"]
        assert plain == ["Starting code generation", "Generated 42 binding files"]

    def test_cfg_flag_empty_string_ignored(self):
        # "nlpl:cfg=" with nothing after the = produces no flag
        d, _ = _parse_directives("nlpl:cfg=\n")
        assert d.cfg_flags == []


class TestBuildScriptCache:
    """Unit tests for BuildScriptCache."""

    def test_needs_rerun_true_when_no_cache_file(self, tmp_path):
        cache = BuildScriptCache(tmp_path / "state.json")
        # Any path — cache is empty so always returns True
        assert cache.needs_rerun("/nonexistent/script.nlpl") is True

    def test_needs_rerun_true_when_script_hash_changes(self, tmp_path):
        script = tmp_path / "build.nlpl"
        script.write_text("print text \"v1\"\n")
        cache_path = tmp_path / "state.json"
        cache = BuildScriptCache(cache_path)

        # Save state for v1
        directives = BuildScriptDirectives()
        cache.save(_file_sha256(str(script)), directives)

        # Modify the script
        script.write_text("print text \"v2\"\n")
        cache2 = BuildScriptCache(cache_path)
        assert cache2.needs_rerun(str(script)) is True

    def test_needs_rerun_false_when_unchanged(self, tmp_path):
        script = tmp_path / "build.nlpl"
        script.write_text("print text \"v1\"\n")
        cache_path = tmp_path / "state.json"
        cache = BuildScriptCache(cache_path)
        directives = BuildScriptDirectives()
        cache.save(_file_sha256(str(script)), directives)

        cache2 = BuildScriptCache(cache_path)
        assert cache2.needs_rerun(str(script)) is False

    def test_needs_rerun_true_when_watched_file_changes(self, tmp_path):
        script = tmp_path / "build.nlpl"
        script.write_text("print text \"ok\"\n")
        watched = tmp_path / "config.h"
        watched.write_text("#define VERSION 1\n")

        cache_path = tmp_path / "state.json"
        cache = BuildScriptCache(cache_path)
        directives = BuildScriptDirectives(rerun_if_changed=[str(watched)])
        cache.save(_file_sha256(str(script)), directives)

        # Change the watched file
        watched.write_text("#define VERSION 2\n")
        cache2 = BuildScriptCache(cache_path)
        assert cache2.needs_rerun(str(script)) is True

    def test_needs_rerun_true_when_env_var_changes(self, tmp_path, monkeypatch):
        script = tmp_path / "build.nlpl"
        script.write_text("print text \"ok\"\n")

        monkeypatch.setenv("TEST_CC", "gcc")
        cache_path = tmp_path / "state.json"
        cache = BuildScriptCache(cache_path)
        directives = BuildScriptDirectives(rerun_if_env_changed=["TEST_CC"])
        cache.save(_file_sha256(str(script)), directives)

        # Simulate env var change
        monkeypatch.setenv("TEST_CC", "clang")
        cache2 = BuildScriptCache(cache_path)
        assert cache2.needs_rerun(str(script)) is True

    def test_needs_rerun_false_when_env_var_unchanged(self, tmp_path, monkeypatch):
        script = tmp_path / "build.nlpl"
        script.write_text("print text \"ok\"\n")

        monkeypatch.setenv("TEST_CC", "gcc")
        cache_path = tmp_path / "state.json"
        cache = BuildScriptCache(cache_path)
        directives = BuildScriptDirectives(rerun_if_env_changed=["TEST_CC"])
        cache.save(_file_sha256(str(script)), directives)

        cache2 = BuildScriptCache(cache_path)
        assert cache2.needs_rerun(str(script)) is False

    def test_clear_removes_cache_file(self, tmp_path):
        script = tmp_path / "build.nlpl"
        script.write_text("x\n")
        cache_path = tmp_path / "state.json"
        cache = BuildScriptCache(cache_path)
        cache.save(_file_sha256(str(script)), BuildScriptDirectives())
        assert cache_path.exists()
        cache.clear()
        assert not cache_path.exists()

    def test_clear_on_empty_cache_is_safe(self, tmp_path):
        cache = BuildScriptCache(tmp_path / "state.json")
        cache.clear()  # must not raise

    def test_corrupted_cache_treated_as_missing(self, tmp_path):
        cache_path = tmp_path / "state.json"
        cache_path.write_text("not json {{{")
        script = tmp_path / "build.nlpl"
        script.write_text("x\n")
        cache = BuildScriptCache(cache_path)
        assert cache.needs_rerun(str(script)) is True


class TestBuildScriptRunnerUnit:
    """Unit tests for run_build_script() that do NOT require the NLPL interpreter."""

    def test_returns_success_false_on_timeout(self, tmp_path, monkeypatch):
        """A TimeoutExpired from subprocess is turned into a failed result."""
        import subprocess
        script = tmp_path / "build.nlpl"
        script.write_text("print text \"x\"\n")

        def _fake_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="test", timeout=300)

        monkeypatch.setattr(subprocess, "run", _fake_run)
        result = run_build_script(
            script_path=str(script),
            manifest_dir=str(tmp_path),
            out_dir=str(tmp_path),
            pkg_name="test",
            pkg_version="0.1.0",
            profile_name="dev",
            opt_level=0,
            debug_info=True,
            jobs=1,
            force=True,
        )
        assert result.success is False
        assert any("timed out" in e.lower() for e in result.directives.errors)

    def test_returns_success_false_on_oserror(self, tmp_path, monkeypatch):
        import subprocess
        script = tmp_path / "build.nlpl"
        script.write_text("print text \"x\"\n")

        def _fake_run(*args, **kwargs):
            raise OSError("No such file")

        monkeypatch.setattr(subprocess, "run", _fake_run)
        result = run_build_script(
            script_path=str(script),
            manifest_dir=str(tmp_path),
            out_dir=str(tmp_path),
            pkg_name="test",
            pkg_version="0.1.0",
            profile_name="dev",
            opt_level=0,
            debug_info=True,
            jobs=1,
            force=True,
        )
        assert result.success is False
        assert result.directives.errors

    def test_nonzero_exit_becomes_error(self, tmp_path, monkeypatch):
        import subprocess
        script = tmp_path / "build.nlpl"
        script.write_text("print text \"x\"\n")

        class _FakeProc:
            returncode = 1
            stdout = ""
            stderr = "kaboom"

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _FakeProc())
        result = run_build_script(
            script_path=str(script),
            manifest_dir=str(tmp_path),
            out_dir=str(tmp_path),
            pkg_name="pkg",
            pkg_version="1.0",
            profile_name="release",
            opt_level=3,
            debug_info=False,
            jobs=4,
            force=True,
        )
        assert result.success is False
        assert "kaboom" in result.directives.errors[0]

    def test_error_directive_overrides_rc_zero(self, tmp_path, monkeypatch):
        """nlpl:error= in stdout must fail the build even if the process exits 0."""
        import subprocess
        script = tmp_path / "build.nlpl"
        script.write_text("print text \"x\"\n")

        class _FakeProc:
            returncode = 0
            stdout = "nlpl:error=required header not found"
            stderr = ""

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _FakeProc())
        result = run_build_script(
            script_path=str(script),
            manifest_dir=str(tmp_path),
            out_dir=str(tmp_path),
            pkg_name="pkg",
            pkg_version="1.0",
            profile_name="dev",
            opt_level=0,
            debug_info=True,
            jobs=1,
            force=True,
        )
        assert result.success is False
        assert result.directives.errors == ["required header not found"]

    def test_cfg_directive_in_result(self, tmp_path, monkeypatch):
        import subprocess
        script = tmp_path / "build.nlpl"
        script.write_text("x\n")

        class _FakeProc:
            returncode = 0
            stdout = "nlpl:cfg=avx2_enabled\nnlpl:cfg=neon_enabled\n"
            stderr = ""

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _FakeProc())
        result = run_build_script(
            script_path=str(script),
            manifest_dir=str(tmp_path),
            out_dir=str(tmp_path),
            pkg_name="p",
            pkg_version="0.1",
            profile_name="dev",
            opt_level=0,
            debug_info=True,
            jobs=1,
            force=True,
        )
        assert result.success is True
        assert "avx2_enabled" in result.directives.cfg_flags
        assert "neon_enabled" in result.directives.cfg_flags

    def test_cache_skip_when_unchanged(self, tmp_path, monkeypatch):
        """run_build_script returns cached success without calling subprocess."""
        import subprocess
        script = tmp_path / "build.nlpl"
        script.write_text("x\n")
        out_dir = tmp_path / "build"
        out_dir.mkdir()

        call_count = [0]

        class _FakeProc:
            returncode = 0
            stdout = ""
            stderr = ""

        def _counting_run(*a, **kw):
            call_count[0] += 1
            return _FakeProc()

        monkeypatch.setattr(subprocess, "run", _counting_run)

        # First call: subprocess used
        run_build_script(
            script_path=str(script),
            manifest_dir=str(tmp_path),
            out_dir=str(out_dir),
            pkg_name="p",
            pkg_version="0.1",
            profile_name="dev",
            opt_level=0,
            debug_info=True,
            jobs=1,
            force=True,  # force first run
        )
        assert call_count[0] == 1

        # Second call without force: should use cache (no subprocess)
        result = run_build_script(
            script_path=str(script),
            manifest_dir=str(tmp_path),
            out_dir=str(out_dir),
            pkg_name="p",
            pkg_version="0.1",
            profile_name="dev",
            opt_level=0,
            debug_info=True,
            jobs=1,
            force=False,
        )
        assert call_count[0] == 1  # subprocess NOT called again
        assert result.success is True

    def test_plain_output_lines_captured(self, tmp_path, monkeypatch):
        import subprocess
        script = tmp_path / "build.nlpl"
        script.write_text("x\n")

        class _FakeProc:
            returncode = 0
            stdout = "Building generated bindings\nnlpl:cfg=bindings\nDone.\n"
            stderr = ""

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _FakeProc())
        result = run_build_script(
            script_path=str(script),
            manifest_dir=str(tmp_path),
            out_dir=str(tmp_path),
            pkg_name="p",
            pkg_version="0.1",
            profile_name="dev",
            opt_level=0,
            debug_info=True,
            jobs=1,
            force=True,
        )
        assert "Building generated bindings" in result.output_lines
        assert "Done." in result.output_lines
        # Directive line must NOT appear in plain output
        assert all("nlpl:cfg" not in ln for ln in result.output_lines)


class TestBuildScriptBuilderIntegration:
    """Tests that verify BuildSystem correctly invokes and reacts to build scripts."""

    def _make_project(self, tmp_path, build_script_content=None, build_script_cfg=None):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.nlpl").write_text(
            'function main\n    print text "hello"\nend\n'
        )
        out_dir = tmp_path / "build"

        if build_script_content is not None:
            (tmp_path / "build.nlpl").write_text(build_script_content)

        config = _minimal_project_config(
            src_dir=str(src_dir), out_dir=str(out_dir)
        )
        config.manifest_dir = str(tmp_path)
        if build_script_cfg is not None:
            config.build.build_script = build_script_cfg
        return config

    def test_no_build_script_file_no_run(self, tmp_path, monkeypatch):
        """When build.nlpl is absent, _run_build_script_if_present returns None."""
        config = self._make_project(tmp_path)  # no build.nlpl
        bs = BuildSystem(config)
        from nlpl.tooling.config import _PROFILE_DEV
        result = bs._run_build_script_if_present(
            _PROFILE_DEV, "dev", str(tmp_path / "build"), 1, False
        )
        assert result is None

    def test_explicitly_disabled_build_script(self, tmp_path):
        """build_script = '' disables the hook even when build.nlpl exists."""
        config = self._make_project(
            tmp_path,
            build_script_content='print text "should not run"\n',
            build_script_cfg="",  # disabled
        )
        bs = BuildSystem(config)
        from nlpl.tooling.config import _PROFILE_DEV
        result = bs._run_build_script_if_present(
            _PROFILE_DEV, "dev", str(tmp_path / "build"), 1, False
        )
        assert result is None

    def test_missing_explicit_script_is_error(self, tmp_path):
        """When build_script points to a non-existent file, result.success is False."""
        config = self._make_project(
            tmp_path,
            build_script_cfg="nonexistent_script.nlpl",
        )
        bs = BuildSystem(config)
        from nlpl.tooling.config import _PROFILE_DEV
        (tmp_path / "build").mkdir(exist_ok=True)
        result = bs._run_build_script_if_present(
            _PROFILE_DEV, "dev", str(tmp_path / "build"), 1, False
        )
        assert result is not None
        assert result.success is False
        assert result.directives.errors

    def test_cfg_flag_from_script_added_to_features(self, tmp_path, monkeypatch):
        """nlpl:cfg= directives emitted by the script appear in active_features."""
        import subprocess
        config = self._make_project(
            tmp_path, build_script_content='print text "x"\n'
        )
        bs = BuildSystem(config)
        (tmp_path / "build").mkdir(exist_ok=True)

        class _FakeProc:
            returncode = 0
            stdout = "nlpl:cfg=my_generated_feature\n"
            stderr = ""

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _FakeProc())

        active = ["existing_flag"]
        # Simulate what _build_internal does after receiving script_result
        from nlpl.tooling.config import _PROFILE_DEV
        result = bs._run_build_script_if_present(
            _PROFILE_DEV, "dev", str(tmp_path / "build"), 1, True
        )
        assert result is not None and result.success
        for flag in result.directives.cfg_flags:
            if flag not in active:
                active.append(flag)
        assert "my_generated_feature" in active
        assert "existing_flag" in active  # original flag preserved

    def test_build_script_error_prevents_compilation(self, tmp_path, monkeypatch):
        """A build script that emits nlpl:error= must cause build() to return False."""
        import subprocess
        config = self._make_project(
            tmp_path, build_script_content='print text "x"\n'
        )
        bs = BuildSystem(config)

        class _FakeProc:
            returncode = 0
            stdout = "nlpl:error=missing required library"
            stderr = ""

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _FakeProc())
        success = bs.build()
        assert success is False

    def test_config_build_script_field_parsed_from_toml(self, tmp_path):
        """build_script setting in [build] is parsed by ConfigLoader."""
        toml = (
            '[package]\nname = "mypkg"\nversion = "1.0.0"\n'
            '[build]\nbuild_script = "scripts/prebuild.nlpl"\n'
        )
        toml_path = tmp_path / "nlpl.toml"
        toml_path.write_text(toml)
        config = ConfigLoader.load(str(toml_path))
        assert config.build.build_script == "scripts/prebuild.nlpl"
        assert config.manifest_dir == str(tmp_path)

    def test_config_build_script_absent_defaults_none(self, tmp_path):
        """When build_script is not in toml, it defaults to None (auto-detect)."""
        toml = '[package]\nname = "x"\nversion = "0.1.0"\n'
        toml_path = tmp_path / "nlpl.toml"
        toml_path.write_text(toml)
        config = ConfigLoader.load(str(toml_path))
        assert config.build.build_script is None

    def test_config_build_script_disabled_empty_string(self, tmp_path):
        """build_script = "" in toml disables the hook."""
        toml = (
            '[package]\nname = "x"\nversion = "0.1.0"\n'
            '[build]\nbuild_script = ""\n'
        )
        toml_path = tmp_path / "nlpl.toml"
        toml_path.write_text(toml)
        config = ConfigLoader.load(str(toml_path))
        assert config.build.build_script == ""

    def test_manifest_dir_set_by_config_loader(self, tmp_path):
        toml = '[package]\nname = "x"\nversion = "0.1.0"\n'
        toml_path = tmp_path / "nlpl.toml"
        toml_path.write_text(toml)
        config = ConfigLoader.load(str(toml_path))
        assert config.manifest_dir == str(tmp_path)
