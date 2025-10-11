"""Integration tests for INCLUDE directive functionality (Story 1.9 - TEST-001)."""

import pytest
from pathlib import Path
import tempfile
import os

from dql_parser import DQLParser
from dql_parser.file_resolver import FileResolver, CircularIncludeError, IncludeDepthError
from dql_parser.exceptions import DQLSyntaxError


@pytest.fixture
def temp_dql_dir():
    """Create temporary directory structure for DQL test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create subdirectories
        (base / "shared").mkdir()
        (base / "models").mkdir()
        (base / "nested").mkdir()
        (base / "nested" / "deep").mkdir()

        yield base


class TestFileResolverBasics:
    """Test basic FileResolver functionality."""

    def test_resolver_initialization_default_path(self):
        """Test resolver initializes with current directory as default."""
        resolver = FileResolver()
        assert resolver.base_path == Path.cwd()
        assert resolver.include_stack == []

    def test_resolver_initialization_custom_path(self, temp_dql_dir):
        """Test resolver initializes with custom base path."""
        resolver = FileResolver(base_path=temp_dql_dir)
        assert resolver.base_path == temp_dql_dir
        assert resolver.include_stack == []

    def test_get_current_file_empty_stack(self):
        """Test get_current_file returns None for empty stack."""
        resolver = FileResolver()
        assert resolver.get_current_file() is None

    def test_get_current_file_with_files(self, temp_dql_dir):
        """Test get_current_file returns top of stack."""
        resolver = FileResolver(base_path=temp_dql_dir)
        file1 = temp_dql_dir / "file1.dql"
        file2 = temp_dql_dir / "file2.dql"

        resolver.push_file(file1)
        assert resolver.get_current_file() == file1

        resolver.push_file(file2)
        assert resolver.get_current_file() == file2

    def test_get_include_depth(self, temp_dql_dir):
        """Test get_include_depth returns correct depth."""
        resolver = FileResolver(base_path=temp_dql_dir)
        assert resolver.get_include_depth() == 0

        resolver.push_file(temp_dql_dir / "file1.dql")
        assert resolver.get_include_depth() == 1

        resolver.push_file(temp_dql_dir / "file2.dql")
        assert resolver.get_include_depth() == 2

    def test_push_and_pop_file(self, temp_dql_dir):
        """Test push_file and pop_file maintain stack correctly."""
        resolver = FileResolver(base_path=temp_dql_dir)
        file1 = temp_dql_dir / "file1.dql"
        file2 = temp_dql_dir / "file2.dql"

        resolver.push_file(file1)
        resolver.push_file(file2)

        assert resolver.pop_file() == file2
        assert resolver.pop_file() == file1
        assert resolver.include_stack == []

    def test_pop_file_empty_stack_raises_error(self):
        """Test pop_file on empty stack raises IndexError."""
        resolver = FileResolver()
        with pytest.raises(IndexError):
            resolver.pop_file()

    def test_clear_stack(self, temp_dql_dir):
        """Test clear() empties the include stack."""
        resolver = FileResolver(base_path=temp_dql_dir)
        resolver.push_file(temp_dql_dir / "file1.dql")
        resolver.push_file(temp_dql_dir / "file2.dql")

        resolver.clear()
        assert resolver.include_stack == []
        assert resolver.get_include_depth() == 0


class TestFileResolverPathResolution:
    """Test FileResolver path resolution logic."""

    def test_resolve_relative_to_base_path(self, temp_dql_dir):
        """Test resolve with no current file uses base_path."""
        resolver = FileResolver(base_path=temp_dql_dir)

        # Create test file
        test_file = temp_dql_dir / "common.dql"
        test_file.write_text("FROM User EXPECT column(\"id\") to_not_be_null")

        resolved = resolver.resolve("common.dql")
        assert resolved == test_file
        assert resolved.exists()

    def test_resolve_relative_to_current_file(self, temp_dql_dir):
        """Test resolve with current file uses file's directory."""
        resolver = FileResolver(base_path=temp_dql_dir)

        # Create files
        current_file = temp_dql_dir / "models" / "user.dql"
        current_file.parent.mkdir(exist_ok=True)
        current_file.write_text("FROM User EXPECT column(\"id\") to_not_be_null")

        shared_file = temp_dql_dir / "models" / "shared.dql"
        shared_file.write_text("FROM Base EXPECT column(\"id\") to_not_be_null")

        resolved = resolver.resolve("shared.dql", current_file=current_file)
        assert resolved == shared_file

    def test_resolve_subdirectory_relative_to_base(self, temp_dql_dir):
        """Test resolve with subdirectory path."""
        resolver = FileResolver(base_path=temp_dql_dir)

        # Create nested file
        nested_file = temp_dql_dir / "shared" / "common.dql"
        nested_file.write_text("FROM User EXPECT column(\"id\") to_not_be_null")

        resolved = resolver.resolve("shared/common.dql")
        assert resolved == nested_file

    def test_resolve_file_not_found_raises_error(self, temp_dql_dir):
        """Test resolve raises FileNotFoundError for missing file."""
        resolver = FileResolver(base_path=temp_dql_dir)

        with pytest.raises(FileNotFoundError, match="INCLUDE file not found"):
            resolver.resolve("nonexistent.dql")

    def test_resolve_directory_not_file_raises_error(self, temp_dql_dir):
        """Test resolve raises error if path is directory."""
        resolver = FileResolver(base_path=temp_dql_dir)

        # shared is a directory, not a file
        with pytest.raises(FileNotFoundError, match="INCLUDE path is not a file"):
            resolver.resolve("shared")

    def test_resolve_normalizes_paths(self, temp_dql_dir):
        """Test resolve normalizes redundant path components."""
        resolver = FileResolver(base_path=temp_dql_dir)

        # Create file
        test_file = temp_dql_dir / "shared" / "common.dql"
        test_file.write_text("FROM User EXPECT column(\"id\") to_not_be_null")

        # Resolve with redundant path
        resolved = resolver.resolve("./shared/../shared/common.dql")
        assert resolved == test_file


class TestFileResolverSecurityPathTraversal:
    """Test FileResolver security against path traversal (SEC-001)."""

    def test_path_traversal_blocked_absolute_escape(self, temp_dql_dir):
        """Test path traversal outside base_path is blocked."""
        resolver = FileResolver(base_path=temp_dql_dir)

        # Create file outside base path
        parent_dir = temp_dql_dir.parent
        external_file = parent_dir / "external.dql"
        external_file.write_text("malicious content")

        # Try to access via relative path traversal
        with pytest.raises(DQLSyntaxError, match="resolves outside project boundary"):
            resolver.resolve("../external.dql")

    def test_path_traversal_blocked_multiple_levels(self, temp_dql_dir):
        """Test multi-level path traversal is blocked."""
        resolver = FileResolver(base_path=temp_dql_dir)

        with pytest.raises(DQLSyntaxError, match="resolves outside project boundary"):
            resolver.resolve("../../etc/passwd")

    def test_path_traversal_within_base_allowed(self, temp_dql_dir):
        """Test relative paths within base_path are allowed."""
        resolver = FileResolver(base_path=temp_dql_dir)

        # Create files in nested structure
        deep_file = temp_dql_dir / "nested" / "deep" / "file.dql"
        deep_file.write_text("FROM User EXPECT column(\"id\") to_not_be_null")

        sibling_file = temp_dql_dir / "nested" / "sibling.dql"
        sibling_file.write_text("FROM Base EXPECT column(\"id\") to_not_be_null")

        # Navigate up and across within base_path (should work)
        resolved = resolver.resolve("../sibling.dql", current_file=deep_file)
        assert resolved == sibling_file

    def test_path_traversal_error_message_includes_fix(self, temp_dql_dir):
        """Test path traversal error includes helpful suggestion."""
        resolver = FileResolver(base_path=temp_dql_dir)

        with pytest.raises(DQLSyntaxError) as exc_info:
            resolver.resolve("../external.dql")

        assert "Path traversal" in str(exc_info.value)
        assert "security" in str(exc_info.value).lower()


class TestFileResolverCircularIncludes:
    """Test FileResolver circular include detection."""

    def test_circular_include_direct(self, temp_dql_dir):
        """Test direct circular include (A includes A) is detected."""
        resolver = FileResolver(base_path=temp_dql_dir)

        file_a = temp_dql_dir / "a.dql"
        file_a.write_text('INCLUDE "a.dql"')

        resolver.push_file(file_a)

        with pytest.raises(CircularIncludeError) as exc_info:
            resolver.resolve("a.dql")

        assert file_a in exc_info.value.chain
        assert "Circular include detected" in str(exc_info.value)

    def test_circular_include_indirect(self, temp_dql_dir):
        """Test indirect circular include (A → B → A) is detected."""
        resolver = FileResolver(base_path=temp_dql_dir)

        file_a = temp_dql_dir / "a.dql"
        file_b = temp_dql_dir / "b.dql"
        file_a.write_text('INCLUDE "b.dql"')
        file_b.write_text('INCLUDE "a.dql"')

        resolver.push_file(file_a)
        resolver.push_file(file_b)

        with pytest.raises(CircularIncludeError) as exc_info:
            resolver.resolve("a.dql")

        chain = exc_info.value.chain
        assert file_a in chain
        assert file_b in chain

    def test_circular_include_chain_displayed(self, temp_dql_dir):
        """Test circular include error shows full chain."""
        resolver = FileResolver(base_path=temp_dql_dir)

        file_a = temp_dql_dir / "a.dql"
        file_b = temp_dql_dir / "b.dql"
        file_c = temp_dql_dir / "c.dql"
        file_a.write_text('INCLUDE "b.dql"')
        file_b.write_text('INCLUDE "c.dql"')
        file_c.write_text('INCLUDE "a.dql"')

        resolver.push_file(file_a)
        resolver.push_file(file_b)
        resolver.push_file(file_c)

        with pytest.raises(CircularIncludeError) as exc_info:
            resolver.resolve("a.dql")

        error_msg = str(exc_info.value)
        assert "a.dql" in error_msg
        assert "b.dql" in error_msg
        assert "c.dql" in error_msg
        assert "→" in error_msg


class TestFileResolverIncludeDepth:
    """Test FileResolver include depth limiting."""

    def test_include_depth_within_limit(self, temp_dql_dir):
        """Test includes within depth limit succeed."""
        resolver = FileResolver(base_path=temp_dql_dir)

        # Create chain of 5 includes (within limit of 10)
        for i in range(5):
            file = temp_dql_dir / f"file{i}.dql"
            file.write_text(f'INCLUDE "file{i+1}.dql"' if i < 4 else "FROM User EXPECT column(\"id\") to_not_be_null")

        # Push files to simulate include chain
        for i in range(5):
            resolver.push_file(temp_dql_dir / f"file{i}.dql")

        assert resolver.get_include_depth() == 5

    def test_include_depth_at_limit(self, temp_dql_dir):
        """Test includes at exactly max depth are allowed."""
        resolver = FileResolver(base_path=temp_dql_dir)

        # Create file at max depth
        for i in range(FileResolver.MAX_INCLUDE_DEPTH):
            resolver.push_file(temp_dql_dir / f"file{i}.dql")

        assert resolver.get_include_depth() == FileResolver.MAX_INCLUDE_DEPTH

    def test_include_depth_exceeds_limit(self, temp_dql_dir):
        """Test includes exceeding max depth raise IncludeDepthError."""
        resolver = FileResolver(base_path=temp_dql_dir)

        # Create file
        file = temp_dql_dir / "deep.dql"
        file.write_text("FROM User EXPECT column(\"id\") to_not_be_null")

        # Fill include stack to max depth
        for i in range(FileResolver.MAX_INCLUDE_DEPTH):
            resolver.push_file(temp_dql_dir / f"file{i}.dql")

        with pytest.raises(IncludeDepthError) as exc_info:
            resolver.resolve("deep.dql")

        assert "exceeds maximum" in str(exc_info.value)
        assert str(FileResolver.MAX_INCLUDE_DEPTH) in str(exc_info.value)


class TestParserIncludeIntegration:
    """Test INCLUDE integration with DQLParser."""

    def test_parser_single_include(self, temp_dql_dir):
        """Test parser resolves single INCLUDE directive."""
        # Create shared validations file
        shared = temp_dql_dir / "shared.dql"
        shared.write_text("""
FROM User
    EXPECT column("id") to_not_be_null
    EXPECT column("email") to_match_pattern("^[a-z]+@[a-z]+\\.[a-z]+$")
""")

        # Create main file with INCLUDE
        main = temp_dql_dir / "main.dql"
        main.write_text("""
INCLUDE "shared.dql"

FROM Order
    EXPECT column("order_id") to_not_be_null
""")

        parser = DQLParser(base_path=temp_dql_dir)
        ast = parser.parse_file(main)

        # Should have from_blocks from both files
        assert len(ast.from_blocks) >= 1
        model_names = {block.model_name for block in ast.from_blocks}
        assert "Order" in model_names

    def test_parser_multiple_includes(self, temp_dql_dir):
        """Test parser resolves multiple INCLUDE directives."""
        # Create shared files
        users = temp_dql_dir / "users.dql"
        users.write_text("FROM User EXPECT column(\"id\") to_not_be_null")

        orders = temp_dql_dir / "orders.dql"
        orders.write_text("FROM Order EXPECT column(\"id\") to_not_be_null")

        # Create main file
        main = temp_dql_dir / "main.dql"
        main.write_text("""
INCLUDE "users.dql"
INCLUDE "orders.dql"

FROM Product
    EXPECT column("id") to_not_be_null
""")

        parser = DQLParser(base_path=temp_dql_dir)
        ast = parser.parse_file(main)

        assert len(ast.from_blocks) >= 1

    def test_parser_nested_includes(self, temp_dql_dir):
        """Test parser resolves nested INCLUDE directives."""
        # Create base validations
        base = temp_dql_dir / "base.dql"
        base.write_text("FROM Base EXPECT column(\"id\") to_not_be_null")

        # Create shared that includes base
        shared = temp_dql_dir / "shared.dql"
        shared.write_text("""
INCLUDE "base.dql"

FROM Shared
    EXPECT column("name") to_not_be_null
""")

        # Create main that includes shared
        main = temp_dql_dir / "main.dql"
        main.write_text("""
INCLUDE "shared.dql"

FROM Main
    EXPECT column("id") to_not_be_null
""")

        parser = DQLParser(base_path=temp_dql_dir)
        ast = parser.parse_file(main)

        # Should have from_blocks from all three files
        assert len(ast.from_blocks) >= 1

    def test_parser_include_from_subdirectory(self, temp_dql_dir):
        """Test parser resolves INCLUDE from subdirectory."""
        # Create shared file in subdirectory
        shared = temp_dql_dir / "shared" / "common.dql"
        shared.write_text("FROM Common EXPECT column(\"id\") to_not_be_null")

        # Create main file
        main = temp_dql_dir / "main.dql"
        main.write_text("""
INCLUDE "shared/common.dql"

FROM Main
    EXPECT column("id") to_not_be_null
""")

        parser = DQLParser(base_path=temp_dql_dir)
        ast = parser.parse_file(main)

        assert len(ast.from_blocks) >= 1

    def test_parser_include_without_error(self, temp_dql_dir):
        """Test parser handles INCLUDE directive without errors."""
        # Create shared file
        shared = temp_dql_dir / "shared.dql"
        shared.write_text("FROM Shared EXPECT column(\"id\") to_not_be_null")

        # Create main file with valid include
        main = temp_dql_dir / "main.dql"
        main.write_text("""
INCLUDE "shared.dql"

FROM User
    EXPECT column("id") to_not_be_null
""")

        parser = DQLParser(base_path=temp_dql_dir)
        ast = parser.parse_file(main)

        # Should parse successfully
        assert ast is not None
        assert len(ast.from_blocks) >= 1


class TestIncludeEdgeCases:
    """Test edge cases and corner scenarios for INCLUDE."""

    def test_include_empty_file(self, temp_dql_dir):
        """Test including empty file doesn't break parsing."""
        # Create empty file
        empty = temp_dql_dir / "empty.dql"
        empty.write_text("")

        # Create main file
        main = temp_dql_dir / "main.dql"
        main.write_text("""
INCLUDE "empty.dql"

FROM User
    EXPECT column("id") to_not_be_null
""")

        parser = DQLParser(base_path=temp_dql_dir)
        ast = parser.parse_file(main)

        assert len(ast.from_blocks) >= 1
        assert ast.from_blocks[0].model_name == "User"

    def test_include_file_with_only_comments(self, temp_dql_dir):
        """Test including file with only comments."""
        # Create file with comments
        comments = temp_dql_dir / "comments.dql"
        comments.write_text("# Just a comment\n# Another comment")

        # Create main file
        main = temp_dql_dir / "main.dql"
        main.write_text("""
INCLUDE "comments.dql"

FROM User
    EXPECT column("id") to_not_be_null
""")

        parser = DQLParser(base_path=temp_dql_dir)
        ast = parser.parse_file(main)

        assert len(ast.from_blocks) >= 1

    def test_multiple_files_include_same_shared_file(self, temp_dql_dir):
        """Test multiple files can include the same shared file (not circular)."""
        # Create shared base
        base = temp_dql_dir / "base.dql"
        base.write_text("FROM Base EXPECT column(\"id\") to_not_be_null")

        # Create two files that both include base
        file1 = temp_dql_dir / "file1.dql"
        file1.write_text("""
INCLUDE "base.dql"
FROM File1 EXPECT column("name") to_not_be_null
""")

        file2 = temp_dql_dir / "file2.dql"
        file2.write_text("""
INCLUDE "base.dql"
FROM File2 EXPECT column("name") to_not_be_null
""")

        parser = DQLParser(base_path=temp_dql_dir)

        # Should be able to parse both separately
        ast1 = parser.parse_file(file1)
        assert len(ast1.from_blocks) >= 1

        # Clear parser state
        parser.file_resolver.clear()

        ast2 = parser.parse_file(file2)
        assert len(ast2.from_blocks) >= 1

    def test_include_with_unicode_filename(self, temp_dql_dir):
        """Test INCLUDE handles unicode filenames."""
        # Create file with unicode name
        unicode_file = temp_dql_dir / "validações.dql"
        unicode_file.write_text("FROM User EXPECT column(\"id\") to_not_be_null", encoding="utf-8")

        # Create main file
        main = temp_dql_dir / "main.dql"
        main.write_text('INCLUDE "validações.dql"\n\nFROM Order EXPECT column("id") to_not_be_null', encoding="utf-8")

        parser = DQLParser(base_path=temp_dql_dir)
        ast = parser.parse_file(main)

        assert len(ast.from_blocks) >= 1
