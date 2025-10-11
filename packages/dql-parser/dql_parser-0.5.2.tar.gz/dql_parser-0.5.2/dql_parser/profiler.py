"""
Performance profiling utilities for DQL parser.

Provides tools for profiling parser performance and identifying bottlenecks.

[Source: docs/stories/1.8.parser-performance-optimization.md#task-2]
"""

import cProfile
import pstats
import time
from io import StringIO
from pathlib import Path
from typing import Callable, Optional


class ParserProfiler:
    """Profiler for analyzing DQL parser performance."""

    def __init__(self):
        """Initialize profiler."""
        self.profiler = cProfile.Profile()
        self.stats: Optional[pstats.Stats] = None

    def profile(self, func: Callable, *args, **kwargs):
        """
        Profile a function call.

        Args:
            func: Function to profile
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of function call
        """
        self.profiler.enable()
        try:
            result = func(*args, **kwargs)
        finally:
            self.profiler.disable()

        return result

    def get_stats(self, sort_by: str = "cumulative") -> pstats.Stats:
        """
        Get profiling statistics.

        Args:
            sort_by: Sort key ('cumulative', 'time', 'calls', etc.)

        Returns:
            Stats object
        """
        if self.stats is None:
            self.stats = pstats.Stats(self.profiler)

        self.stats.sort_stats(sort_by)
        return self.stats

    def print_stats(self, limit: int = 20, sort_by: str = "cumulative"):
        """
        Print top N hottest functions.

        Args:
            limit: Number of functions to display
            sort_by: Sort key
        """
        stats = self.get_stats(sort_by)
        print(f"\n{'=' * 80}")
        print(f"TOP {limit} FUNCTIONS BY {sort_by.upper()}")
        print(f"{'=' * 80}")
        stats.print_stats(limit)

    def save_stats(self, output_path: Path):
        """
        Save profiling stats to file.

        Args:
            output_path: Output file path (.prof extension)
        """
        self.profiler.dump_stats(str(output_path))
        print(f"Profile saved to: {output_path}")

    def analyze_bottlenecks(self) -> dict:
        """
        Analyze profiling results and identify bottlenecks.

        Returns:
            Dictionary with bottleneck analysis
        """
        stats = self.get_stats("cumulative")

        # Get top functions by cumulative time
        stream = StringIO()
        stats.stream = stream
        stats.print_stats(20)
        output = stream.getvalue()

        # Parse stats
        bottlenecks = {
            "total_calls": stats.total_calls,
            "total_time": stats.total_tt,
            "output": output,
        }

        return bottlenecks


def profile_parser_on_file(file_path: Path, parser_class, output_path: Optional[Path] = None):
    """
    Profile parser on a specific DQL file.

    Args:
        file_path: Path to DQL file to parse
        parser_class: DQLParser class
        output_path: Optional path to save profile stats

    Returns:
        Profiling results dictionary
    """
    content = file_path.read_text()

    # Create parser
    parser = parser_class()

    # Warm up
    parser.parse(content)

    # Profile
    profiler = ParserProfiler()
    start = time.perf_counter()
    profiler.profile(parser.parse, content)
    elapsed = time.perf_counter() - start

    print(f"\nProfiling Results for: {file_path.name}")
    print(f"{'=' * 80}")
    print(f"Parse time: {elapsed * 1000:.2f}ms")

    # Print top bottlenecks
    profiler.print_stats(limit=20, sort_by="cumulative")

    # Optionally save stats
    if output_path:
        profiler.save_stats(output_path)

    # Analyze
    bottlenecks = profiler.analyze_bottlenecks()
    bottlenecks["parse_time_ms"] = elapsed * 1000

    return bottlenecks


def compare_profiles(before_path: Path, after_path: Path):
    """
    Compare two profiling results.

    Args:
        before_path: Path to "before" profile
        after_path: Path to "after" profile
    """
    before_stats = pstats.Stats(str(before_path))
    after_stats = pstats.Stats(str(after_path))

    print(f"\n{'=' * 80}")
    print("BEFORE OPTIMIZATION")
    print(f"{'=' * 80}")
    before_stats.sort_stats("cumulative")
    before_stats.print_stats(10)

    print(f"\n{'=' * 80}")
    print("AFTER OPTIMIZATION")
    print(f"{'=' * 80}")
    after_stats.sort_stats("cumulative")
    after_stats.print_stats(10)

    print(f"\n{'=' * 80}")
    print("COMPARISON SUMMARY")
    print(f"{'=' * 80}")
    print("Review the cumulative times above to see improvements")
