"""
NLPL Build System - Incremental Compilation

Tracks file dependencies and modification times to enable smart rebuilds.
Only recompiles files that have changed or whose dependencies have changed.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Set, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class FileMetadata:
    """Metadata for a source file."""
    path: str
    mtime: float  # Modification time (timestamp)
    size: int  # File size in bytes
    hash: str  # Content hash (SHA-256)
    imports: List[str] = field(default_factory=list)  # Imported modules
    
    def has_changed(self, current_mtime: float, current_size: int) -> bool:
        """Check if file has changed based on mtime and size."""
        return self.mtime != current_mtime or self.size != current_size
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FileMetadata':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class BuildArtifact:
    """Metadata for a build artifact."""
    source_file: str
    output_file: str
    build_time: float
    profile: str
    features: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BuildArtifact':
        """Create from dictionary."""
        return cls(**data)


class DependencyGraph:
    """Dependency graph for tracking file dependencies."""
    
    def __init__(self):
        """Initialize empty dependency graph."""
        self.dependencies: Dict[str, Set[str]] = {}  # file -> set of dependencies
        self.reverse_deps: Dict[str, Set[str]] = {}  # file -> set of dependents
    
    def add_dependency(self, source: str, dependency: str) -> None:
        """
        Add a dependency relationship.
        
        Args:
            source: The file that imports/depends on another
            dependency: The file being imported/depended on
        """
        if source not in self.dependencies:
            self.dependencies[source] = set()
        self.dependencies[source].add(dependency)
        
        if dependency not in self.reverse_deps:
            self.reverse_deps[dependency] = set()
        self.reverse_deps[dependency].add(source)
    
    def get_dependencies(self, file: str) -> Set[str]:
        """Get all direct dependencies of a file."""
        return self.dependencies.get(file, set()).copy()
    
    def get_dependents(self, file: str) -> Set[str]:
        """Get all files that depend on this file."""
        return self.reverse_deps.get(file, set()).copy()
    
    def get_transitive_dependencies(self, file: str) -> Set[str]:
        """
        Get all transitive dependencies of a file.
        
        Returns all files that this file depends on, directly or indirectly.
        """
        visited = set()
        to_visit = [file]
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            
            visited.add(current)
            deps = self.get_dependencies(current)
            to_visit.extend(deps - visited)
        
        visited.discard(file)  # Remove the file itself
        return visited
    
    def get_transitive_dependents(self, file: str) -> Set[str]:
        """
        Get all transitive dependents of a file.
        
        Returns all files that depend on this file, directly or indirectly.
        """
        visited = set()
        to_visit = [file]
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            
            visited.add(current)
            dependents = self.get_dependents(current)
            to_visit.extend(dependents - visited)
        
        visited.discard(file)  # Remove the file itself
        return visited
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'dependencies': {k: list(v) for k, v in self.dependencies.items()},
            'reverse_deps': {k: list(v) for k, v in self.reverse_deps.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DependencyGraph':
        """Create from dictionary."""
        graph = cls()
        graph.dependencies = {k: set(v) for k, v in data.get('dependencies', {}).items()}
        graph.reverse_deps = {k: set(v) for k, v in data.get('reverse_deps', {}).items()}
        return graph


class BuildCache:
    """
    Build cache for incremental compilation.
    
    Tracks file metadata, dependencies, and build artifacts to determine
    what needs to be rebuilt.
    """
    
    def __init__(self, cache_dir: Path):
        """
        Initialize build cache.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self.cache_file = cache_dir / 'build_cache.json'
        
        self.file_metadata: Dict[str, FileMetadata] = {}
        self.dependency_graph = DependencyGraph()
        self.build_artifacts: Dict[str, BuildArtifact] = {}
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing cache
        self._load_cache()
    
    def update_file_metadata(self, file_path: Path, imports: List[str] = None) -> FileMetadata:
        """
        Update metadata for a file.
        
        Args:
            file_path: Path to the file
            imports: List of imported module paths (optional)
        
        Returns:
            Updated FileMetadata
        """
        # Get file stats
        stat = file_path.stat()
        mtime = stat.st_mtime
        size = stat.st_size
        
        # Calculate content hash
        with open(file_path, 'rb') as f:
            content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()
        
        # Create or update metadata
        path_str = str(file_path)
        metadata = FileMetadata(
            path=path_str,
            mtime=mtime,
            size=size,
            hash=file_hash,
            imports=imports or []
        )
        
        self.file_metadata[path_str] = metadata
        
        # Update dependency graph
        if imports:
            for import_path in imports:
                self.dependency_graph.add_dependency(path_str, import_path)
        
        return metadata
    
    def is_file_changed(self, file_path: Path) -> bool:
        """
        Check if a file has changed since last build.
        
        Args:
            file_path: Path to check
        
        Returns:
            True if file has changed or is new
        """
        path_str = str(file_path)
        
        # New file
        if path_str not in self.file_metadata:
            return True
        
        # Check if file still exists
        if not file_path.exists():
            return True
        
        # Compare modification time and size (fast check)
        stat = file_path.stat()
        metadata = self.file_metadata[path_str]
        
        if metadata.has_changed(stat.st_mtime, stat.st_size):
            return True
        
        return False
    
    def is_file_hash_changed(self, file_path: Path) -> bool:
        """
        Check if file content has changed using hash (slower but more accurate).
        
        Args:
            file_path: Path to check
        
        Returns:
            True if content hash has changed
        """
        path_str = str(file_path)
        
        if path_str not in self.file_metadata:
            return True
        
        if not file_path.exists():
            return True
        
        # Calculate current hash
        with open(file_path, 'rb') as f:
            content = f.read()
            current_hash = hashlib.sha256(content).hexdigest()
        
        return self.file_metadata[path_str].hash != current_hash
    
    def needs_rebuild(self, source_path: Path, profile: str = 'dev', 
                     features: List[str] = None) -> Tuple[bool, str]:
        """
        Determine if a source file needs to be rebuilt.
        
        Args:
            source_path: Source file path
            profile: Build profile
            features: Enabled features
        
        Returns:
            Tuple of (needs_rebuild, reason)
        """
        path_str = str(source_path)
        features = features or []
        
        # Check if source file has changed
        if self.is_file_changed(source_path):
            return (True, f"Source file {source_path.name} changed")
        
        # Check if any dependencies have changed
        deps = self.dependency_graph.get_transitive_dependencies(path_str)
        for dep_path_str in deps:
            dep_path = Path(dep_path_str)
            if self.is_file_changed(dep_path):
                return (True, f"Dependency {dep_path.name} changed")
        
        # Check if build artifact exists
        artifact_key = self._artifact_key(source_path, profile, features)
        if artifact_key not in self.build_artifacts:
            return (True, "No previous build artifact")
        
        artifact = self.build_artifacts[artifact_key]
        output_path = Path(artifact.output_file)
        
        if not output_path.exists():
            return (True, "Output artifact missing")
        
        # Check if profile or features changed
        if artifact.profile != profile:
            return (True, f"Profile changed: {artifact.profile} → {profile}")
        
        if set(artifact.features) != set(features):
            return (True, "Feature flags changed")
        
        return (False, "Up to date")
    
    def record_build(self, source_path: Path, output_path: Path, 
                    profile: str, features: List[str] = None) -> None:
        """
        Record a successful build.
        
        Args:
            source_path: Source file that was compiled
            output_path: Output artifact path
            profile: Build profile used
            features: Features enabled
        """
        features = features or []
        
        artifact = BuildArtifact(
            source_file=str(source_path),
            output_file=str(output_path),
            build_time=datetime.now().timestamp(),
            profile=profile,
            features=features
        )
        
        artifact_key = self._artifact_key(source_path, profile, features)
        self.build_artifacts[artifact_key] = artifact
    
    def get_files_to_rebuild(self, files: List[Path], profile: str = 'dev',
                            features: List[str] = None) -> List[Tuple[Path, str]]:
        """
        Get list of files that need to be rebuilt.
        
        Args:
            files: List of source files
            profile: Build profile
            features: Enabled features
        
        Returns:
            List of (file_path, reason) tuples for files that need rebuilding
        """
        to_rebuild = []
        
        for file_path in files:
            needs_rebuild, reason = self.needs_rebuild(file_path, profile, features)
            if needs_rebuild:
                to_rebuild.append((file_path, reason))
        
        return to_rebuild
    
    def invalidate_file(self, file_path: Path) -> Set[Path]:
        """
        Invalidate a file and all its dependents.
        
        Args:
            file_path: File to invalidate
        
        Returns:
            Set of all files that need to be rebuilt
        """
        path_str = str(file_path)
        invalidated = {file_path}
        
        # Get all transitive dependents
        dependents = self.dependency_graph.get_transitive_dependents(path_str)
        invalidated.update(Path(d) for d in dependents)
        
        return invalidated
    
    def save(self) -> None:
        """Save cache to disk."""
        cache_data = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'file_metadata': {k: v.to_dict() for k, v in self.file_metadata.items()},
            'dependency_graph': self.dependency_graph.to_dict(),
            'build_artifacts': {k: v.to_dict() for k, v in self.build_artifacts.items()}
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def clear(self) -> None:
        """Clear the cache."""
        self.file_metadata.clear()
        self.dependency_graph = DependencyGraph()
        self.build_artifacts.clear()
        
        if self.cache_file.exists():
            self.cache_file.unlink()
    
    def _load_cache(self) -> None:
        """Load cache from disk."""
        if not self.cache_file.exists():
            return
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Load file metadata
            for path, data in cache_data.get('file_metadata', {}).items():
                self.file_metadata[path] = FileMetadata.from_dict(data)
            
            # Load dependency graph
            graph_data = cache_data.get('dependency_graph', {})
            self.dependency_graph = DependencyGraph.from_dict(graph_data)
            
            # Load build artifacts
            for key, data in cache_data.get('build_artifacts', {}).items():
                self.build_artifacts[key] = BuildArtifact.from_dict(data)
        
        except Exception as e:
            # If cache is corrupted, start fresh
            print(f"Warning: Failed to load build cache: {e}")
            self.clear()
    
    def _artifact_key(self, source_path: Path, profile: str, features: List[str]) -> str:
        """Generate unique key for build artifact."""
        features_str = ','.join(sorted(features))
        return f"{source_path}:{profile}:{features_str}"


def extract_imports_from_source(source_code: str) -> List[str]:
    """
    Extract import statements from NLPL source code.
    
    Args:
        source_code: NLPL source code
    
    Returns:
        List of imported module names
    """
    imports = []
    
    # Match import statements
    # Pattern: import module_name
    import_pattern = r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
    
    for line in source_code.split('\n'):
        match = re.match(import_pattern, line)
        if match:
            imports.append(match.group(1))
    
    return imports


# Re-export for convenience
import re
