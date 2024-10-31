"""Tests for the csvy reader functions."""
import logging
import warnings

import pytest

from csvy.readers import read_into_dict

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

data_files = [
    'tests/data_comment.csv',
    'tests/array_data.csv',
    'tests/data.csv',
    'tests/data_read_into_dict.csvy'
]

@pytest.mark.parametrize("file_path", data_files)
def test_read_into_dict(file_path):
    """Test the read_into_dict function with multiple datasets."""
    data, metadata = read_into_dict(file_path)
    if not metadata:
        warnings.warn(f"Metadata is empty for file {file_path}", UserWarning)
    else:
        logger.debug("Metadata keys: %s", list(metadata.keys()))

    assert isinstance(data, dict), (
        f"Expected data to be a dict, but got {type(data)} "
        f"from file {file_path}"
    )
    assert isinstance(metadata, dict), (
        f"Expected metadata to be a dict, but got {type(metadata)} "
        f"from file {file_path}"
    )

    if metadata:
        assert len(metadata) > 0, (
            f"Metadata should have at least one key in file {file_path}"
        )
