
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# Try to import tomllib (Python 3.11+) or tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        # Fallback for older python without tomli installed
        # This is a very basic parser for bootstrapping
        class SimpleToml:
            def load(self, f):
                data = {}
                current_section = data
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    if line.startswith('[') and line.endswith(']'):
                        section = line[1:-1]
                        current_section = {}
                        data[section] = current_section
                    elif '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        current_section[key] = value
                return data
        tomllib = SimpleToml()

@dataclass
class PackageConfig:
    name: str
    version: str
    authors: List[str] = field(default_factory=list)
    description: str = ""

@dataclass
class BuildConfig:
    source_dir: str = "src"
    output_dir: str = "build"
    target: str = "c"  # c, cpp, llvm_ir, etc.
    optimization: int = 0
    headers: bool = False

@dataclass
class ProjectConfig:
    package: PackageConfig
    build: BuildConfig
    dependencies: Dict[str, str] = field(default_factory=dict)

class ConfigLoader:
    """Loads and validates nlpl.toml configuration."""
    
    @staticmethod
    def load(path: str = "nlpl.toml") -> ProjectConfig:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")
            
        with open(path, "rb") as f:
            data = tomllib.load(f)
            
        # Parse [package]
        pkg_data = data.get("package", {})
        package = PackageConfig(
            name=pkg_data.get("name", "untitled"),
            version=pkg_data.get("version", "0.1.0"),
            authors=pkg_data.get("authors", []),
            description=pkg_data.get("description", "")
        )
        
        # Parse [build]
        build_data = data.get("build", {})
        build = BuildConfig(
            source_dir=build_data.get("source_dir", "src"),
            output_dir=build_data.get("output_dir", "build"),
            target=build_data.get("target", "c"),
            optimization=int(build_data.get("optimization", 0)),
            headers=bool(build_data.get("headers", False))
        )
        
        # Parse [dependencies]
        dependencies = data.get("dependencies", {})
        
        return ProjectConfig(package, build, dependencies)
