"""
NLPL Build System - Manifest Parser

Parses and validates nlpl.toml manifest files.
Provides structured access to project configuration.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


try:
    import tomli as toml  # Python 3.11+
except ImportError:
    try:
        import toml  # Fallback for older Python
    except ImportError:
        raise ImportError(
            "TOML parser not available. Install with: pip install tomli"
        )


class CrateType(Enum):
    """Types of crates (compilation outputs)."""
    LIB = "lib"  # NLPL library
    STATICLIB = "staticlib"  # Static C library (.a)
    DYLIB = "dylib"  # Dynamic C library (.so/.dll)
    CDYLIB = "cdylib"  # C-compatible dynamic library
    BIN = "bin"  # Executable binary


class PanicStrategy(Enum):
    """Panic handling strategies."""
    UNWIND = "unwind"  # Unwind stack on panic
    ABORT = "abort"  # Abort process on panic


@dataclass
class Dependency:
    """Represents a package dependency."""
    name: str
    version_req: Optional[str] = None  # Version constraint
    path: Optional[str] = None  # Local path
    git: Optional[str] = None  # Git repository
    branch: Optional[str] = None  # Git branch
    tag: Optional[str] = None  # Git tag
    rev: Optional[str] = None  # Git revision
    features: List[str] = field(default_factory=list)
    default_features: bool = True
    optional: bool = False
    package: Optional[str] = None  # Rename dependency


@dataclass
class BinaryTarget:
    """Binary executable target."""
    name: str
    path: str
    required_features: List[str] = field(default_factory=list)


@dataclass
class LibraryTarget:
    """Library target configuration."""
    name: str
    path: str
    crate_type: List[CrateType] = field(default_factory=lambda: [CrateType.LIB])


@dataclass
class BuildProfile:
    """Build profile configuration (debug, release, custom)."""
    name: str
    opt_level: int = 0  # 0-3
    debug: bool = True
    debug_assertions: bool = True
    overflow_checks: bool = True
    lto: Union[bool, str] = False  # False, True, "thin"
    panic: PanicStrategy = PanicStrategy.UNWIND
    incremental: bool = True
    codegen_units: int = 256
    strip: Union[bool, str] = False  # False, True, "symbols"
    
    def __post_init__(self):
        if isinstance(self.panic, str):
            self.panic = PanicStrategy(self.panic)


@dataclass
class PackageMetadata:
    """Project metadata from [package] section."""
    name: str
    version: str
    authors: List[str] = field(default_factory=list)
    license: Optional[str] = None
    description: Optional[str] = None
    repository: Optional[str] = None
    homepage: Optional[str] = None
    documentation: Optional[str] = None
    readme: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    edition: str = "2026"
    build: Optional[str] = None  # Build script path


@dataclass
class Workspace:
    """Workspace configuration for multi-package projects."""
    members: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    default_members: List[str] = field(default_factory=list)


class Manifest:
    """Parsed nlpl.toml manifest with validation."""
    
    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.project_root = self.path.parent
        
        if not self.path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.path}")
        
        # Parse TOML
        with open(self.path, 'rb') as f:
            self.data = toml.load(f)
        
        # Validate and extract sections
        self._validate()
        self.package = self._parse_package()
        self.dependencies = self._parse_dependencies('dependencies')
        self.dev_dependencies = self._parse_dependencies('dev-dependencies')
        self.build_dependencies = self._parse_dependencies('build-dependencies')
        self.binary_targets = self._parse_binary_targets()
        self.library_target = self._parse_library_target()
        self.features = self._parse_features()
        self.profiles = self._parse_profiles()
        self.workspace = self._parse_workspace()
        self.target_specific_deps = self._parse_target_specific_deps()
    
    def _validate(self):
        """Validate required fields and structure."""
        # Allow workspace-only manifests (no [package] section)
        if 'package' not in self.data and 'workspace' not in self.data:
            raise ValueError("Manifest must have either [package] or [workspace] section")
        
        if 'package' not in self.data:
            # Workspace-only manifest, skip package validation
            return
        
        pkg = self.data['package']
        if 'name' not in pkg:
            raise ValueError("Missing required field 'name' in [package]")
        if 'version' not in pkg:
            raise ValueError("Missing required field 'version' in [package]")
        
        # Validate package name
        name = pkg['name']
        if not re.match(r'^[a-z0-9_-]+$', name):
            raise ValueError(
                f"Invalid package name '{name}'. "
                "Must be lowercase with hyphens or underscores."
            )
        
        # Validate version (basic semver check)
        version = pkg['version']
        if not re.match(r'^\d+\.\d+\.\d+', version):
            raise ValueError(
                f"Invalid version '{version}'. "
                "Must be semantic version (x.y.z)."
            )
    
    def _parse_package(self) -> Optional[PackageMetadata]:
        """Parse [package] section."""
        if 'package' not in self.data:
            return None  # Workspace-only manifest
        
        pkg = self.data['package']
        return PackageMetadata(
            name=pkg['name'],
            version=pkg['version'],
            authors=pkg.get('authors', []),
            license=pkg.get('license'),
            description=pkg.get('description'),
            repository=pkg.get('repository'),
            homepage=pkg.get('homepage'),
            documentation=pkg.get('documentation'),
            readme=pkg.get('readme'),
            keywords=pkg.get('keywords', []),
            categories=pkg.get('categories', []),
            edition=pkg.get('edition', '2026'),
            build=pkg.get('build')
        )
    
    def _parse_dependencies(self, section: str) -> Dict[str, Dependency]:
        """Parse dependency section."""
        deps = {}
        if section not in self.data:
            return deps
        
        for name, spec in self.data[section].items():
            if isinstance(spec, str):
                # Simple version: "1.0"
                deps[name] = Dependency(name=name, version_req=spec)
            elif isinstance(spec, dict):
                # Complex dependency
                deps[name] = Dependency(
                    name=name,
                    version_req=spec.get('version'),
                    path=spec.get('path'),
                    git=spec.get('git'),
                    branch=spec.get('branch'),
                    tag=spec.get('tag'),
                    rev=spec.get('rev'),
                    features=spec.get('features', []),
                    default_features=spec.get('default-features', True),
                    optional=spec.get('optional', False),
                    package=spec.get('package')
                )
            else:
                raise ValueError(f"Invalid dependency spec for '{name}'")
        
        return deps
    
    def _parse_binary_targets(self) -> List[BinaryTarget]:
        """Parse [[bin]] sections."""
        targets = []
        
        # Single [bin] or multiple [[bin]]
        if 'bin' in self.data:
            bins = self.data['bin']
            if isinstance(bins, dict):
                bins = [bins]
            
            for bin_spec in bins:
                targets.append(BinaryTarget(
                    name=bin_spec['name'],
                    path=bin_spec.get('path', f"src/bin/{bin_spec['name']}.nlpl"),
                    required_features=bin_spec.get('required-features', [])
                ))
        
        # Auto-discover binaries in src/bin/
        bin_dir = self.project_root / 'src' / 'bin'
        if bin_dir.exists():
            for nlpl_file in bin_dir.glob('*.nlpl'):
                name = nlpl_file.stem
                # Don't add if already explicitly defined
                if not any(t.name == name for t in targets):
                    targets.append(BinaryTarget(
                        name=name,
                        path=f"src/bin/{nlpl_file.name}"
                    ))
        
        return targets
    
    def _parse_library_target(self) -> Optional[LibraryTarget]:
        """Parse [lib] section."""
        if 'lib' not in self.data:
            # Check for default lib.nlpl
            lib_path = self.project_root / 'src' / 'lib.nlpl'
            if lib_path.exists() and self.package:
                return LibraryTarget(
                    name=self.package.name.replace('-', '_'),
                    path='src/lib.nlpl'
                )
            return None
        
        lib = self.data['lib']
        crate_types = []
        for ct in lib.get('crate-type', ['lib']):
            crate_types.append(CrateType(ct))
        
        default_name = self.package.name.replace('-', '_') if self.package else 'lib'
        return LibraryTarget(
            name=lib.get('name', default_name),
            path=lib.get('path', 'src/lib.nlpl'),
            crate_type=crate_types
        )
    
    def _parse_features(self) -> Dict[str, List[str]]:
        """Parse [features] section."""
        if 'features' not in self.data:
            return {}
        return dict(self.data['features'])
    
    def _parse_profiles(self) -> Dict[str, BuildProfile]:
        """Parse [profile.*] sections."""
        profiles = {}
        
        # Default profiles
        profiles['dev'] = BuildProfile(
            name='dev',
            opt_level=0,
            debug=True,
            debug_assertions=True,
            overflow_checks=True,
            lto=False,
            panic=PanicStrategy.UNWIND,
            incremental=True,
            codegen_units=256,
            strip=False
        )
        
        profiles['release'] = BuildProfile(
            name='release',
            opt_level=3,
            debug=False,
            debug_assertions=False,
            overflow_checks=False,
            lto=True,
            panic=PanicStrategy.ABORT,
            incremental=False,
            codegen_units=16,
            strip=True
        )
        
        # Parse custom profiles from manifest
        if 'profile' in self.data:
            for profile_name, profile_data in self.data['profile'].items():
                # Check if it inherits from another profile
                inherits = profile_data.get('inherits')
                if inherits and inherits in profiles:
                    # Start with inherited profile
                    base_profile = profiles[inherits]
                    profile = BuildProfile(
                        name=profile_name,
                        opt_level=profile_data.get('opt-level', base_profile.opt_level),
                        debug=profile_data.get('debug', base_profile.debug),
                        debug_assertions=profile_data.get('debug-assertions', base_profile.debug_assertions),
                        overflow_checks=profile_data.get('overflow-checks', base_profile.overflow_checks),
                        lto=profile_data.get('lto', base_profile.lto),
                        panic=profile_data.get('panic', base_profile.panic.value),
                        incremental=profile_data.get('incremental', base_profile.incremental),
                        codegen_units=profile_data.get('codegen-units', base_profile.codegen_units),
                        strip=profile_data.get('strip', base_profile.strip)
                    )
                else:
                    # Build from scratch or override defaults
                    default = profiles.get('dev')
                    profile = BuildProfile(
                        name=profile_name,
                        opt_level=profile_data.get('opt-level', default.opt_level if default else 0),
                        debug=profile_data.get('debug', default.debug if default else True),
                        debug_assertions=profile_data.get('debug-assertions', default.debug_assertions if default else True),
                        overflow_checks=profile_data.get('overflow-checks', default.overflow_checks if default else True),
                        lto=profile_data.get('lto', default.lto if default else False),
                        panic=profile_data.get('panic', default.panic.value if default else 'unwind'),
                        incremental=profile_data.get('incremental', default.incremental if default else True),
                        codegen_units=profile_data.get('codegen-units', default.codegen_units if default else 256),
                        strip=profile_data.get('strip', default.strip if default else False)
                    )
                
                profiles[profile_name] = profile
        
        return profiles
    
    def _parse_workspace(self) -> Optional[Workspace]:
        """Parse [workspace] section."""
        if 'workspace' not in self.data:
            return None
        
        ws = self.data['workspace']
        return Workspace(
            members=ws.get('members', []),
            exclude=ws.get('exclude', []),
            default_members=ws.get('default-members', [])
        )
    
    def _parse_target_specific_deps(self) -> Dict[str, Dict[str, Dependency]]:
        """Parse target-specific dependencies [target.'cfg(...)'.*]."""
        target_deps = {}
        
        # TOML parsers create nested structure: data['target']['cfg(unix)']['dependencies']
        if 'target' not in self.data:
            return target_deps
        
        for cfg, sections in self.data['target'].items():
            if not isinstance(sections, dict):
                continue
            
            for section, deps in sections.items():
                if section in ('dependencies', 'dev-dependencies', 'build-dependencies'):
                    if cfg not in target_deps:
                        target_deps[cfg] = {}
                    
                    # Parse dependencies for this target
                    for name, spec in deps.items():
                        if isinstance(spec, str):
                            target_deps[cfg][name] = Dependency(name=name, version_req=spec)
                        elif isinstance(spec, dict):
                            target_deps[cfg][name] = Dependency(
                                name=name,
                                version_req=spec.get('version'),
                                path=spec.get('path'),
                                features=spec.get('features', []),
                                optional=spec.get('optional', False)
                            )
        
        return target_deps
    
    def get_profile(self, name: str = 'dev') -> BuildProfile:
        """Get build profile by name."""
        if name not in self.profiles:
            raise ValueError(f"Unknown profile: {name}")
        return self.profiles[name]
    
    def has_feature(self, feature: str) -> bool:
        """Check if feature exists."""
        return feature in self.features
    
    def get_feature_dependencies(self, feature: str) -> List[str]:
        """Get dependencies enabled by a feature."""
        if feature not in self.features:
            return []
        return self.features[feature]
    
    def get_all_dependencies(self, include_dev: bool = False, include_build: bool = False) -> Dict[str, Dependency]:
        """Get all dependencies."""
        deps = dict(self.dependencies)
        if include_dev:
            deps.update(self.dev_dependencies)
        if include_build:
            deps.update(self.build_dependencies)
        return deps
    
    def resolve_path(self, relative_path: str) -> Path:
        """Resolve path relative to project root."""
        return self.project_root / relative_path
    
    def __repr__(self) -> str:
        if self.package:
            return f"Manifest({self.package.name} v{self.package.version})"
        return "Manifest(workspace)"


def load_manifest(path: Optional[Union[str, Path]] = None) -> Manifest:
    """
    Load and parse nlpl.toml manifest.
    
    Args:
        path: Path to nlpl.toml file. If None, searches current directory and parents.
    
    Returns:
        Parsed Manifest object
    
    Raises:
        FileNotFoundError: If nlpl.toml not found
        ValueError: If manifest is invalid
    """
    if path is None:
        # Search for nlpl.toml in current directory and parents
        current = Path.cwd()
        while current != current.parent:
            manifest_path = current / 'nlpl.toml'
            if manifest_path.exists():
                return Manifest(manifest_path)
            current = current.parent
        
        raise FileNotFoundError(
            "Could not find nlpl.toml in current directory or any parent directory"
        )
    
    return Manifest(path)


# Example usage
if __name__ == '__main__':
    import sys
    
    try:
        manifest = load_manifest(sys.argv[1] if len(sys.argv) > 1 else None)
        print(f"Loaded: {manifest}")
        if manifest.package:
            print(f"Package: {manifest.package.name} v{manifest.package.version}")
        print(f"Dependencies: {len(manifest.dependencies)}")
        print(f"Binary targets: {len(manifest.binary_targets)}")
        if manifest.library_target:
            print(f"Library: {manifest.library_target.name}")
        print(f"Features: {list(manifest.features.keys())}")
        print(f"Profiles: {list(manifest.profiles.keys())}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
