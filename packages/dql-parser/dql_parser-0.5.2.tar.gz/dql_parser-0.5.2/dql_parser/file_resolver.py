"""
File resolution and include management for DQL parser.

Handles resolution of INCLUDE directives, circular dependency detection,
and include stack management.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .exceptions import DQLSyntaxError


class CircularIncludeError(DQLSyntaxError):
    """Raised when circular include dependency is detected."""

    def __init__(self, chain: List[Path]):
        self.chain = chain
        chain_str = " → ".join(str(p.name) for p in chain)
        message = f"Circular include detected: {chain_str}"
        super().__init__(message=message, line=0, column=0, context="")


class IncludeDepthError(DQLSyntaxError):
    """Raised when include depth exceeds maximum limit."""

    def __init__(self, depth: int, max_depth: int):
        message = f"Include depth {depth} exceeds maximum of {max_depth}"
        super().__init__(message=message, line=0, column=0, context="")


class FileResolver:
    """
    Resolves file paths for INCLUDE directives and manages include stack.

    Handles relative path resolution, circular dependency detection,
    and depth limiting to prevent infinite loops.

    Example:
        >>> resolver = FileResolver(base_path=Path("/project/dql"))
        >>> resolved = resolver.resolve("shared/common.dql", current_file=Path("/project/dql/models/customer.dql"))
        >>> print(resolved)
        /project/dql/models/shared/common.dql
    """

    MAX_INCLUDE_DEPTH = 10

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize file resolver.

        Args:
            base_path: Base directory for resolving relative paths.
                      Defaults to current working directory.
        """
        self.base_path = base_path or Path.cwd()
        self.include_stack: List[Path] = []

    def resolve(
        self, include_path: str, current_file: Optional[Path] = None
    ) -> Path:
        """
        Resolve include path to absolute path.

        Resolution priority:
        1. Relative to current file's directory (if current_file provided)
        2. Relative to base_path

        Args:
            include_path: Path from INCLUDE directive (relative)
            current_file: Path to file containing INCLUDE directive

        Returns:
            Absolute resolved path

        Raises:
            CircularIncludeError: If resolved path is already in include stack
            IncludeDepthError: If include depth exceeds maximum
            FileNotFoundError: If resolved file doesn't exist
        """
        # Check include depth
        if len(self.include_stack) >= self.MAX_INCLUDE_DEPTH:
            raise IncludeDepthError(
                len(self.include_stack), self.MAX_INCLUDE_DEPTH
            )

        # Resolve path relative to current file or base path
        if current_file:
            resolved = (current_file.parent / include_path).resolve()
        else:
            resolved = (self.base_path / include_path).resolve()

        # SECURITY: Prevent path traversal outside base_path (SEC-001 fix)
        # Use try/except for Python 3.8 compatibility (is_relative_to() requires 3.9+)
        try:
            resolved.relative_to(self.base_path)
        except ValueError:
            raise DQLSyntaxError(
                message=f"INCLUDE path '{include_path}' resolves outside project boundary: {resolved}",
                line=0,
                column=0,
                context="",
                suggested_fix="Use relative paths within project directory only. "
                              "Path traversal (../) outside base_path is not allowed for security reasons."
            )

        # Check for circular includes
        if resolved in self.include_stack:
            chain = self.include_stack + [resolved]
            raise CircularIncludeError(chain)

        # Verify file exists
        if not resolved.exists():
            raise FileNotFoundError(
                f"INCLUDE file not found: {include_path} "
                f"(resolved to {resolved})"
            )

        if not resolved.is_file():
            raise FileNotFoundError(
                f"INCLUDE path is not a file: {include_path} "
                f"(resolved to {resolved})"
            )

        return resolved

    def push_file(self, file_path: Path) -> None:
        """
        Add file to include stack.

        Args:
            file_path: Absolute path to file being included
        """
        self.include_stack.append(file_path)

    def pop_file(self) -> Path:
        """
        Remove file from include stack.

        Returns:
            The path that was removed

        Raises:
            IndexError: If include stack is empty
        """
        return self.include_stack.pop()

    def get_current_file(self) -> Optional[Path]:
        """
        Get the current file being parsed.

        Returns:
            Path to current file, or None if stack is empty
        """
        return self.include_stack[-1] if self.include_stack else None

    def get_include_depth(self) -> int:
        """
        Get current include depth.

        Returns:
            Number of files in include stack
        """
        return len(self.include_stack)

    def clear(self) -> None:
        """Clear the include stack."""
        self.include_stack.clear()
