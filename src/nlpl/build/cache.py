"""
Build Cache

Handles incremental compilation with file change detection and caching.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Set, Optional
from dataclasses import dataclass, field


@dataclass
class FileMetadata:
    """Metadata for a source file."""
    path: str
    hash: str
    mtime: float
    dependencies: Set[str] = field(default_factory=set)


class BuildCache:
    """
    Build cache for incremental compilation.
    
    Tracks file hashes and modification times to determine what needs recompilation.
    """
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = cache_dir / "build_cache.json"
        self.metadata: Dict[str, FileMetadata] = {}
        self.load()
    
    def load(self) -> None:
        """Load cache from disk."""
        if not self.cache_file.exists():
            return
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            
            for path, meta in data.items():
                self.metadata[path] = FileMetadata(
                    path=meta['path'],
                    hash=meta['hash'],
                    mtime=meta['mtime'],
                    dependencies=set(meta.get('dependencies', []))
                )
        except (json.JSONDecodeError, KeyError):
            self.metadata = {}
    
    def save(self) -> None:
        """Save cache to disk."""
        data = {}
        for path, meta in self.metadata.items():
            data[path] = {
                'path': meta.path,
                'hash': meta.hash,
                'mtime': meta.mtime,
                'dependencies': list(meta.dependencies)
            }
        
        with open(self.cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_file_hash(self, path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def needs_rebuild(self, path: Path) -> bool:
        """Check if a file needs to be rebuilt."""
        path_str = str(path)
        
        # File doesn't exist in cache - needs rebuild
        if path_str not in self.metadata:
            return True
        
        # File doesn't exist on disk - needs rebuild
        if not path.exists():
            return True
        
        meta = self.metadata[path_str]
        
        # Check modification time first (fast check)
        current_mtime = path.stat().st_mtime
        if current_mtime != meta.mtime:
            # Modification time changed - verify with hash
            current_hash = self.get_file_hash(path)
            if current_hash != meta.hash:
                return True
        
        # Check if any dependencies changed
        for dep_path in meta.dependencies:
            dep = Path(dep_path)
            if self.needs_rebuild(dep):
                return True
        
        return False
    
    def update(self, path: Path, dependencies: Optional[Set[Path]] = None) -> None:
        """Update cache entry for a file."""
        if not path.exists():
            return
        
        path_str = str(path)
        deps = set(str(d) for d in (dependencies or set()))
        
        self.metadata[path_str] = FileMetadata(
            path=path_str,
            hash=self.get_file_hash(path),
            mtime=path.stat().st_mtime,
            dependencies=deps
        )
    
    def get_files_to_rebuild(self, files: list[Path]) -> list[Path]:
        """Get list of files that need to be rebuilt."""
        to_rebuild = []
        for file in files:
            if self.needs_rebuild(file):
                to_rebuild.append(file)
        return to_rebuild
    
    def clear(self) -> None:
        """Clear the entire cache."""
        self.metadata = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
    
    def remove(self, path: Path) -> None:
        """Remove a file from the cache."""
        path_str = str(path)
        if path_str in self.metadata:
            del self.metadata[path_str]
