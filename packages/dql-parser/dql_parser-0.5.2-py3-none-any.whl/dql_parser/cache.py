"""
File-based caching for DQL parser to avoid re-parsing unchanged files.

Implements caching with SHA256 hash-based invalidation (AC2, AC3).

[Source: docs/stories/1.8.parser-performance-optimization.md#task-5]
"""

import hashlib
from collections import OrderedDict
from pathlib import Path
from typing import Optional

from dql_parser.ast_nodes import DQLFile


class ParserCache:
    """
    LRU cache for parsed DQL files with content-hash-based invalidation.

    Uses SHA256 hash of file content as cache key to detect changes.
    Implements LRU eviction when cache is full.

    AC3: Cache uses file content hash (SHA256) as key for invalidation
    AC6: Cache overhead <10% (fast hash computation, minimal bookkeeping)
    """

    def __init__(self, max_size: int = 128):
        """
        Initialize parser cache.

        Args:
            max_size: Maximum number of cached files (default: 128)
        """
        self._cache: OrderedDict[str, DQLFile] = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get_file_hash(self, content: str) -> str:
        """
        Compute SHA256 hash of file content.

        Args:
            content: File content string

        Returns:
            Hexadecimal SHA256 hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get(self, content: str) -> Optional[DQLFile]:
        """
        Get cached AST if file content unchanged.

        Args:
            content: Current file content

        Returns:
            Cached DQLFile or None if not in cache
        """
        content_hash = self.get_file_hash(content)

        if content_hash in self._cache:
            # Move to end (mark as recently used)
            self._cache.move_to_end(content_hash)
            self._hits += 1
            return self._cache[content_hash]

        self._misses += 1
        return None

    def set(self, content: str, ast: DQLFile):
        """
        Cache parsed AST with content hash as key.

        Implements LRU eviction if cache is full.

        Args:
            content: File content that was parsed
            ast: Parsed AST
        """
        content_hash = self.get_file_hash(content)

        # If already in cache, update and move to end
        if content_hash in self._cache:
            self._cache.move_to_end(content_hash)
            self._cache[content_hash] = ast
            return

        # Evict oldest entry if cache full (OrderedDict preserves insertion order)
        if len(self._cache) >= self._max_size:
            # Remove first (oldest) entry
            self._cache.popitem(last=False)

        # Add to cache (at end = most recent)
        self._cache[content_hash] = ast

    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (hits, misses, size, hit_rate)
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": len(self._cache),
            "max_size": self._max_size,
            "hit_rate": hit_rate,
        }

    def __len__(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)


class FileCache:
    """
    File-path-based cache that tracks file modification times.

    Alternative to ParserCache for file-based workflows.
    Uses file mtime and size for quick invalidation checks.
    """

    def __init__(self, max_size: int = 128):
        """
        Initialize file cache.

        Args:
            max_size: Maximum number of cached files
        """
        self._cache: OrderedDict[str, tuple[DQLFile, float, int]] = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, file_path: Path) -> Optional[DQLFile]:
        """
        Get cached AST if file unchanged.

        Checks file mtime and size for quick invalidation.

        Args:
            file_path: Path to DQL file

        Returns:
            Cached DQLFile or None if invalid/missing
        """
        if not file_path.exists():
            return None

        key = str(file_path)
        stat = file_path.stat()
        current_mtime = stat.st_mtime
        current_size = stat.st_size

        if key in self._cache:
            ast, cached_mtime, cached_size = self._cache[key]

            # Check if file changed
            if current_mtime == cached_mtime and current_size == cached_size:
                # Move to end (mark as recently used)
                self._cache.move_to_end(key)
                self._hits += 1
                return ast

            # File changed, invalidate entry
            del self._cache[key]

        self._misses += 1
        return None

    def set(self, file_path: Path, ast: DQLFile):
        """
        Cache parsed AST for file.

        Args:
            file_path: Path to DQL file
            ast: Parsed AST
        """
        key = str(file_path)
        stat = file_path.stat()
        mtime = stat.st_mtime
        size = stat.st_size

        # If already in cache, update and move to end
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = (ast, mtime, size)
            return

        # Evict oldest if full
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)

        # Add to cache
        self._cache[key] = (ast, mtime, size)

    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": len(self._cache),
            "max_size": self._max_size,
            "hit_rate": hit_rate,
        }

    def __len__(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)
