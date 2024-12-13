"""Fixtures for the test suite."""

import pytest


@pytest.fixture
def data_path():
    """Provide a data path fixture."""
    from pathlib import Path

    return Path(__file__).parent / "data.csv"


@pytest.fixture
def data_comment_path():
    """Provide a data comment path fixture."""
    from pathlib import Path

    return Path(__file__).parent / "data_comment.csv"


@pytest.fixture
def array_data_path():
    """Provide a data array path fixture."""
    from pathlib import Path

    return Path(__file__).parent / "array_data.csv"


@pytest.fixture
def validators_registry():
    """Provide a validators registry fixture."""
    from csvy.validators import VALIDATORS_REGISTRY

    backup = VALIDATORS_REGISTRY.copy()
    yield VALIDATORS_REGISTRY
    VALIDATORS_REGISTRY.clear()
    VALIDATORS_REGISTRY.update(backup)
