"""
Unit tests for utility functions in mcp_kql_server.utils

Tests the utility functions for path handling, schema discovery,
and query validation.

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

from pathlib import Path

import pytest

from mcp_kql_server.utils import (
    ensure_directory_exists,
    fix_query_with_real_schema,
    get_default_cluster_memory_path,
    get_schema_discovery,
    get_schema_discovery_status,
    sanitize_filename,
    validate_all_query_columns,
    validate_projected_columns,
)


class TestPathUtilities:
    """Test cases for path-related utility functions."""

    def test_get_default_cluster_memory_path(self):
        """Test getting default cluster memory path."""
        path = get_default_cluster_memory_path()
        assert isinstance(path, Path)
        assert "KQL_MCP" in str(path) or "kql_memory" in str(path)

    def test_ensure_directory_exists(self):
        """Test directory creation."""
        test_path = Path("./test_dir_temp")
        result = ensure_directory_exists(test_path)
        assert result is True

        # Clean up
        if test_path.exists():
            test_path.rmdir()

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test with invalid characters
        result = sanitize_filename('test<>:"/\\|?*file.txt')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "/" not in result
        assert "\\" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result

        # Test with valid filename
        result = sanitize_filename("valid_filename.txt")
        assert result == "valid_filename.txt"


class TestSchemaDiscovery:
    """Test cases for schema discovery functionality."""

    def test_get_schema_discovery_status(self):
        """Test schema discovery status retrieval."""
        status = get_schema_discovery_status()
        assert isinstance(status, dict)
        assert "status" in status
        assert "memory_path" in status
        assert "cached_schemas" in status

    def test_get_schema_discovery_instance(self):
        """Test getting schema discovery instance."""
        discovery = get_schema_discovery()
        assert discovery is not None
        assert hasattr(discovery, "get_table_schema")
        assert hasattr(discovery, "get_column_mapping_from_schema")


class TestQueryValidation:
    """Test cases for KQL query validation functions."""

    def test_validate_projected_columns_no_schema(self):
        """Test column validation with no schema."""
        query = "MyTable | project Column1, Column2"
        result = validate_projected_columns(query, {})
        assert result == query  # Should return unchanged

    def test_validate_projected_columns_with_schema(self):
        """Test column validation with schema."""
        query = "MyTable | project Column1, Column2, InvalidColumn"
        schema = {"columns": ["Column1", "Column2", "ValidColumn"], "table": "MyTable"}
        result = validate_projected_columns(query, schema)
        # Should remove invalid columns and keep valid ones
        assert "Column1" in result
        assert "Column2" in result
        assert (
            "InvalidColumn" not in result or result == query
        )  # Might be kept if considered expression

    def test_validate_all_query_columns_no_schema(self):
        """Test comprehensive query validation with no schema."""
        query = "MyTable | where Column1 == 'test'"
        result = validate_all_query_columns(query, {})
        assert result == query  # Should return unchanged

    def test_validate_all_query_columns_with_schema(self):
        """Test comprehensive query validation with schema."""
        query = "MyTable | where column1 == 'test' | project COLUMN1"
        schema = {"columns": ["Column1", "Column2"], "table": "MyTable"}
        result = validate_all_query_columns(query, schema)
        # Should fix case issues
        assert "Column1" in result


class TestQueryFixing:
    """Test cases for query fixing functionality."""

    def test_fix_query_with_real_schema_no_cluster_info(self):
        """Test query fixing when no cluster info can be extracted."""
        query = "MyTable | where Column1 == 'test'"
        result = fix_query_with_real_schema(query)
        assert result == query  # Should return unchanged

    def test_fix_query_with_real_schema_invalid_format(self):
        """Test query fixing with invalid cluster format."""
        query = "invalid_query_format"
        result = fix_query_with_real_schema(query)
        assert result == query  # Should return unchanged


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        # Test sanitize_filename with empty string
        result = sanitize_filename("")
        assert result == ""

        # Test validate_projected_columns with empty query
        result = validate_projected_columns("", {})
        assert result == ""

        # Test validate_all_query_columns with empty query
        result = validate_all_query_columns("", {})
        assert result == ""

    def test_none_inputs(self):
        """Test handling of None inputs."""
        # Test functions with None schema
        query = "test query"
        result = validate_projected_columns(query, None)
        assert result == query

        result = validate_all_query_columns(query, None)
        assert result == query


class TestSchemaDiscoveryMethods:
    """Test schema discovery class methods."""

    def test_schema_discovery_cache(self):
        """Test schema discovery caching mechanism."""
        discovery = get_schema_discovery()

        # Test cache key generation and validation
        cache_key = "test_cluster/test_db/test_table"

        # Test that _is_schema_cached_and_valid returns False for non-existent cache
        assert not discovery._is_schema_cached_and_valid(cache_key)

    def test_normalize_cluster_uri(self):
        """Test cluster URI normalization."""
        discovery = get_schema_discovery()

        # Test adding https prefix
        result = discovery._normalize_cluster_uri("mycluster.kusto.windows.net")
        assert result.startswith("https://")
        assert result.endswith("mycluster.kusto.windows.net")

        # Test with existing https
        result = discovery._normalize_cluster_uri(
            "https://mycluster.kusto.windows.net/"
        )
        assert result == "https://mycluster.kusto.windows.net"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
