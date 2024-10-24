"""A collection of functions for parsing CSVY files."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from itertools import zip_longest
from pathlib import Path
from typing import Any

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

from .validators import validate_read


def get_comment(line: str, marker: str = "---") -> str:
    """Retrieves the comment character used in the header.

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


def read_header(
    filename: Path | str, marker: str = "---", **kwargs: Any
) -> tuple[dict[str, Any], int, str]:
    """Read the yaml-formatted header from a file.

    Args:
        filename: Name of the file to read the header from.
        marker: The marker characters that indicate the yaml header.
        **kwargs: Arguments to pass to 'yaml.safe_load'.

    Returns:
        Tuple containing: a dictionary with the header information, the number of header
            lines, and the comment character.
    """
    header = []
    markers = 0
    nlines = 0
    comment = ""
    with Path(filename).open("r") as f:
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

    return validate_read(yaml.safe_load("".join(header), **kwargs)), nlines, comment


def read_metadata(
    filename: Path | str, marker: str = "---", **kwargs: Any
) -> dict[str, Any]:
    """Read the yaml-formatted metadata from a file.

    Args:
        filename: Name of the file to read the header from.
        marker: The marker characters that indicate the yaml header.
        **kwargs: Arguments to pass to 'yaml.safe_load'.

    Returns:
        The metadata stored in the header.
    """
    return read_header(filename, marker, **kwargs)[0]


def read_to_array(
    filename: Path | str,
    marker: str = "---",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
) -> tuple[NDArray, dict[str, Any]]:
    """Reads a CSVY file into dict with the header and array with the data.

    Args:
        filename:  Name of the file to read.
        marker: The marker characters that indicate the yaml header.
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
    header, nlines, comment = read_header(filename, marker=marker, **yaml_options)

    options = csv_options.copy() if csv_options is not None else {}
    options["skiprows"] = nlines + options.get("skiprows", 0)
    options["comments"] = comment[0] if len(comment) >= 1 else "#"
    return np.loadtxt(filename, **options), header


def read_to_dataframe(
    filename: Path | str,
    marker: str = "---",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
) -> tuple[DataFrame, dict[str, Any]]:
    """Reads a CSVY file into dict with the header and a DataFrame with the data.

    Possible 'skiprows' and 'comment' argument provided in the 'csv_options' dictionary
    will be ignored.

    Args:
        filename:  Name of the file to read.
        marker: The marker characters that indicate the yaml header.
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
    header, nlines, comment = read_header(filename, marker=marker, **yaml_options)

    options = csv_options.copy() if csv_options is not None else {}
    options["skiprows"] = nlines
    options["comment"] = comment[0] if len(comment) >= 1 else None
    return pd.read_csv(filename, **options), header


def read_to_polars(
    filename: Path | str,
    marker: str = "---",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
    eager: bool = False,
) -> tuple[LazyFrame | PolarsDataFrame, dict[str, Any]]:
    """Reads a CSVY file into dict with the header and a Polars LazyFrame with the data.

    This uses the `scan_csv` method from Polars to read the data. This returns a polars
    LazyFrame, which means the data is not loaded into memory until it is needed. To
    load the data into memory, set the `eager` parameter to `True`.

    Possible 'skip_rows' and 'comment_prefix' argument provided in the 'csv_options'
    dictionary will be ignored.

    Args:
        filename:  Name of the file to read.
        marker: The marker characters that indicate the yaml header.
        csv_options: Options to pass to pl.scan_csv.
        yaml_options: Options to pass to yaml.safe_load.
        eager: Whether to load the data into memory.

    Raises:
        ModuleNotFoundError: If polars is not found.

    Returns:
        Tuple containing: The polars LazyFrame and the header as a dictionary.
    """
    if LazyFrame is None:
        raise ModuleNotFoundError(
            "Module polars is not present. Install it to read data into DataFrame."
        )
    import polars as pl

    yaml_options = yaml_options if yaml_options is not None else {}
    header, nlines, comment = read_header(filename, marker=marker, **yaml_options)

    options = csv_options.copy() if csv_options is not None else {}
    options["skip_rows"] = nlines
    options["comment_prefix"] = comment[0] if len(comment) >= 1 else None

    lf = pl.scan_csv(filename, **options)
    if eager:
        return lf.collect(), header
    return lf, header


def read_to_list(
    filename: Path | str,
    marker: str = "---",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
) -> tuple[list[list], dict[str, Any]]:
    """Reads a CSVY file into a list with the header and a nested list with the data.

    Args:
        filename: Name of the file to read.
        marker: The marker characters that indicate the yaml header.
        csv_options: Options to pass to csv.reader.
        yaml_options: Options to pass to yaml.safe_load.

    Raises:
        ModuleNotFoundError: If numpy is not found.

    Returns:
        Tuple containing: The nested list and the header as a dictionary.
    """
    import csv

    yaml_options = yaml_options if yaml_options is not None else {}
    header, nlines, _ = read_header(filename, marker=marker, **yaml_options)

    options = csv_options.copy() if csv_options is not None else {}

    data = []
    with open(filename, newline="") as csvfile:
        csvreader = csv.reader(csvfile, **options)

        for _ in range(nlines):
            next(csvreader)

        for row in csvreader:
            data.append(row)

    return data, header


class ReaderBase(ABC):
    """Base class for CSVY readers.

    This class is meant to be subclassed by other classes that implement the read_data
    method. It provides a common interface for reading CSVY files.
    """

    def __init__(self, filename: Path | str, marker: str = "---"):
        """Initializes the ReaderBase object.

        Args:
            filename: Name of the file to read.
            marker: The marker characters that indicate the yaml header.
        """
        self._filename: Path | str = filename
        self._marker: str = marker
        self._nlines: int | None = None
        self._comment: str | None = None
        self._header: dict[str, Any] | None = None

    def read(
        self, csv_options: dict[str, Any], yaml_options: dict[str, Any]
    ) -> tuple[Any, dict[str, Any]]:
        """Reads the file and returns the data.

        Args:
            csv_options: Options to pass to the read_data method.
            yaml_options: Options to pass to the read_header method.

        Returns:
            Tuple containing: The data and the header.
        """
        header = self._header or self.read_header(**yaml_options)
        data = self.read_data(**csv_options)
        return data, header

    def read_header(self, **kwargs) -> dict[str, Any]:
        """Reads the header from the file.

        Args:
            **kwargs: Arguments to pass to the read_header method.

        Returns:
            The header as a dictionary.
        """
        self._header, self._nlines, self._comment = read_header(
            self._filename, self._marker, **kwargs
        )
        return self._header

    @abstractmethod
    def read_data(self, **kwargs) -> Any:
        """Reads the data from the file."""


class ListReader(ReaderBase):
    """Reader class for reading CSVY files into a list of lists."""

    def read_data(
        self, in_columns: bool = False, fillvalue: str = "", **kwargs
    ) -> list[list]:
        """Reads the data from the file.

        Args:
            in_columns: Whether to read the data in columns.
            fillvalue: Value to use for missing data when reading in columns.
            **kwargs: Arguments to pass to the csv.reader function.

        Returns:
            The data as a list of lists.
        """
        import csv

        if self._nlines is None:
            self.read_header()

        data: list[list[str]] = []
        with open(self._filename, newline="") as csvfile:
            csvreader = csv.reader(csvfile, **kwargs)

            for _ in range(self._nlines):
                next(csvreader)

            for row in csvreader:
                data.append(row)

        if in_columns:
            data = list(map(list, zip_longest(*data, fillvalue=fillvalue)))

        return data
