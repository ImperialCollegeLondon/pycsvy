from pathlib import Path
from typing import Any, Dict, Union

import yaml


def load_header(filename: Union[Path, str], comment: str = "") -> Dict[str, Any]:
    """Loads the yaml-formatted header from a file.

    Args:
        filename (Union[Path, str]): Name of the file to save the header into. If it
        exists, it will be overwritten.
        comment (str): String that marks the header lines as comments.

    Returns:
        Dict[str, Any]: Dictionary with the header information.
    """
    header = []
    markers = 0
    with Path(filename).open("r") as f:
        for line in f:
            if line.startswith(f"{comment}---\n"):
                markers += 1
                if markers == 2:
                    break
            line = line.lstrip(comment)
            header.append(line)

    return yaml.safe_load("".join(header))
