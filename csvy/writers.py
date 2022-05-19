import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Union

import yaml

KNOWN_WRITERS: List[Callable[[Union[Path, str], Any], bool]] = []
"""Writers known"""


def register_writer(fun: Callable[[Union[Path, str], Any], bool]) -> Callable:
    if fun not in KNOWN_WRITERS:
        KNOWN_WRITERS.append(fun)
    return fun


def write_header(
    filename: Union[Path, str], header: Dict[str, Any], comment: str = ""
) -> None:
    """Writes the header dictionary into the file with lines starting with comment.

    Args:
        filename (Union[Path, str]): Name of the file to save the header into. If it
        exists, it will be overwritten.
        header (Dict[str, Any]): Dictionary with the header information to save.
        comment (str): String to use to mark the header lines as comments.
    """
    stream = yaml.safe_dump(header)
    stream = "\n".join([f"{comment}" + line for line in stream.split("\n")])
    marker = f"{comment}---\n"
    stream = marker + stream + "---\n"
    with Path(filename).open("w") as f:
        f.write(stream)


def write_data(filename: Union[Path, str], data: Any, **kwargs) -> None:
    """Writes the tabular data to the chosen file, adding it after the header.

    Args:
        filename (Union[Path, str]): Name of the file to save the data into. The data
        will be added to the end of the file.
        data (Any): The data to add to the file. Depending on its type, a different
        method will be used to save the data to disk. The fallback will be the built
        in CSV package. If it is a numpy array, the `savetxt` will be used, while if it
        is a pandas Dataframe, the `to_csv` method will be used.
        kwargs: Arguments to be passed to the underlaying saving method.
    """
    for fun in KNOWN_WRITERS:
        if fun(filename, data, **kwargs):
            return

    write_csv(filename, data, **kwargs)


@register_writer
def write_numpy(filename: Union[Path, str], data: Any, **kwargs) -> bool:
    """Writes the numpy array to the chosen file, adding it after the header.

    Args:
        filename (Union[Path, str]): Name of the file to save the data into. The data
        will be added to the end of the file.
        data (Any): The data. If it is a numpy array, it will be saved, otherwise
        nothing is done.
        kwargs: Arguments to be passed to the underlaying saving method.

    Return:
        (bool) True if the writer worked, false otherwise.
    """
    try:
        import numpy as np

        if isinstance(data, np.ndarray):
            with open(filename, "a") as f:
                np.savetxt(f, data, **kwargs)

            return True

    except ModuleNotFoundError:
        logging.getLogger().debug("Numpy is not installed, so not using 'savetxt'.")

    return False


@register_writer
def write_pandas(filename: Union[Path, str], data: Any, **kwargs) -> bool:
    """Writes the pandas dataframe to the chosen file, adding it after the header.

    Args:
        filename (Union[Path, str]): Name of the file to save the data into. The data
        will be added to the end of the file.
        data (Any): The data. If it is a pandas dataframe, it will be saved, otherwise
        nothing is done.
        kwargs: Arguments to be passed to the underlaying saving method.

    Return:
        (bool) True if the writer worked, false otherwise.
    """
    try:
        import pandas as pd

        if isinstance(data, pd.DataFrame):
            with open(filename, "a") as f:
                data.to_csv(f, **kwargs)

            return True

    except ModuleNotFoundError:
        logging.getLogger().debug("Pandas is not installed, so not using 'to_csv'.")

    return False


def write_csv(filename: Union[Path, str], data: Any, **kwargs) -> bool:
    """Writes the tabular to the chosen file, adding it after the header.

    Args:
        filename (Union[Path, str]): Name of the file to save the data into. The data
        will be added to the end of the file.
        data (Any): The data. Can have anything that counts as a sequence. Each
        component of the sequence will be saved in a different row.
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
