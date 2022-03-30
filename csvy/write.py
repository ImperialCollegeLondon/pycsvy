from typing import Union, Any, Dict
from pathlib import Path

import yaml


def save_header(
    filename: Union[Path, str], header: Dict[str, Any], comment: str = ""
) -> None:
    """Saves the header dictionary into the file with lines starting with comment.

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
