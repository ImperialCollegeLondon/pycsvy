"""Tests for utility functions."""

import warnings

from csvy.utils import merge_csv_options_with_dialect
from csvy.validators import CSVDialectValidator


def test_merge_csv_options_with_dialect_no_dialect():
    """Test merging options when no dialect is present in header."""
    header = {"title": "Test"}
    csv_options = {"delimiter": ",", "quotechar": '"'}

    merged_options, updated_header = merge_csv_options_with_dialect(header, csv_options)

    assert merged_options == csv_options
    assert updated_header == header


def test_merge_csv_options_with_dialect_no_options():
    """Test merging when no CSV options are provided."""
    header = {
        "title": "Test",
        "csv_dialect": CSVDialectValidator(delimiter=";", quotechar="'"),
    }
    csv_options = None

    merged_options, updated_header = merge_csv_options_with_dialect(header, csv_options)

    # Should get all dialect options
    expected_options = {
        "delimiter": ";",
        "quotechar": "'",
        "doublequote": True,
        "escapechar": None,
        "lineterminator": "\r\n",
        "skipinitialspace": False,
    }
    assert merged_options == expected_options
    assert updated_header == header


def test_merge_csv_options_with_dialect_basic_merge():
    """Test basic merging of dialect and user options."""
    header = {
        "title": "Test",
        "csv_dialect": CSVDialectValidator(delimiter=";", quotechar="'"),
    }
    csv_options = {"delimiter": ","}

    merged_options, updated_header = merge_csv_options_with_dialect(header, csv_options)

    # User option should override dialect
    expected_options = {
        "delimiter": ",",
        "quotechar": "'",
        "doublequote": True,
        "escapechar": None,
        "lineterminator": "\r\n",
        "skipinitialspace": False,
    }
    assert merged_options == expected_options


def test_merge_csv_options_with_dialect_conflict_warning():
    """Test that conflicts between user options and dialect generate warnings."""
    header = {
        "title": "Test",
        "csv_dialect": CSVDialectValidator(delimiter=";", quotechar="'"),
    }
    csv_options = {"delimiter": ","}

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        merged_options, updated_header = merge_csv_options_with_dialect(
            header, csv_options
        )

        assert len(w) == 1
        assert "delimiter" in str(w[0].message)
        assert "conflicts" in str(w[0].message)
        assert "'('" in str(w[0].message)  # Should show the conflicting values


def test_merge_csv_options_with_dialect_header_update():
    """Test that header is updated when user options override dialect."""
    header = {
        "title": "Test",
        "csv_dialect": CSVDialectValidator(delimiter=";", quotechar="'"),
    }
    csv_options = {"delimiter": ","}

    merged_options, updated_header = merge_csv_options_with_dialect(header, csv_options)

    # Original header should be unchanged
    assert header["csv_dialect"].delimiter == ";"
    # Updated header should reflect the override
    assert updated_header["csv_dialect"].delimiter == ","
    # They should be different objects
    assert updated_header is not header


def test_merge_csv_options_with_dialect_multiple_conflicts():
    """Test handling multiple conflicting options."""
    header = {
        "title": "Test",
        "csv_dialect": CSVDialectValidator(
            delimiter=";", quotechar="'", doublequote=False
        ),
    }
    csv_options = {"delimiter": ",", "quotechar": '"', "doublequote": True}

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        merged_options, updated_header = merge_csv_options_with_dialect(
            header, csv_options
        )

        # Should have warnings for delimiter and doublequote conflicts
        assert len(w) >= 2
        warning_messages = [str(warning.message) for warning in w]
        assert any(
            "delimiter" in msg and "conflicts" in msg for msg in warning_messages
        )
        assert any(
            "doublequote" in msg and "conflicts" in msg for msg in warning_messages
        )


def test_merge_csv_options_with_dialect_no_conflicts():
    """Test merging when user options don't conflict with dialect."""
    header = {
        "title": "Test",
        "csv_dialect": CSVDialectValidator(delimiter=";", quotechar="'"),
    }
    csv_options = {"delimiter": ";", "quotechar": "'"}

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        merged_options, updated_header = merge_csv_options_with_dialect(
            header, csv_options
        )

        # Should have no warnings since values match
        assert len(w) == 0

        # Should include both user option and all dialect options
        assert merged_options["delimiter"] == ";"
        assert merged_options["quotechar"] == "'"
