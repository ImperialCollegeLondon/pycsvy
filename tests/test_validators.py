"""Tests for the validators module."""

import pytest


@pytest.mark.parametrize("shortcut", ["excel", "excel_tab", "unix_dialect"])
def test_shortcut_dialects_roundtrip(shortcut):
    """Test that the shortcut dialects roundtrip to the actual dialects."""
    import csv

    from csvy.validators import CSVDialectValidator

    validator = getattr(CSVDialectValidator, shortcut)()
    dialect = validator.to_dialect()
    actual = getattr(csv, shortcut)()

    assert dialect.delimiter == actual.delimiter
    assert dialect.doublequote == actual.doublequote
    assert dialect.escapechar == actual.escapechar
    assert dialect.lineterminator == actual.lineterminator
    assert dialect.quotechar == actual.quotechar
    assert dialect.skipinitialspace == actual.skipinitialspace
