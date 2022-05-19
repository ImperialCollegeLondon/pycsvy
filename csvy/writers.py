import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import yaml

KNOWN_WRITERS: List[Callable[[Union[Path, str], Any, str], bool]] = []


def register_writer(fun: Callable[[Union[Path, str], Any, str], bool]) -> Callable:
    if fun not in KNOWN_WRITERS:
        KNOWN_WRITERS.append(fun)
    return fun


def write(
    filename: Union[Path, str],
    data: Any,
    header: Dict[str, Any],
    comment: str = "",
    csv_options: Optional[Dict[str, Any]] = None,
    yaml_options: Optional[Dict[str, Any]] = None,
) -> None:
    """Writes the data and header in a CSV file, formating the header as yaml.

    Args:
        filename (Union[Path, str]): Name of the file to save the information into. If
        it exists, it will be overwritten.
        data (Any): The data to add to the file.
        header (Optional[Dict]): Dictionary with the header information to save.
        comment (str, optional): String to use to mark the header lines as comments.
        Defaults to "".
        csv_options (Optional[Dict], optional): Arguments to pass to the CSV writer,
        being this savetxt, panda's 'to_csv' or something else. Mind that any argument
        related to the character to indicate a comment or header line will be ignored.
        yaml_options (Optional[Dict], optional): Arguments to pass to the
        'yaml.safe_dump' function to control writing the header. Defaults to None.
    """
    csv_options = csv_options if csv_options is not None else {}
    yaml_options = yaml_options if yaml_options is not None else {}

    write_header(filename, header, comment, **yaml_options)
    write_data(filename, data, comment, **csv_options)


def write_header(
    filename: Union[Path, str], header: Dict[str, Any], comment: str = "", **kwargs
) -> None:
    """Writes the header dictionary into the file with lines starting with comment.

    Args:
        filename (Union[Path, str]): Name of the file to save the header into. If it
        exists, it will be overwritten.
        header (Dict[str, Any]): Dictionary with the header information to save.
        comment (str): String to use to mark the header lines as comments.
        kwargs: Arguments to pass to 'yaml.safe_dump'.
    """
    stream = yaml.safe_dump(header, **kwargs)
    stream = "\n".join([f"{comment}" + line for line in stream.split("\n")])
    marker = f"{comment}---\n"
    stream = marker + stream + "---\n"
    with Path(filename).open("w") as f:
        f.write(stream)


def write_data(
    filename: Union[Path, str], data: Any, comment: str = "", **kwargs
) -> None:
    """Writes the tabular data to the chosen file, adding it after the header.

    Args:
        filename (Union[Path, str]): Name of the file to save the data into. The data
        will be added to the end of the file.
        data (Any): The data to add to the file. Depending on its type, a different
        method will be used to save the data to disk. The fallback will be the built
        in CSV package. If it is a numpy array, the `savetxt` will be used, while if it
        is a pandas Dataframe, the `to_csv` method will be used.
        comment (str): String to use to mark the header lines as comments.
        kwargs: Arguments to be passed to the underlaying saving method.
    """
    for fun in KNOWN_WRITERS:
        if fun(filename, data, comment, **kwargs):
            return

    write_csv(filename, data, comment, **kwargs)


@register_writer
def write_numpy(
    filename: Union[Path, str], data: Any, comment: str = "", **kwargs
) -> bool:
    """Writes the numpy array to the chosen file, adding it after the header.

    Args:
        filename (Union[Path, str]): Name of the file to save the data into. The data
        will be added to the end of the file.
        data (Any): The data. If it is a numpy array, it will be saved, otherwise
        nothing is done.
        comment (str): String to use to mark the header lines as comments.
        kwargs: Arguments to be passed to the underlaying saving method.

    Return:
        (bool) True if the writer worked, false otherwise.
    """
    try:
        import numpy as np

        kwargs["comments"] = comment
        if isinstance(data, np.ndarray):
            with open(filename, "a") as f:
                np.savetxt(f, data, **kwargs)

            return True

    except ModuleNotFoundError:
        logging.getLogger().debug("Numpy is not installed, so not using 'savetxt'.")

    return False


@register_writer
def write_pandas(
    filename: Union[Path, str], data: Any, comment: str = "", **kwargs
) -> bool:
    """Writes the pandas dataframe to the chosen file, adding it after the header.

    Args:
        filename (Union[Path, str]): Name of the file to save the data into. The data
        will be added to the end of the file.
        data (Any): The data. If it is a pandas dataframe, it will be saved, otherwise
        nothing is done.
        comment (str): String to use to mark the header lines as comments.
        kwargs: Arguments to be passed to the underlaying saving method.

    Return:
        (bool) True if the writer worked, false otherwise.
    """
    try:
        import pandas as pd

        if isinstance(data, pd.DataFrame):
            with open(filename, "a", newline="") as f:
                data.to_csv(f, **kwargs)

            return True

    except ModuleNotFoundError:
        logging.getLogger().debug("Pandas is not installed, so not using 'to_csv'.")

    return False


def write_csv(
    filename: Union[Path, str], data: Any, comment: str = "", **kwargs
) -> bool:
    """Writes the tabular to the chosen file, adding it after the header.

    Args:
        filename (Union[Path, str]): Name of the file to save the data into. The data
        will be added to the end of the file.
        data (Any): The data. Can have anything that counts as a sequence. Each
        component of the sequence will be saved in a different row.
        comment (str): String to use to mark the header lines as comments.
        kwargs: Arguments to be passed to the underlaying saving method.

    Return:
        (bool) True if the writer worked, false otherwise.
    """
    import csv

    with open(filename, "a", newline="") as f:
        writer = csv.writer(f, **kwargs)
        for row in data:
            writer.writerow(row)

    return True
