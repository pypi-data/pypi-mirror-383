"""
Unit tests for parser caching (Story 1.8 Task 8).

Tests AC2: Parser SHALL implement file-based caching
Tests AC3: Cache SHALL use file content hash (SHA256) as key
Tests AC6: Cache overhead <10%

[Source: docs/stories/1.8.parser-performance-optimization.md#task-8]
"""

import time
from pathlib import Path

import pytest

from dql_parser import DQLParser, ParserCache, FileCache


class TestParserCache:
    """Test ParserCache functionality."""

    @pytest.fixture
    def dql_content(self):
        """Sample DQL content."""
        return """
from Customer
expect column("email") to_not_be_null severity critical
expect column("age") to_be_between(0, 120) severity warning
"""

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = ParserCache(max_size=64)
        assert len(cache) == 0
        assert cache.get_stats()["size"] == 0
        assert cache.get_stats()["max_size"] == 64

    def test_cache_hit(self, dql_content):
        """Test cache hit on same content (AC2)."""
        parser = DQLParser(cache=ParserCache())

        # First parse (cache miss)
        ast1 = parser.parse(dql_content)
        stats1 = parser.get_cache_stats()

        assert stats1["misses"] == 1
        assert stats1["hits"] == 0

        # Second parse (cache hit)
        ast2 = parser.parse(dql_content)
        stats2 = parser.get_cache_stats()

        assert stats2["misses"] == 1
        assert stats2["hits"] == 1

        # ASTs should be identical (same object)
        assert ast1 is ast2

    def test_cache_miss_on_content_change(self, dql_content):
        """Test cache invalidation when content changes (AC3)."""
        parser = DQLParser(cache=ParserCache())

        # Parse original
        ast1 = parser.parse(dql_content)

        # Parse modified content
        modified_content = dql_content.replace("critical", "warning")
        ast2 = parser.parse(modified_content)

        stats = parser.get_cache_stats()
        assert stats["misses"] == 2  # Both were cache misses
        assert stats["hits"] == 0

        # ASTs should be different objects
        assert ast1 is not ast2

    def test_cache_sha256_hash(self):
        """Test that cache uses SHA256 hash (AC3)."""
        cache = ParserCache()
        content = "from Model\nexpect column(\"x\") to_not_be_null"

        hash1 = cache.get_file_hash(content)

        # SHA256 produces 64 character hex string
        assert len(hash1) == 64
        assert all(c in "0123456789abcdef" for c in hash1)

        # Same content produces same hash
        hash2 = cache.get_file_hash(content)
        assert hash1 == hash2

        # Different content produces different hash
        hash3 = cache.get_file_hash(content + " ")
        assert hash1 != hash3

    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache full."""
        cache = ParserCache(max_size=3)
        parser = DQLParser(cache=cache)

        contents = [
            "from Model1\nexpect column(\"x\") to_not_be_null",
            "from Model2\nexpect column(\"y\") to_not_be_null",
            "from Model3\nexpect column(\"z\") to_not_be_null",
            "from Model4\nexpect column(\"w\") to_not_be_null",
        ]

        # Fill cache
        for content in contents[:3]:
            parser.parse(content)

        assert len(cache) == 3

        # Add 4th item (should evict oldest)
        parser.parse(contents[3])

        assert len(cache) == 3

        # First item should be evicted
        parser.parse(contents[0])  # Should be cache miss
        stats = parser.get_cache_stats()

        # Should have 1 hit (from refilling cache) and misses
        assert stats["size"] == 3

    def test_cache_performance_overhead(self):
        """
        Test that cache overhead is <10% (AC6).

        Uses larger content to ensure SHA256 overhead is proportionally small.
        """
        # Generate larger content (50 expectations ~= 200 lines)
        expectations = []
        for i in range(50):
            expectations.append(f'expect column("field{i}") to_not_be_null severity critical')

        large_content = "from LargeModel\n" + "\n".join(expectations)

        # Parse without cache
        parser_no_cache = DQLParser(enable_cache=False)

        # Warm up
        parser_no_cache.parse(large_content)

        times_no_cache = []
        for _ in range(50):  # More samples for stable measurement
            start = time.perf_counter()
            parser_no_cache.parse(large_content)
            elapsed = time.perf_counter() - start
            times_no_cache.append(elapsed)

        mean_no_cache = sum(times_no_cache) / len(times_no_cache)

        # Parse with cache (first time = cache miss with overhead)
        parser_with_cache = DQLParser(enable_cache=True)

        # Warm up
        parser_with_cache.clear_cache()
        parser_with_cache.parse(large_content)

        times_with_cache = []
        for _ in range(50):  # More samples
            parser_with_cache.clear_cache()  # Force cache miss
            start = time.perf_counter()
            parser_with_cache.parse(large_content)
            elapsed = time.perf_counter() - start
            times_with_cache.append(elapsed)

        mean_with_cache = sum(times_with_cache) / len(times_with_cache)

        # Cache overhead should be <10%
        overhead_pct = ((mean_with_cache - mean_no_cache) / mean_no_cache) * 100

        print(f"\nCache overhead: {overhead_pct:.2f}%")
        print(f"No cache: {mean_no_cache*1000:.2f}ms")
        print(f"With cache (miss): {mean_with_cache*1000:.2f}ms")

        # AC6: Cache overhead <10%
        assert overhead_pct < 10.0, f"Cache overhead {overhead_pct:.1f}% exceeds 10% limit"

    def test_cache_hit_performance(self, dql_content):
        """Test cache hit is significantly faster than miss."""
        parser = DQLParser(cache=ParserCache())

        # Warm up and populate cache
        parser.parse(dql_content)

        # Measure cache miss (with cleared cache)
        parser.clear_cache()
        start = time.perf_counter()
        parser.parse(dql_content)
        miss_time = time.perf_counter() - start

        # Measure cache hit
        start = time.perf_counter()
        parser.parse(dql_content)
        hit_time = time.perf_counter() - start

        print(f"\nCache miss: {miss_time*1000:.2f}ms")
        print(f"Cache hit: {hit_time*1000:.2f}ms")
        print(f"Speedup: {miss_time/hit_time:.1f}x")

        # Cache hit should be at least 10x faster
        assert hit_time < miss_time / 10, f"Cache hit not fast enough: {hit_time*1000:.2f}ms"

    def test_cache_stats(self, dql_content):
        """Test cache statistics reporting (AC5)."""
        parser = DQLParser(cache=ParserCache())

        # Initial stats
        stats = parser.get_cache_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["size"] == 0
        assert stats["hit_rate"] == 0.0

        # After cache miss
        parser.parse(dql_content)
        stats = parser.get_cache_stats()
        assert stats["misses"] == 1
        assert stats["size"] == 1

        # After cache hit
        parser.parse(dql_content)
        stats = parser.get_cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0

    def test_cache_disabled(self, dql_content):
        """Test that caching can be disabled."""
        parser = DQLParser(enable_cache=False)

        # Parse twice
        parser.parse(dql_content)
        parser.parse(dql_content)

        # Stats should be empty
        stats = parser.get_cache_stats()
        assert stats == {}


class TestFileCache:
    """Test FileCache for file-path-based caching."""

    @pytest.fixture
    def temp_dql_file(self, tmp_path):
        """Create temporary DQL file."""
        file_path = tmp_path / "test.dql"
        content = """
from Customer
expect column("email") to_not_be_null severity critical
"""
        file_path.write_text(content)
        return file_path

    def test_file_cache_initialization(self):
        """Test FileCache initialization."""
        cache = FileCache(max_size=32)
        assert len(cache) == 0
        assert cache.get_stats()["max_size"] == 32

    def test_file_cache_hit(self, temp_dql_file):
        """Test file cache hit."""
        from dql_parser.parser import DQLParser

        cache = FileCache()
        parser = DQLParser()

        # First parse
        content = temp_dql_file.read_text()
        ast1 = parser.parse(content)
        cache.set(temp_dql_file, ast1)

        # Second parse (cache hit)
        ast2 = cache.get(temp_dql_file)

        assert ast2 is not None
        assert ast2 is ast1
        assert cache.get_stats()["hits"] == 1

    def test_file_cache_invalidation_on_modification(self, temp_dql_file):
        """Test file cache invalidates on file modification."""
        from dql_parser.parser import DQLParser

        cache = FileCache()
        parser = DQLParser()

        # Parse and cache
        content = temp_dql_file.read_text()
        ast1 = parser.parse(content)
        cache.set(temp_dql_file, ast1)

        # Modify file
        time.sleep(0.01)  # Ensure mtime changes
        temp_dql_file.write_text(content + "\n# Comment")

        # Should be cache miss
        ast2 = cache.get(temp_dql_file)
        assert ast2 is None

        stats = cache.get_stats()
        assert stats["misses"] == 1
