"""A collection of functions for parsing CSVY files."""
from __future__ import annotations

import csv
import logging
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
    import pandas as pd
    from pandas import DataFrame
except ModuleNotFoundError:
    DataFrame = None  # type: ignore
    logging.getLogger().debug(
        "Pandas is not installed. Reading into a pd.DataFrame will not work."
    )

try:
    import polars as pl
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
    """Retrieves the comment character used in the header."""
    if marker not in line:
        raise ValueError(f"Yaml header marker '{marker}' not found in line '{line}'.")
    return "" if line.startswith(marker) else line.split(marker)[0]


def read_header(
    filename: Path | str, marker: str = "---", **kwargs: Any
) -> tuple[dict[str, Any], int, str]:
    """Read the yaml-formatted header from a file."""
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
    """Read the yaml-formatted metadata from a file."""
    return read_header(filename, marker, **kwargs)[0]


def read_to_array(
    filename: Path | str,
    marker: str = "---",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
) -> tuple[NDArray, dict[str, Any]]:
    """Reads a CSVY file into dict with the header and array with the data."""
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
    """Reads a CSVY file into dict with the header and a DataFrame with the data."""
    if DataFrame is None:
        raise ModuleNotFoundError(
            "Module pandas is not present. Install it to read data into DataFrame."
        )

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
    """Reads a CSVY file into dict with the header and a Polars LazyFrame with the data."""
    if LazyFrame is None:
        raise ModuleNotFoundError(
            "Module polars is not present. Install it to read data into DataFrame."
        )

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
    """Reads a CSVY file into a list with the header and a nested list with the data."""
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


def read_into_dict(file_path: Path | str):
    """Read a CSVY file into a dictionary and metadata."""
    with open(file_path) as f:
        lines = f.readlines()

    metadata = {}
    data = []
    section = None

    for line in lines:
        line = line.strip()
        if line.startswith("# ---"):
            if section is None:
                section = "metadata"
            elif section == "metadata":
                section = "data"
            else:
                break
            continue  # Skip the marker line itself

        if section == "metadata":
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
        elif section == "data":
            if line:  # Ignore empty lines
                data.append(line.split(","))

    if data:
        data = list(map(list, zip_longest(*data, fillvalue="")))
        data_dict = {data[i][0]: data[i][1:] for i in range(len(data))}
        return data_dict, metadata
    return {}, {}