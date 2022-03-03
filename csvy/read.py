from typing import Union, Any, Dict
from pathlib import Path

import yaml


def load_header(filename: Union[Path, str]) -> Dict[str, Any]:
    """_summary_

    Args:
        filename (Union[Path, str]): _description_

    Returns:
        Dict[str, Any]: _description_
    """
    header = []
    markers = 0
    with Path(filename).open("r") as f:
        for line in f:
            if line.startswith("---") or line.startswith("# ---"):
                markers += 1
                if markers == 2:
                    break
                continue
            line = line[2:] if line[0] == "#" else line
            header.append(line)

    return yaml.safe_load("".join(header))
