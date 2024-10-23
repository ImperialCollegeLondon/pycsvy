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


def test_register_validator():
    """Test that we can register a new validator."""
    from pydantic import BaseModel

    from csvy.validators import VALIDATORS_REGISTRY, register_validator

    @register_validator("my_validator")
    class MyValidator(BaseModel):
        pass

    assert VALIDATORS_REGISTRY["my_validator"] == MyValidator

    # We clean up the registry to avoid side effects in other tests.
    VALIDATORS_REGISTRY.pop("my_validator")


def test_register_validator_duplicate():
    """Test that we cannot register a validator with the same name."""
    from pydantic import BaseModel

    from csvy.validators import VALIDATORS_REGISTRY, register_validator

    # With overwriting, we should not raise an error.
    name = "my_validator"

    @register_validator(name)
    class MyValidator(BaseModel):
        pass

    # Without overwriting, we should raise an error.
    with pytest.raises(ValueError):

        @register_validator(name)
        class MyOverwritingValidator(BaseModel):
            pass

    # With overwriting, we should not raise an error,
    # and the validator should be overwritten.
    @register_validator(name, overwrite=True)
    class MyOverwritingValidator(BaseModel):
        pass

    assert VALIDATORS_REGISTRY[name] == MyOverwritingValidator


def test_register_validator_not_base_model():
    """Test that we cannot register a validator that is not a BaseModel."""
    from csvy.validators import register_validator

    with pytest.raises(TypeError):

        @register_validator("not_base_model")
        class NotBaseModel:
            pass


def test_run_validators_in_read():
    """Test that we can run validators on the header."""
    from pydantic import BaseModel, PositiveInt

    from csvy.validators import register_validator, validate_read

    @register_validator("my_validator")
    class MyValidator(BaseModel):
        value: PositiveInt

    header = {"author": "Gandalf", "my_validator": {"value": 42}}
    validated_header = validate_read(header)

    assert isinstance(validated_header["my_validator"], MyValidator)
    assert validated_header["my_validator"].value == 42
    assert validated_header["author"] == header["author"]
