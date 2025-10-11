"""
Security tests for DQL parser.

Tests security-critical functionality including path traversal prevention.

[Source: Story 1.7 - QA SEC-001 fix validation]
"""

import pytest
from pathlib import Path

from dql_parser.file_resolver import FileResolver
from dql_parser.exceptions import DQLSyntaxError


class TestPathTraversalPrevention:
    """
    Test path traversal vulnerability prevention (SEC-001).

    These tests verify that the FileResolver properly rejects attempts
    to access files outside the project boundary using path traversal.
    """

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure for testing."""
        # Create project structure
        project = tmp_path / "project"
        project.mkdir()

        # Create models directory
        models_dir = project / "models"
        models_dir.mkdir()

        # Create a legitimate file
        customer_file = models_dir / "customer.dql"
        customer_file.write_text("from Customer\nexpect column(\"email\") to_not_be_null")

        # Create a shared file
        shared_file = models_dir / "shared.dql"
        shared_file.write_text("expect column(\"id\") to_not_be_null")

        # Create sensitive file OUTSIDE project (simulating /etc/passwd)
        sensitive_dir = tmp_path / "sensitive"
        sensitive_dir.mkdir()
        sensitive_file = sensitive_dir / "secrets.txt"
        sensitive_file.write_text("DATABASE_PASSWORD=super_secret")

        return {
            "project": project,
            "models_dir": models_dir,
            "customer_file": customer_file,
            "shared_file": shared_file,
            "sensitive_file": sensitive_file,
        }

    def test_reject_path_traversal_to_parent(self, temp_project):
        """
        Test that path traversal to parent directory is rejected.

        Simulates: INCLUDE "../../sensitive/secrets.txt"
        """
        resolver = FileResolver(base_path=temp_project["project"])

        with pytest.raises(DQLSyntaxError) as exc_info:
            resolver.resolve(
                "../../sensitive/secrets.txt",
                current_file=temp_project["customer_file"]
            )

        assert "resolves outside project boundary" in str(exc_info.value)
        assert "Path traversal" in str(exc_info.value)

    def test_reject_path_traversal_to_root(self, temp_project):
        """
        Test that path traversal to root directory is rejected.

        Simulates: INCLUDE "../../../../../etc/passwd"
        """
        resolver = FileResolver(base_path=temp_project["project"])

        with pytest.raises(DQLSyntaxError) as exc_info:
            resolver.resolve(
                "../../../../../etc/passwd",
                current_file=temp_project["customer_file"]
            )

        assert "resolves outside project boundary" in str(exc_info.value)

    def test_reject_absolute_path_outside_project(self, temp_project):
        """
        Test that absolute paths outside project are rejected.

        Simulates: INCLUDE "/etc/passwd"
        """
        resolver = FileResolver(base_path=temp_project["project"])

        with pytest.raises(DQLSyntaxError) as exc_info:
            resolver.resolve(
                "/etc/passwd",
                current_file=temp_project["customer_file"]
            )

        assert "resolves outside project boundary" in str(exc_info.value)

    def test_allow_relative_path_within_project(self, temp_project):
        """
        Test that legitimate relative paths within project are allowed.

        Simulates: INCLUDE "shared.dql" (same directory)
        """
        resolver = FileResolver(base_path=temp_project["project"])

        # Should succeed - file is in same directory
        resolved = resolver.resolve(
            "shared.dql",
            current_file=temp_project["customer_file"]
        )

        assert resolved == temp_project["shared_file"]
        assert resolved.exists()

    def test_allow_subdirectory_within_project(self, temp_project):
        """
        Test that subdirectories within project are allowed.

        Simulates: INCLUDE "models/shared.dql" from project root
        """
        resolver = FileResolver(base_path=temp_project["project"])

        # Should succeed - file is within project
        resolved = resolver.resolve("models/shared.dql")

        assert resolved == temp_project["shared_file"]
        assert resolved.exists()

    def test_reject_symlink_outside_project(self, temp_project):
        """
        Test that symlinks pointing outside project are rejected.

        This prevents symlink-based path traversal attacks.
        """
        # Create symlink inside project pointing to sensitive file outside
        symlink_path = temp_project["models_dir"] / "evil_symlink.dql"
        symlink_path.symlink_to(temp_project["sensitive_file"])

        resolver = FileResolver(base_path=temp_project["project"])

        # Should reject - symlink resolves outside project
        with pytest.raises(DQLSyntaxError) as exc_info:
            resolver.resolve(
                "evil_symlink.dql",
                current_file=temp_project["customer_file"]
            )

        assert "resolves outside project boundary" in str(exc_info.value)

    def test_boundary_case_exact_base_path(self, temp_project):
        """
        Test file exactly at base_path boundary is allowed.

        Simulates: INCLUDE "../root_file.dql" from models/ to project root
        """
        # Create file at project root
        root_file = temp_project["project"] / "root.dql"
        root_file.write_text("from Root\nexpect column(\"x\") to_not_be_null")

        resolver = FileResolver(base_path=temp_project["project"])

        # Should succeed - file is at project root (still within project)
        resolved = resolver.resolve(
            "../root.dql",
            current_file=temp_project["customer_file"]
        )

        assert resolved == root_file
        assert resolved.exists()

    def test_error_message_includes_helpful_suggestion(self, temp_project):
        """
        Test that error message includes helpful fix suggestion.
        """
        resolver = FileResolver(base_path=temp_project["project"])

        with pytest.raises(DQLSyntaxError) as exc_info:
            resolver.resolve(
                "../../sensitive/secrets.txt",
                current_file=temp_project["customer_file"]
            )

        error = exc_info.value
        assert error.suggested_fix is not None
        assert "relative paths within project directory only" in error.suggested_fix
        assert "security" in error.suggested_fix.lower()

    def test_multiple_levels_within_project_allowed(self, temp_project):
        """
        Test that multiple directory levels within project are allowed.

        Create: project/models/customers/vip/special.dql
        """
        # Create deep directory structure
        deep_dir = temp_project["models_dir"] / "customers" / "vip"
        deep_dir.mkdir(parents=True)

        deep_file = deep_dir / "special.dql"
        deep_file.write_text("from VIP\nexpect column(\"tier\") to_not_be_null")

        resolver = FileResolver(base_path=temp_project["project"])

        # Should succeed - all within project
        resolved = resolver.resolve("models/customers/vip/special.dql")

        assert resolved == deep_file
        assert resolved.exists()

    def test_normalize_redundant_paths_within_project(self, temp_project):
        """
        Test that redundant path components are normalized (but still validated).

        Simulates: INCLUDE "./subdir/../shared.dql" (normalizes to "shared.dql")
        """
        resolver = FileResolver(base_path=temp_project["project"])

        # Should succeed - normalizes to valid path within project
        resolved = resolver.resolve(
            "./subdir/../shared.dql",
            current_file=temp_project["customer_file"]
        )

        assert resolved == temp_project["shared_file"]
        assert resolved.exists()


class TestSecurityBestPractices:
    """Test other security best practices in the parser."""

    def test_no_shell_command_execution(self):
        """Verify no shell commands are executed during parsing."""
        # This is a documentation test - FileResolver should never use:
        # - os.system()
        # - subprocess
        # - exec()
        # - eval()

        from dql_parser import file_resolver
        import inspect

        source = inspect.getsource(file_resolver)

        # Check for dangerous patterns
        dangerous_patterns = [
            "os.system",
            "subprocess",
            "exec(",
            "eval(",
            "__import__",
        ]

        for pattern in dangerous_patterns:
            assert pattern not in source, f"Found dangerous pattern: {pattern}"

    def test_file_resolver_uses_pathlib(self):
        """Verify FileResolver uses pathlib (safer than string manipulation)."""
        from dql_parser import file_resolver
        import inspect

        source = inspect.getsource(file_resolver.FileResolver)

        # Should use Path objects, not string concatenation
        assert "from pathlib import Path" in inspect.getsource(file_resolver)
        assert "Path(" in source or "self.base_path" in source
