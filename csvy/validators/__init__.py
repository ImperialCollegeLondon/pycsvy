"""Validators for the CSVY format."""

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

from .csv_dialect import CSVDialectValidator  # noqa: F401
from .registry import VALIDATORS_REGISTRY, register_validator  # noqa: F401
from .table_schema import SchemaValidator  # noqa: F401


def validate_header(header: dict[str, Any]) -> dict[str, Any]:
    """Run the validators on the header.

    This function runs the validators on the header. It uses the keys of the header to
    find the validators in the registry and runs them on the corresponding values. As
    a result, some values in the header may be replaced by the validated values in the
    form of Pydantic models.

    If the header is an already validated header, the Pydantic models within, if any,
    are dumped to dictionaries and re-validated, again. This accounts for the case where
    attributes of the Pydantic models are changed to invalid values.

    Args:
        header: The header of the CSVY file.

    Returns:
        The validated header.

    """
    validated_header: dict[str, Any] = {}
    for key, value in header.items():
        value_ = value.model_dump() if isinstance(value, BaseModel) else value
        if key in VALIDATORS_REGISTRY:
            if not isinstance(value_, Mapping):
                raise TypeError(
                    f"Value for '{key}' must be a mapping, not a '{type(value_)}'."
                )
            validator = VALIDATORS_REGISTRY[key]
            validated_header[key] = validator(**value_)
        else:
            validated_header[key] = value_
    return validated_header


def header_to_dict(header: dict[str, Any]) -> dict[str, Any]:
    """Transform the header into a serializable dictionary.

    Transforms the header with validators to a header with dictionaries that can be
    saved as yaml.

    Args:
        header: Dictionary to be saved as the header of the CSVY file.

    Returns:
        The validated header, as a serializable dictionary.

    """
    validated_header = {}
    for key, value in header.items():
        validated_header[key] = (
            value.model_dump() if isinstance(value, BaseModel) else value
        )
    return validated_header
