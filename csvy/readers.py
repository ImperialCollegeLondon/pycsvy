import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

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


def read_header(
    filename: Union[Path, str], comment: str = "", **kwargs
) -> Tuple[Dict[str, Any], int]:
    """Read the yaml-formatted header from a file.

    Args:
        filename (Union[Path, str]): Name of the file to read the header from.
        comment (str): String that marks the header lines as comments.
        kwargs: Arguments to pass to 'yaml.safe_load'.

    Returns:
        Tuple[Dict[str, Any], int]: Tuple with a dictionary with the header information
        and the number of header lines.
    """
    header = []
    markers = 0
    nlines = 0
    with Path(filename).open("r") as f:
        for line in f:
            nlines += 1
            if line.startswith(f"{comment}---\n"):
                markers += 1
                if markers == 2:
                    break
            line = line.lstrip(comment)
            header.append(line)

    return yaml.safe_load("".join(header), **kwargs), nlines


def read_to_array(
    filename: Union[Path, str],
    comment: str = "",
    csv_options: Optional[Dict[str, Any]] = None,
    yaml_options: Optional[Dict[str, Any]] = None,
) -> Tuple[NDArray, Dict[str, Any]]:
    """Reads a CSVY file into dict with the header and array with the data.

    Args:
        filename (Union[Path, str]): _description_
        comment (str, optional): _description_. Defaults to "".
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
    header, nlines = read_header(filename, comment, **yaml_options)

    options = csv_options.copy() if csv_options is not None else {}
    options["skiprows"] = nlines
    options["comments"] = comment
    return np.loadtxt(filename, **options), header


def read_to_dataframe(
    filename: Union[Path, str],
    comment: str = "",
    csv_options: Optional[Dict[str, Any]] = None,
    yaml_options: Optional[Dict[str, Any]] = None,
) -> Tuple[DataFrame, Dict[str, Any]]:
    """Reads a CSVY file into dict with the header and a DataFrame with the data.

    Possible 'skiprows' and 'comment' argument provided in the 'csv_options' dictionary
    will be ignored.

    Args:
        filename (Union[Path, str]): _description_
        comment (str, optional): _description_. Defaults to "".
        csv_options (Optional[Dict[str, Any]], optional): _description_. Defaults to
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
    header, nlines = read_header(filename, comment, **yaml_options)

    options = csv_options.copy() if csv_options is not None else {}
    options["skiprows"] = nlines
    options["comment"] = comment[0] if len(comment) >= 1 else None
    return pd.read_csv(filename, **options), header
