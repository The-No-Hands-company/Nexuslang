"""
NLPL Project Configuration

Handles nlpl.toml project files, dependencies, and build configurations.
"""

import os
import tomli
import tomli_w
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class ProjectDependency:
    """External dependency specification."""
    name: str
    version: str
    source: str = "registry"  # registry, git, path
    path: Optional[str] = None
    git_url: Optional[str] = None
    git_ref: Optional[str] = None


@dataclass
class BuildConfig:
    """Build configuration options."""
    optimization_level: int = 0  # 0, 1, 2, 3
    debug_info: bool = True
    warnings_as_errors: bool = False
    target_triple: Optional[str] = None
    output_dir: str = "build"
    incremental: bool = True
    # Parallel compilation (0 = auto-detect CPU count, 1 = serial)
    parallel_jobs: int = 0
    # Link-time optimization: "disabled" | "thin" | "full"
    lto: str = "disabled"
    # Optional sysroot override for cross-compilation
    sysroot: Optional[str] = None


@dataclass
class Project:
    """
    NLPL Project configuration.
    
    Manages project metadata, dependencies, and build settings.
    """
    name: str
    version: str
    authors: List[str] = field(default_factory=list)
    description: str = ""
    license: str = ""
    
    # Source configuration
    src_dir: str = "src"
    main_file: str = "main.nlpl"
    
    # Dependencies
    dependencies: Dict[str, ProjectDependency] = field(default_factory=dict)
    dev_dependencies: Dict[str, ProjectDependency] = field(default_factory=dict)
    
    # Build configurations
    build: BuildConfig = field(default_factory=BuildConfig)
    
    # Project root
    root_dir: Path = field(default_factory=Path.cwd)
    
    @classmethod
    def from_toml(cls, path: Path) -> "Project":
        """Load project from nlpl.toml file."""
        with open(path, "rb") as f:
            data = tomli.load(f)
        
        # Parse package info
        package = data.get("package", {})
        name = package.get("name", "nlpl-project")
        version = package.get("version", "0.1.0")
        authors = package.get("authors", [])
        description = package.get("description", "")
        license = package.get("license", "")
        
        # Parse source config
        src = data.get("source", {})
        src_dir = src.get("dir", "src")
        main_file = src.get("main", "main.nlpl")
        
        # Parse dependencies
        deps = {}
        for name, spec in data.get("dependencies", {}).items():
            if isinstance(spec, str):
                deps[name] = ProjectDependency(name, spec)
            elif isinstance(spec, dict):
                deps[name] = ProjectDependency(
                    name=name,
                    version=spec.get("version", "*"),
                    source=spec.get("source", "registry"),
                    path=spec.get("path"),
                    git_url=spec.get("git"),
                    git_ref=spec.get("ref", "main")
                )
        
        dev_deps = {}
        for name, spec in data.get("dev-dependencies", {}).items():
            if isinstance(spec, str):
                dev_deps[name] = ProjectDependency(name, spec)
            elif isinstance(spec, dict):
                dev_deps[name] = ProjectDependency(
                    name=name,
                    version=spec.get("version", "*"),
                    source=spec.get("source", "registry"),
                    path=spec.get("path"),
                    git_url=spec.get("git"),
                    git_ref=spec.get("ref", "main")
                )
        
        # Parse build config
        build_data = data.get("build", {})
        build = BuildConfig(
            optimization_level=build_data.get("optimization_level", 0),
            debug_info=build_data.get("debug_info", True),
            warnings_as_errors=build_data.get("warnings_as_errors", False),
            target_triple=build_data.get("target_triple"),
            output_dir=build_data.get("output_dir", "build"),
            incremental=build_data.get("incremental", True),
            parallel_jobs=build_data.get("parallel_jobs", 0),
            lto=build_data.get("lto", "disabled"),
            sysroot=build_data.get("sysroot"),
        )
        
        return cls(
            name=name,
            version=version,
            authors=authors,
            description=description,
            license=license,
            src_dir=src_dir,
            main_file=main_file,
            dependencies=deps,
            dev_dependencies=dev_deps,
            build=build,
            root_dir=path.parent
        )
    
    def to_toml(self, path: Path) -> None:
        """Save project to nlpl.toml file."""
        data = {
            "package": {
                "name": self.name,
                "version": self.version,
                "authors": self.authors,
                "description": self.description,
                "license": self.license,
            },
            "source": {
                "dir": self.src_dir,
                "main": self.main_file,
            },
            "dependencies": {},
            "dev-dependencies": {},
            "build": {
                "optimization_level": self.build.optimization_level,
                "debug_info": self.build.debug_info,
                "warnings_as_errors": self.build.warnings_as_errors,
                "output_dir": self.build.output_dir,
                "incremental": self.build.incremental,
                "parallel_jobs": self.build.parallel_jobs,
                "lto": self.build.lto,
            }
        }

        if self.build.target_triple:
            data["build"]["target_triple"] = self.build.target_triple

        if self.build.sysroot:
            data["build"]["sysroot"] = self.build.sysroot
        
        # Add dependencies
        for name, dep in self.dependencies.items():
            if dep.source == "registry":
                data["dependencies"][name] = dep.version
            else:
                dep_data = {"version": dep.version, "source": dep.source}
                if dep.path:
                    dep_data["path"] = dep.path
                if dep.git_url:
                    dep_data["git"] = dep.git_url
                    dep_data["ref"] = dep.git_ref
                data["dependencies"][name] = dep_data
        
        # Add dev dependencies
        for name, dep in self.dev_dependencies.items():
            if dep.source == "registry":
                data["dev-dependencies"][name] = dep.version
            else:
                dep_data = {"version": dep.version, "source": dep.source}
                if dep.path:
                    dep_data["path"] = dep.path
                if dep.git_url:
                    dep_data["git"] = dep.git_url
                    dep_data["ref"] = dep.git_ref
                data["dev-dependencies"][name] = dep_data
        
        with open(path, "wb") as f:
            tomli_w.dump(data, f)
    
    @classmethod
    def init(cls, path: Path, name: str) -> "Project":
        """Initialize a new NLPL project."""
        project = cls(
            name=name,
            version="0.1.0",
            root_dir=path
        )
        
        # Create directory structure
        (path / "src").mkdir(exist_ok=True)
        (path / "build").mkdir(exist_ok=True)
        (path / "tests").mkdir(exist_ok=True)
        
        # Create main.nlpl
        main_path = path / "src" / "main.nlpl"
        if not main_path.exists():
            main_path.write_text(
                '# NLPL Project\n\n'
                'function main returns Integer\n'
                '    print text "Hello from NLPL!"\n'
                '    return 0\n'
            )
        
        # Create nlpl.toml
        toml_path = path / "nlpl.toml"
        project.to_toml(toml_path)
        
        # Create .gitignore
        gitignore_path = path / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text(
                'build/\n'
                '*.o\n'
                '*.ll\n'
                '*.s\n'
                '__pycache__/\n'
                '.nlpl-cache/\n'
            )
        
        return project
    
    def get_source_files(self) -> List[Path]:
        """Get all NLPL source files in the project."""
        src_path = self.root_dir / self.src_dir
        if not src_path.exists():
            return []
        
        files = []
        for ext in ['.nlpl']:
            files.extend(src_path.rglob(f'*{ext}'))
        return files
    
    def get_main_file(self) -> Path:
        """Get the main entry point file."""
        return self.root_dir / self.src_dir / self.main_file
    
    def get_output_dir(self) -> Path:
        """Get the build output directory."""
        return self.root_dir / self.build.output_dir
    
    def get_cache_dir(self) -> Path:
        """Get the build cache directory."""
        cache_dir = self.root_dir / ".nlpl-cache"
        cache_dir.mkdir(exist_ok=True)
        return cache_dir
