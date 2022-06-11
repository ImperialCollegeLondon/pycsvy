import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

try:
    from numpy.typing import NDArray
except ModuleNotFoundError:
    NDArray = NotImplemented  # type: ignore
    logging.getLogger().debug(
        "Numpy is not installed. Reading into an array will not work."
    )

try:
    from pandas import DataFrame
except ModuleNotFoundError:
    DataFrame = NotImplemented  # type: ignore
    logging.getLogger().debug(
        "Pandas is not installed. Reading into a DataFrame will not work."
    )


def get_comment(line: str, marker: str = "---") -> str:
    """Retrieves the comment character used in the header.

    Given that we know the header limiting markers are '---' it is possible to
    automatically find out the comment character by simply retrieving what is
    before the first occurrence of the marker. So, if we find '# ---', then we
    know that the comment characters are '# '.

    This will save the user to having to check the file before reading it.

    Args:
        line (str): Line of text, typically the first one of the file.
        marker (str): The marker characters that indicate the yaml header.
        Defaults to "---".

    Returns:
        str: The comment character found.
    """
    if marker not in line:
        raise ValueError(f"Yaml header marker '{marker}' not found in line '{line}'.")
    else:
        return "" if line.startswith(marker) else line.split(marker)[0]


def read_header(
    filename: Union[Path, str], marker: str = "---", **kwargs
) -> Tuple[Dict[str, Any], int, str]:
    """Read the yaml-formatted header from a file.

    Args:
        filename (Union[Path, str]): Name of the file to read the header from.
        marker (str): The marker characters that indicate the yaml header.
        Defaults to "---".
        kwargs: Arguments to pass to 'yaml.safe_load'.

    Returns:
        Tuple[Dict[str, Any], int, srt]: Tuple with a dictionary with the header
        information the number of header lines and the comment character.
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

    return yaml.safe_load("".join(header), **kwargs), nlines, comment


def read_to_array(
    filename: Union[Path, str],
    marker: str = "---",
    csv_options: Optional[Dict[str, Any]] = None,
    yaml_options: Optional[Dict[str, Any]] = None,
) -> Tuple[NDArray, Dict[str, Any]]:
    """Reads a CSVY file into dict with the header and array with the data.

    Args:
        filename (Union[Path, str]):  Name of the file to read.
        marker (str): The marker characters that indicate the yaml header.
        Defaults to "---".
        csv_options (Optional[Dict[str, Any]], optional): Options to pass to np.loadtxt.
        Defaults to None.
        yaml_options (Optional[Dict[str, Any]], optional): Options to pass to
        yaml.safe_load. Defaults to None.

    Raises:
        ModuleNotFoundError: If numpy is not found.

    Returns:
        Tuple[NDArray, Dict[str, Any]]: The numpy array and the header as a dictionary.
    """
    if NDArray is NotImplemented:
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
    filename: Union[Path, str],
    marker: str = "---",
    csv_options: Optional[Dict[str, Any]] = None,
    yaml_options: Optional[Dict[str, Any]] = None,
) -> Tuple[DataFrame, Dict[str, Any]]:
    """Reads a CSVY file into dict with the header and a DataFrame with the data.

    Possible 'skiprows' and 'comment' argument provided in the 'csv_options' dictionary
    will be ignored.

    Args:
        filename (Union[Path, str]):  Name of the file to read.
        marker (str): The marker characters that indicate the yaml header.
        Defaults to "---".
        csv_options (Optional[Dict[str, Any]], optional): Options to pass to
        pd.read_csv. Defaults to None.
        yaml_options (Optional[Dict[str, Any]], optional): Options to pass to
        yaml.safe_load. Defaults to None.

    Raises:
        ModuleNotFoundError: If pandas is not found.

    Returns:
        Tuple[DataFrame, Dict[str, Any]]: The pandas DataFrame and the header as a
        dictionary.
    """
    if DataFrame is NotImplemented:
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


def read_to_list(
    filename: Union[Path, str],
    marker: str = "---",
    csv_options: Optional[Dict[str, Any]] = None,
    yaml_options: Optional[Dict[str, Any]] = None,
) -> Tuple[List[List], Dict[str, Any]]:
    """Reads a CSVY file into a list with the header and a nested list with the data.

    Args:
        filename (Union[Path, str]): Name of the file to read.
        marker (str): The marker characters that indicate the yaml header.
        Defaults to "---".
        csv_options (Optional[Dict[str, Any]], optional): Options to pass to csv.reader.
        Defaults to None.
        yaml_options (Optional[Dict[str, Any]], optional): Options to pass to
        yaml.safe_load. Defaults to None.

    Raises:
        ModuleNotFoundError: If numpy is not found.

    Returns:
        Tuple[List[List], Dict[str, Any]]: The numpy array and the header as a
        dictionary.
    """
    import csv

    yaml_options = yaml_options if yaml_options is not None else {}
    header, nlines, _ = read_header(filename, marker=marker, **yaml_options)

    options = csv_options.copy() if csv_options is not None else {}

    data = []
    with open(filename, "r", newline="") as csvfile:
        csvreader = csv.reader(csvfile, **options)

        for _ in range(nlines):
            next(csvreader)

        for row in csvreader:
            data.append(row)

    return data, header
