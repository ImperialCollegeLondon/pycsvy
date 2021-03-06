import pytest


@pytest.fixture
def data_path():
    from pathlib import Path

    return Path(__file__).parent / "data.csv"


@pytest.fixture
def data_comment_path():
    from pathlib import Path

    return Path(__file__).parent / "data_comment.csv"


@pytest.fixture
def array_data_path():
    from pathlib import Path

    return Path(__file__).parent / "array_data.csv"
