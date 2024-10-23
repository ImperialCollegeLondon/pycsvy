"""A collection of functions for writing CSVY files."""

from __future__ import annotations

import csv
import logging
from collections.abc import Callable, Iterable
from io import TextIOBase
from pathlib import Path
from typing import Any

import yaml

KNOWN_WRITERS: list[Callable[[Path | str, Any, str], bool]] = []


def register_writer(fun: Callable[[Path | str, Any, str], bool]) -> Callable:
    """Register a file writer.

    Args:
        fun (Callable): The writer function.

    Returns:
        Callable: the writer function.
    """
    if fun not in KNOWN_WRITERS:
        KNOWN_WRITERS.append(fun)
    return fun


def write(
    filename: Path | str,
    data: Any,
    header: dict[str, Any],
    comment: str = "",
    csv_options: dict[str, Any] | None = None,
    yaml_options: dict[str, Any] | None = None,
) -> None:
    """Writes the data and header in a CSV file, formating the header as yaml.

    Args:
        filename: Name of the file to save the information into. If it exists, it will
            be overwritten.
        data: The data to add to the file.
        header: Dictionary with the header information to save.
        comment: String to use to mark the header lines as comments.
        csv_options: Arguments to pass to the CSV writer, being this `savetxt`, panda's
            `to_csv` or something else. Mind that any argument related to the character
            to indicate a comment or header line will be ignored.
        yaml_options: Arguments to pass to the 'yaml.safe_dump' function to control
            writing the header.
    """
    csv_options = csv_options if csv_options is not None else {}
    yaml_options = yaml_options if yaml_options is not None else {}

    write_header(filename, header, comment, **yaml_options)
    write_data(filename, data, comment, **csv_options)


class Writer:
    """A class for writing the CSV data to a file incrementally.

    Under the hood, this class uses csv.writer to write lines of data to CSV files.
    """

    def __init__(
        self,
        filename: Path | str,
        header: dict[str, Any],
        comment: str = "",
        csv_options: dict[str, Any] | None = None,
        yaml_options: dict[str, Any] | None = None,
        line_buffering: bool = False,
    ) -> None:
        """Create a new Writer.

        Args:
            filename: Path to file. If it exists it will be overwritten.
            header: Dictionary with the header information to save.
            comment: String to use to mark the header lines as comments.
            csv_options: Arguments to pass to csv.writer()
            yaml_options: Arguments to pass to the 'yaml.safe_dump' function to control
                writing the header.
            line_buffering: Line buffering instead of chunk buffering (default False).
        """
        if not csv_options:
            csv_options = {}
        if not yaml_options:
            yaml_options = {}

        # Line buffering: 1 and default chunk buffering: -1
        buffering = 1 if line_buffering else -1

        # Newline must be "" as per csv.writer's documentation
        self._file = Path(filename).open(
            "w", encoding="utf-8", newline="", buffering=buffering
        )
        write_header(self._file, header, comment, **yaml_options)

        self._writer = csv.writer(self._file, **csv_options)

    def __enter__(self) -> Writer:
        """Enter the context manager."""
        return self

    def __exit__(self, *_: Any) -> None:
        """Exit the context manager."""
        self._file.close()

    def close(self) -> None:
        """Close the underlying file handle."""
        self._file.close()

    def writerow(self, row: Iterable[Any]) -> None:
        """Write a single row of data to the CSV file."""
        self._writer.writerow(row)

    def writerows(self, rows: Iterable[Iterable[Any]]) -> None:
        """Write multiple rows of data to the CSV file."""
        self._writer.writerows(rows)


def write_header(
    file: Path | str | TextIOBase,
    header: dict[str, Any],
    comment: str = "",
    **kwargs: Any,
) -> None:
    """Writes the header dictionary into the file with lines starting with comment.

    Args:
        file: File handle or path to file. Will be overwritten if it exists.
        header: Dictionary with the header information to save.
        comment: String to use to mark the header lines as comments.
        **kwargs: Arguments to pass to 'yaml.safe_dump'. If "sort_keys" is not one of
            arguments, it will be set to sort_keys=False.
    """
    if not isinstance(file, TextIOBase):
        with Path(file).open("w", encoding="utf-8") as f:
            write_header(f, header, comment, **kwargs)
            return

    if "sort_keys" not in kwargs:
        kwargs["sort_keys"] = False

    stream = yaml.safe_dump(header, **kwargs)
    stream = "\n".join([f"{comment}" + line for line in stream.split("\n")])
    marker = f"{comment}---\n"
    stream = marker + stream + "---\n"
    file.write(stream)  # type: ignore


def write_data(
    filename: Path | str, data: Any, comment: str = "", **kwargs: Any
) -> None:
    """Writes the tabular data to the chosen file, adding it after the header.

    Args:
        filename: Name of the file to save the data into. The data will be added to the
            end of the file.
        data: The data to add to the file. Depending on its type, a different method
            will be used to save the data to disk. The fallback will be the built in CSV
            package. If it is a numpy array, the `savetxt` will be used, while if it is
            a pandas Dataframe, the `to_csv` method will be used.
        comment: String to use to mark the header lines as comments.
        **kwargs: Arguments to be passed to the underlaying saving method.
    """
    for fun in KNOWN_WRITERS:
        if fun(filename, data, comment, **kwargs):
            return

    write_csv(filename, data, comment, **kwargs)


@register_writer
def write_numpy(
    filename: Path | str, data: Any, comment: str = "", **kwargs: Any
) -> bool:
    """Writes the numpy array to the chosen file, adding it after the header.

    Args:
        filename: Name of the file to save the data into. The data will be added to the
            end of the file.
        data: The data. If it is a numpy array, it will be saved, otherwise nothing is
            done.
        comment: String to use to mark the header lines as comments.
        **kwargs: Arguments to be passed to the underlaying saving method.

    Return:
        True if the writer worked, False otherwise.
    """
    try:
        import numpy as np

        kwargs["comments"] = comment
        if isinstance(data, np.ndarray):
            with open(filename, "a", encoding="utf-8") as f:
                np.savetxt(f, data, **kwargs)

            return True

    except ModuleNotFoundError:
        logging.getLogger().debug("Numpy is not installed, so not using 'savetxt'.")

    return False


@register_writer
def write_pandas(
    filename: Path | str, data: Any, comment: str = "", **kwargs: Any
) -> bool:
    """Writes the pandas dataframe to the chosen file, adding it after the header.

    Args:
        filename: Name of the file to save the data into. The data will be added to the
            end of the file.
        data: The data. If it is a pandas dataframe, it will be saved, otherwise nothing
            is done.
        comment: String to use to mark the header lines as comments.
        **kwargs: Arguments to be passed to the underlaying saving method.

    Returns:
        True if the writer worked, False otherwise.
    """
    try:
        import pandas as pd

        if isinstance(data, pd.DataFrame):
            with open(filename, "a", encoding="utf-8", newline="") as f:
                data.to_csv(f, **kwargs)

            return True

    except ModuleNotFoundError:
        logging.getLogger().debug("Pandas is not installed, so not using 'to_csv'.")

    return False


@register_writer
def write_polars(
    filename: Path | str, data: Any, comment: str = "", **kwargs: Any
) -> bool:
    """Writes the polars dataframe to the chosen file, adding it after the header.

    Args:
        filename: Name of the file to save the data into. The data will be added to the
            end of the file.
        data: The data. If it is a polars DataFrame or LazyFrame, it will be saved,
            otherwise nothing is done.
        comment: String to use to mark the header lines as comments.
        **kwargs: Arguments to be passed to the underlaying saving method.

    Returns:
        True if the writer worked, False otherwise.
    """
    try:
        import polars as pl

        if isinstance(data, pl.LazyFrame):
            # Streaming mode (saving with `LazyFrame.sink_csv`) is unstable, so we
            # collect the data into a DataFrame first
            data = data.collect()
        if isinstance(data, pl.DataFrame):
            with open(filename, "a", encoding="utf-8", newline="") as f:
                data.write_csv(f, **kwargs)

            return True

    except ModuleNotFoundError:
        logging.getLogger().debug("Polars is not installed, so not using 'write_csv'.")

    return False


def write_csv(
    filename: Path | str, data: Any, comment: str = "", **kwargs: Any
) -> bool:
    """Writes the tabular to the chosen file, adding it after the header.

    Args:
        filename: Name of the file to save the data into. The data will be added to the
            end of the file.
        data: The data. Can have anything that counts as a sequence. Each component of
            the sequence will be saved in a different row.
        comment: String to use to mark the header lines as comments.
        **kwargs: Arguments to be passed to the underlaying saving method.

    Returns:
        True if the writer worked, False otherwise.
    """
    with open(filename, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, **kwargs)
        for row in data:
            writer.writerow(row)

    return True
