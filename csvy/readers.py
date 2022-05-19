from pathlib import Path
from typing import Any, Dict, Tuple, Union

import yaml


def read_header(
    filename: Union[Path, str], comment: str = ""
) -> Tuple[Dict[str, Any], int]:
    """Read the yaml-formatted header from a file.

    Args:
        filename (Union[Path, str]): Name of the file to read the header from.
        comment (str): String that marks the header lines as comments.

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

    return yaml.safe_load("".join(header)), nlines
