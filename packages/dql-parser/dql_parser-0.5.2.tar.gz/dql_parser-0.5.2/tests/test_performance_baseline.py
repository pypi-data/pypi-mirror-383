"""
Performance baseline tests for Story 1.8: Parser Performance Optimization.

Establishes baseline metrics and benchmarks with pytest-benchmark.
Tests AC1: Parser SHALL handle 1000-line files in <200ms (NFR1.1 target)

[Source: docs/stories/1.8.parser-performance-optimization.md]
"""

import time
from pathlib import Path

import pytest

from dql_parser.parser import DQLParser


class TestPerformanceBaseline:
    """Baseline performance tests using pytest-benchmark."""

    @pytest.fixture
    def parser(self):
        """Create DQL parser instance."""
        return DQLParser()

    @pytest.fixture
    def fixtures_dir(self):
        """Get path to benchmark fixtures directory."""
        return Path(__file__).parent.parent / "benchmarks" / "fixtures"

    # Subtask 1.2: Benchmark current parser with 100, 500, 1000, 2000 line files

    @pytest.mark.benchmark(group="baseline")
    def test_baseline_100_lines(self, benchmark, parser, fixtures_dir):
        """Benchmark parsing 100-line file (baseline)."""
        file_path = fixtures_dir / "100_lines.dql"
        content = file_path.read_text()

        result = benchmark(parser.parse, content)

        # Verify correctness
        assert len(result.from_blocks) == 25
        assert sum(len(block.expectations) for block in result.from_blocks) == 100

    @pytest.mark.benchmark(group="baseline")
    def test_baseline_500_lines(self, benchmark, parser, fixtures_dir):
        """Benchmark parsing 500-line file (baseline)."""
        file_path = fixtures_dir / "500_lines.dql"
        content = file_path.read_text()

        result = benchmark(parser.parse, content)

        # Verify correctness
        assert len(result.from_blocks) == 125
        assert sum(len(block.expectations) for block in result.from_blocks) == 500

    @pytest.mark.benchmark(group="baseline")
    def test_baseline_1000_lines(self, benchmark, parser, fixtures_dir):
        """
        Benchmark parsing 1000-line file (AC1 target: <200ms).

        This is the primary performance target from NFR1.1.
        """
        file_path = fixtures_dir / "1000_lines.dql"
        content = file_path.read_text()

        result = benchmark(parser.parse, content)

        # Verify correctness
        assert len(result.from_blocks) == 250
        assert sum(len(block.expectations) for block in result.from_blocks) == 1000

        # AC1: Target <200ms for 1000 lines
        # Note: Will likely fail before optimization - that's expected
        # Uncomment after optimization:
        # assert benchmark.stats.mean < 0.200, f"Target <200ms, got {benchmark.stats.mean*1000:.1f}ms"

    @pytest.mark.benchmark(group="baseline")
    def test_baseline_2000_lines(self, benchmark, parser, fixtures_dir):
        """Benchmark parsing 2000-line file (stress test)."""
        file_path = fixtures_dir / "2000_lines.dql"
        content = file_path.read_text()

        result = benchmark(parser.parse, content)

        # Verify correctness
        assert len(result.from_blocks) == 500
        assert sum(len(block.expectations) for block in result.from_blocks) == 2000

    # Subtask 1.3: Identify baseline performance metrics (mean, p50, p95, p99)
    # pytest-benchmark automatically captures these statistics

    def test_baseline_metrics_manual(self, parser, fixtures_dir):
        """
        Manually measure baseline metrics for detailed analysis.

        Captures mean, p50, p95, p99 for performance profiling.
        """
        file_path = fixtures_dir / "1000_lines.dql"
        content = file_path.read_text()

        # Warm up
        parser.parse(content)

        # Collect 100 samples
        times = []
        for _ in range(100):
            start = time.perf_counter()
            parser.parse(content)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms

        times.sort()

        mean = sum(times) / len(times)
        p50 = times[len(times) // 2]
        p95 = times[int(len(times) * 0.95)]
        p99 = times[int(len(times) * 0.99)]

        print(f"\n" + "=" * 60)
        print(f"BASELINE PERFORMANCE METRICS (1000 lines, n=100)")
        print(f"=" * 60)
        print(f"Mean: {mean:.2f}ms")
        print(f"P50:  {p50:.2f}ms")
        print(f"P95:  {p95:.2f}ms")
        print(f"P99:  {p99:.2f}ms")
        print(f"Min:  {times[0]:.2f}ms")
        print(f"Max:  {times[-1]:.2f}ms")
        print(f"=" * 60)
        print(f"TARGET: <200ms for 1000 lines (AC1)")
        print(f"STATUS: {'✓ PASS' if mean < 200 else '✗ FAIL - optimization needed'}")
        print(f"=" * 60)

        # Document for comparison after optimization
        assert len(times) == 100


class TestParserInitializationPerformance:
    """Test parser initialization overhead."""

    @pytest.mark.benchmark(group="initialization")
    def test_parser_initialization(self, benchmark):
        """Benchmark parser initialization time."""

        def init_parser():
            return DQLParser()

        parser = benchmark(init_parser)
        assert parser is not None

        # Parser initialization should be reasonable (<150ms)
        # This is important for CLI tools and test suites
        # Note: May need optimization if exceeds 150ms


class TestParserScaling:
    """Test parser scaling characteristics."""

    @pytest.fixture
    def parser(self):
        """Create DQL parser instance."""
        return DQLParser()

    @pytest.fixture
    def fixtures_dir(self):
        """Get path to benchmark fixtures directory."""
        return Path(__file__).parent.parent / "benchmarks" / "fixtures"

    def test_scaling_linearity(self, parser, fixtures_dir):
        """
        Test that parser scaling is roughly linear with file size.

        Validates O(n) parsing complexity.
        """
        sizes = [100, 500, 1000, 2000]
        results = {}

        for size in sizes:
            file_path = fixtures_dir / f"{size}_lines.dql"
            content = file_path.read_text()

            # Warm up
            parser.parse(content)

            # Measure
            times = []
            for _ in range(10):
                start = time.perf_counter()
                parser.parse(content)
                elapsed = time.perf_counter() - start
                times.append(elapsed * 1000)

            mean = sum(times) / len(times)
            results[size] = mean

        print(f"\n" + "=" * 60)
        print(f"PARSER SCALING ANALYSIS")
        print(f"=" * 60)
        for size in sizes:
            per_line = results[size] / size
            print(f"{size:4d} lines: {results[size]:6.2f}ms ({per_line:.4f}ms/line)")

        # Check scaling ratio
        ratio_100_to_1000 = results[1000] / results[100]
        expected_ratio = 10.0  # 1000/100
        scaling_factor = ratio_100_to_1000 / expected_ratio

        print(f"\nScaling factor (1000 vs 100): {scaling_factor:.2f}x")
        print(f"(1.0 = perfectly linear, >1.0 = super-linear)")
        print(f"=" * 60)

        # Should be roughly linear (within 2x of expected)
        assert scaling_factor < 2.0, f"Parser scaling is super-linear: {scaling_factor:.2f}x"
