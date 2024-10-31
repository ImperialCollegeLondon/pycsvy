"""Python reader/writer for CSV files with YAML header information."""

__version__ = "0.2.2"

from .readers import (  # noqa: F401
    read_header,
    read_into_dict,
    read_metadata,
    read_to_array,
    read_to_dataframe,
    read_to_polars,
)
from .writers import Writer, write, write_header  # noqa: F401