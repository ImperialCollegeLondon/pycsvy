"""Tests for the csvy reader functions."""

from unittest.mock import patch

import pytest


def test_get_comment():
    """Test the get_comment function."""
    from csvy.readers import get_comment

    assert "" == get_comment("--- Something else")
    assert "# " == get_comment("# ---")
    assert "# " == get_comment("# @@", marker="@@")

    with pytest.raises(ValueError):
        get_comment("Wrong marker")


def test_get_header(data_path, data_comment_path):
    """Test the read_header function."""
    from csvy.readers import read_header

    header, nlines, comment = read_header(data_path)
    assert isinstance(header, dict)
    assert "freq" in header.keys()
    assert nlines == 18
    assert comment == ""

    header2, nlines, comment = read_header(data_comment_path)
    assert isinstance(header2, dict)
    assert "freq" in header.keys()
    assert nlines == 18
    assert comment == "# "

    assert header == header2


@patch("csvy.readers.read_header")
def test_read_metadata(read_header_mock, data_path):
    """Test the read_metadata function."""
    from csvy import read_metadata

    read_header_mock.return_value = ("a", "b")

    filename = "test.csv"
    marker = "!!!"
    encoding = "hieroglyphics"
    kwargs = {"key": "value"}
    assert (
        read_metadata(filename=filename, marker=marker, encoding=encoding, **kwargs)
        == "a"
    )

    read_header_mock.assert_called_once_with(filename, marker, encoding, **kwargs)


def test_read_to_array(array_data_path):
    """Test the read_to_array function."""
    import numpy as np

    from csvy.readers import read_to_array

    data, header = read_to_array(array_data_path, csv_options={"delimiter": ","})
    assert isinstance(data, np.ndarray)
    assert data.shape == (15, 4)
    assert isinstance(header, dict)
    assert len(header) > 0

    import csvy.readers as readers

    readers.NDArray = None  # type: ignore [assignment]

    with pytest.raises(ModuleNotFoundError):
        read_to_array(array_data_path)


def test_read_to_dataframe(data_path):
    """Test the read_to_dataframe function."""
    import pandas as pd

    from csvy import read_to_dataframe

    data, header = read_to_dataframe(data_path)
    assert isinstance(data, pd.DataFrame)
    assert tuple(data.columns) == ("Date", "WTI")
    assert isinstance(header, dict)
    assert len(header) > 0

    import csvy.readers as readers

    readers.DataFrame = None  # type: ignore [assignment]

    with pytest.raises(ModuleNotFoundError):
        read_to_dataframe(data_path)


def test_read_to_polars(data_path):
    """Test the read_to_polars function."""
    import polars as pl
    from polars.testing import assert_frame_equal

    from csvy import read_to_polars

    lazy_data, header = read_to_polars(data_path)
    assert isinstance(lazy_data, pl.LazyFrame)
    assert tuple(lazy_data.collect_schema().names()) == ("Date", "WTI")
    assert isinstance(header, dict)
    assert len(header) > 0

    eager_data, _ = read_to_polars(data_path, eager=True)
    assert_frame_equal(lazy_data.collect(), eager_data)

    import csvy.readers as readers

    readers.LazyFrame = None  # type: ignore [assignment, misc]

    with pytest.raises(ModuleNotFoundError):
        read_to_polars(data_path)

    with pytest.raises(ValueError):
        read_to_polars(data_path, encoding="utf-9")  # type: ignore [arg-type]


def test_read_to_list(array_data_path):
    """Test the read_to_list function."""
    from csvy import read_to_list

    data, header = read_to_list(array_data_path, csv_options={"delimiter": ","})
    assert isinstance(data, list)
    assert len(data) == 15
    assert len(data[0]) == 4
    assert isinstance(header, dict)
    assert len(header) > 0


def test_read_to_dict_with_default_column_names(array_data_path):
    """Test the read_to_list function."""
    from csvy import read_to_dict

    data, header = read_to_dict(array_data_path, csv_options={"delimiter": ","})

    assert isinstance(data, dict)
    assert len(data) == 4
    assert list(data.keys()) == ["col_0", "col_1", "col_2", "col_3"]
    assert len(data["col_0"]) == 15
    assert len(header) > 0


def test_read_to_dict_with_custom_column_names(array_data_path):
    """Test the read_to_list function."""
    from csvy import read_to_dict

    column_names = ["A", "B", "C", "D"]
    data, header = read_to_dict(
        array_data_path, column_names=column_names, csv_options={"delimiter": ","}
    )

    assert isinstance(data, dict)
    assert len(data) == 4
    assert list(data.keys()) == column_names
    assert len(data["A"]) == 15
    assert len(header) > 0


def test_read_to_dict_with_row_based_column_names(data_path):
    """Test the read_to_list function."""
    from csvy import read_to_dict

    data, header = read_to_dict(
        data_path, column_names=0, csv_options={"delimiter": ","}
    )

    assert isinstance(data, dict)
    assert len(data) == 2
    assert list(data.keys()) == ["Date", "WTI"]
    assert len(data["Date"]) == 15
    assert len(header) > 0


def test_read_with_csv_dialect(tmp_path):
    """Test that CSV dialect information is used when reading."""
    from csvy.readers import read_to_list
    from csvy.validators import CSVDialectValidator

    csvy_content = """---
title: Test with dialect
csv_dialect:
  delimiter: ";"
  quotechar: "'"
---
name;age;city
'Alice';25;'New York'
'Bob';30;'London'
"""

    csvy_file = tmp_path / "test_dialect.csvy"
    csvy_file.write_text(csvy_content)

    data, header = read_to_list(csvy_file)

    expected_data = [
        ["name", "age", "city"],
        ["Alice", "25", "New York"],
        ["Bob", "30", "London"],
    ]
    assert data == expected_data

    assert "csv_dialect" in header
    dialect = header["csv_dialect"]
    assert isinstance(dialect, CSVDialectValidator)
    assert dialect.delimiter == ";"
    assert dialect.quotechar == "'"


def test_read_csv_options_override_dialect(tmp_path):
    """Test that user CSV options override dialect settings with warnings."""
    import warnings

    from csvy.readers import read_to_list

    csvy_content = """---
title: Test with dialect override
csv_dialect:
  delimiter: ";"
  quotechar: "'"
---
name;age;city
'Alice';25;'New York'
"""

    csvy_file = tmp_path / "test_dialect_override.csvy"
    csvy_file.write_text(csvy_content)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        data, header = read_to_list(csvy_file, csv_options={"delimiter": ","})

        assert len(w) >= 1
        assert "delimiter" in str(w[0].message)
        assert "conflicts" in str(w[0].message)

    assert len(data) == 1
    assert "name;age;city" in data[0][0]

    dialect = header["csv_dialect"]
    assert dialect.delimiter == ","