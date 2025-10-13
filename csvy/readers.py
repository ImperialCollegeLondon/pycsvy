"""A collection of functions for parsing CSVY files."""

from __future__ import annotations

import csv
import logging
import warnings
from itertools import zip_longest
from pathlib import Path
from typing import Any, Literal

import yaml

try:
    from numpy.typing import NDArray
except ModuleNotFoundError:
    NDArray = None  # type: ignore
    logging.getLogger().debug(
        "Numpy is not installed. Reading into an array will not work."
    )

try:
    from pandas import DataFrame
except ModuleNotFoundError:
    DataFrame = None  # type: ignore
    logging.getLogger().debug(
        "Pandas is not installed. Reading into a pd.DataFrame will not work."
    )

try:
    from polars import DataFrame as PolarsDataFrame
    from polars import LazyFrame
except ModuleNotFoundError:
    LazyFrame = None  # type: ignore
    PolarsDataFrame = None  # type: ignore
    logging.getLogger().debug(
        "Polars is not installed. Reading into a pl.DataFrame will not work."
    )

from .validators import CSVDialectValidator, validate_header


def get_comment(line: str, marker: str = "---") -> str:
    """Retrieve the comment character used in the header.

    Given that we know the header limiting markers are '---' it is possible to
    automatically find out the comment character by simply retrieving what is
    before the first occurrence of the marker. So, if we find '# ---', then we
    know that the comment characters are '# '.

    This will save the user to having to check the file before reading it.

    Args:
        line: Line of text, typically the first one of the file.
        marker: The marker characters that indicate the yaml header.

    Returns:
        The comment character found.

    """
    if marker not in line:
        raise ValueError(f"Yaml header marker '{marker}' not found in line '{line}'.")
    else:
        return "" if line.startswith(marker) else line.split(marker)[0]


def merge_csv_options_with_dialect(
    header: dict[str, Any],
    csv_options: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Merge CSV options with dialect information from header."""
    merged_options = csv_options.copy() if csv_options is not None else {}
    updated_header = header.copy()

    if "csv_dialect" in header and isinstance(
        header["csv_dialect"], CSVDialectValidator
    ):
        dialect_validator = header["csv_dialect"]

        dialect_mapping = {
            "delimiter": "delimiter",
            "quotechar": "quotechar",
            "escapechar": "escapechar",
            "doublequote": "doublequote",
            "skipinitialspace": "skipinitialspace",
            "lineterminator": "lineterminator",
        }

        dialect_updated = False
        for dialect_attr, csv_option in dialect_mapping.items():
            dialect_value = getattr(dialect_validator, dialect_attr)
            if csv_option in merged_options:
                user_value = merged_options[csv_option]
                if user_value != dialect_value:
                    warnings.warn(
                        f"CSV option '{csv_option}' ({user_value!r}) conflicts with "
                        f"dialect setting ({dialect_value!r}). Using user option.",
                        UserWarning,
                        stacklevel=2,
                    )
                    setattr(dialect_validator, dialect_attr, user_value)
                    dialect_updated = True
            else:
                merged_options[csv_option] = dialect_value

        if dialect_updated:
            updated_header["csv_dialect"] = dialect_validator

    return merged_options, updated_header


def read_header(
    filename: Path | str, marker: str = "---", encoding: str = "utf-8", **kwargs: Any
) -> tuple[dict[str, Any], int, str]:
    """Read the yaml-formatted header from a file.

    Args:
        filename: Name of the file to read the header from.
        marker: The marker characters that indicate the yaml header.
        encoding: The character encoding in the file to read.
        **kwargs: Arguments to pass to 'yaml.safe_load'.

    Returns:
        Tuple containing: a dictionary with the header information, the number of header
            lines, and the comment character.

    """
    header = []
    markers = 0
    nlines = 0
    comment = ""
    with Path(filename).open("r", encoding=encoding) as f:
        for line in f:
            if nlines == 0:
                comment = get_comment(line, marker=marker)

            nlines += 1
            if line.startswith(f"{comment}{marker}\n"):
                markers += 1
                if markers == 2:
                    break

            line = line.lstrip(comment)
            header.append(line)

    return validate_header(yaml.safe_load("".join(header), **kwargs)), nlines, comment


def read_metadata(
    filename: Path | str, marker: str = "---", encoding: str = "utf-8", **kwargs: Any
) -> dict[str, Any]:
    """Read the yaml-formatted metadata from a file.

    Args:
        filename: Name of the file to read the header from.
        marker: The marker characters that indicate the yaml header.
        encoding: The character encoding in the file to read.
        **kwargs: Arguments to pass to 'yaml.safe_load'.

    Returns:
        The metadata stored in the header.

    """
    return read_header(filename, marker, encoding, **kwargs)[0]


def read_to_array(
    filename: Path | str,
    marker: str = "---",
    encoding: str = "utf-8",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
) -> tuple[NDArray, dict[str, Any]]:
    """Read a CSVY file into dict with the header and array with the data.

    Args:
        filename:  Name of the file to read.
        marker: The marker characters that indicate the yaml header.
        encoding: The character encoding in the file to read.
        csv_options: Options to pass to np.loadtxt.
        yaml_options: Options to pass to yaml.safe_load.

    Raises:
        ModuleNotFoundError: If numpy is not found.

    Returns:
        Tuple containing: The numpy array and the header as a dictionary.

    """
    if NDArray is None:
        raise ModuleNotFoundError(
            "Module numpy is not present. Install it to read data into an array."
        )
    import numpy as np

    yaml_options = yaml_options if yaml_options is not None else {}
    header, nlines, comment = read_header(
        filename, marker=marker, encoding=encoding, **yaml_options
    )

    # Merge CSV options with dialect information
    merged_options, header = merge_csv_options_with_dialect(header, csv_options)

    options = merged_options.copy()
    options["skiprows"] = nlines + options.get("skiprows", 0)
    options["comments"] = comment[0] if len(comment) >= 1 else "#"

    # np.loadtxt only supports 'delimiter' from dialect options
    # Remove unsupported options
    supported_options = {"delimiter"}
    options = {
        k: v
        for k, v in options.items()
        if k in supported_options or k in ["skiprows", "comments"]
    }

    return np.loadtxt(filename, encoding=encoding, **options), header


def read_to_dataframe(
    filename: Path | str,
    marker: str = "---",
    encoding: str = "utf-8",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
) -> tuple[DataFrame, dict[str, Any]]:
    """Read a CSVY file into dict with the header and a DataFrame with the data.

    Possible 'skiprows' and 'comment' argument provided in the 'csv_options' dictionary
    will be ignored.

    Args:
        filename:  Name of the file to read.
        marker: The marker characters that indicate the yaml header.
        encoding: The character encoding in the file to read.
        csv_options: Options to pass to pd.read_csv.
        yaml_options: Options to pass to yaml.safe_load.

    Raises:
        ModuleNotFoundError: If pandas is not found.

    Returns:
        Tuple containing: The pandas DataFrame and the header as a dictionary.

    """
    if DataFrame is None:
        raise ModuleNotFoundError(
            "Module pandas is not present. Install it to read data into DataFrame."
        )
    import pandas as pd

    yaml_options = yaml_options if yaml_options is not None else {}
    header, nlines, comment = read_header(
        filename, marker=marker, encoding=encoding, **yaml_options
    )

    # Merge CSV options with dialect information
    merged_options, header = merge_csv_options_with_dialect(header, csv_options)

    options = merged_options.copy()
    options["skiprows"] = nlines
    options["comment"] = comment[0] if len(comment) >= 1 else None

    # Remove options that conflict with pandas read_csv requirements
    # pandas uses 'sep' instead of 'delimiter'
    if "delimiter" in options:
        options["sep"] = options.pop("delimiter")

    return pd.read_csv(filename, encoding=encoding, **options), header


def read_to_polars(
    filename: Path | str,
    marker: str = "---",
    encoding: Literal["utf8", "utf8-lossy"] = "utf8",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
    eager: bool = False,
) -> tuple[LazyFrame | PolarsDataFrame, dict[str, Any]]:
    """Read a CSVY file into dict with the header and a Polars LazyFrame with the data.

    This uses the `scan_csv` method from Polars to read the data. This returns a polars
    LazyFrame, which means the data is not loaded into memory until it is needed. To
    load the data into memory, set the `eager` parameter to `True`.

    Possible 'skip_rows' and 'comment_prefix' argument provided in the 'csv_options'
    dictionary will be ignored.

    Args:
        filename:  Name of the file to read.
        marker: The marker characters that indicate the yaml header.
        encoding: The character encoding in the file to read.
        csv_options: Options to pass to pl.scan_csv.
        yaml_options: Options to pass to yaml.safe_load.
        eager: Whether to load the data into memory.

    Raises:
        ModuleNotFoundError: If polars is not found.
        ValueError: If an invalid character encoding is specified.

    Returns:
        Tuple containing: The polars LazyFrame and the header as a dictionary.

    """
    if encoding not in ("utf8", "utf8-lossy"):
        raise ValueError("Encoding must be either 'utf8' or 'utf8-lossy'")

    if LazyFrame is None:
        raise ModuleNotFoundError(
            "Module polars is not present. Install it to read data into DataFrame."
        )
    import polars as pl

    yaml_options = yaml_options if yaml_options is not None else {}
    header, nlines, comment = read_header(
        filename, marker=marker, encoding="utf-8", **yaml_options
    )

    # Merge CSV options with dialect information
    merged_options, header = merge_csv_options_with_dialect(header, csv_options)

    options = merged_options.copy()
    options["skip_rows"] = nlines
    options["comment_prefix"] = comment[0] if len(comment) >= 1 else None

    # Polars uses 'separator' instead of 'delimiter'
    if "delimiter" in options:
        options["separator"] = options.pop("delimiter")

    lf = pl.scan_csv(filename, encoding=encoding, **options)
    if eager:
        return lf.collect(), header
    return lf, header


def read_to_list(
    filename: Path | str,
    marker: str = "---",
    encoding: str = "utf-8",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
) -> tuple[list[list], dict[str, Any]]:
    """Read a CSVY file into a list with the header and a nested list with the data.

    Args:
        filename: Name of the file to read.
        marker: The marker characters that indicate the yaml header.
        encoding: The character encoding in the file to read.
        csv_options: Options to pass to csv.reader.
        yaml_options: Options to pass to yaml.safe_load.

    Raises:
        ModuleNotFoundError: If numpy is not found.

    Returns:
        Tuple containing: The nested list and the header as a dictionary.

    """
    yaml_options = yaml_options if yaml_options is not None else {}
    header, nlines, _ = read_header(
        filename, marker=marker, encoding=encoding, **yaml_options
    )

    # Merge CSV options with dialect information
    options, header = merge_csv_options_with_dialect(header, csv_options)

    data = []
    with open(filename, encoding=encoding, newline="") as csvfile:
        csvreader = csv.reader(csvfile, **options)

        for _ in range(nlines):
            next(csvreader)

        for row in csvreader:
            data.append(row)

    return data, header


def read_to_dict(
    filename: Path | str,
    marker: str = "---",
    encoding: str = "utf-8",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
    *,
    column_names: list[Any] | int | None = None,
    fillvalue: Any = None,
) -> tuple[dict[str, list[Any]], dict[str, Any]]:
    """Read a CSVY file into a dictionary with the header and the data as dictionaries.

    Internally, it calls `read_to_list` and then transforms the data into a dictionary.

    Args:
        filename: Name of the file to read.
        marker: The marker characters that indicate the yaml header.
        encoding: The character encoding in the file to read.
        csv_options: Options to pass to csv.reader.
        yaml_options: Options to pass to yaml.safe_load.
        column_names: Either a list with the column names, the row number containing the
            column names or None. If None (the default) an automatic column name
            ('col_0', 'col_1', ...) will be used.
        fillvalue: Value to use for missing data in the columns.

    Returns:
        Tuple containing: The data and the header both as a dictionaries.

    """
    data, header = read_to_list(filename, marker, encoding, csv_options, yaml_options)

    longest_row = len(max(data, key=len))
    if column_names is None:
        column_names = [f"col_{i}" for i in range(longest_row)]
    else:
        if isinstance(column_names, int):
            column_names = data.pop(column_names)

        if len(column_names) != longest_row:
            raise ValueError(
                "The number of column names must be exactly the length of the longest "
                f"row ({len({column_names})} != {longest_row})."
            )

    columns = list(map(list, zip_longest(*data, fillvalue=fillvalue)))
    return dict(zip(column_names, columns)), header
