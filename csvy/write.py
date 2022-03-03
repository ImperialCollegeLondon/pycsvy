from typing import Union, Any, Dict
from pathlib import Path

import yaml


def save_header(
    filename: Union[Path, str], header: Dict[str, Any], comment: str = ""
) -> Dict[str, Any]:
    """_summary_

    Args:
        filename (Union[Path, str]): _description_

    Returns:
        Dict[str, Any]: _description_
    """
    stream = yaml.safe_dump(header)
    if comment != "":
        stream = "\n".join([f"{comment} " + line for line in stream.split("\n")])

    marker = "---\n" if comment == "" else f"{comment} ---\n"
    stream = marker + stream + "---\n"
    with Path(filename).open("w") as f:
        f.write(stream)
