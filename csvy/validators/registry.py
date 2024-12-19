"""Registry of validators to run on the header."""

from typing import Callable

from pydantic import BaseModel

VALIDATORS_REGISTRY: dict[str, type[BaseModel]] = {}
"""Registry of validators to run on the header."""


def register_validator(
    name: str, overwrite: bool = False
) -> Callable[[type[BaseModel]], type[BaseModel]]:
    """Register a validator in the registry.

    This function is a decorator that registers a validator in the registry. The name
    of the validator is used as the key in the registry.

    Args:
        name: The name of the validator.
        overwrite: Whether to overwrite the validator if it already exists.

    Returns:
        The decorator function that registers the validator.

    """

    def decorator(cls: type[BaseModel]) -> type[BaseModel]:
        if not issubclass(cls, BaseModel):
            raise TypeError("Validators must be subclasses of pydantic.BaseModel.")

        if name in VALIDATORS_REGISTRY and not overwrite:
            raise ValueError(f"Validator with name '{name}' already exists.")

        VALIDATORS_REGISTRY[name] = cls
        return cls

    return decorator
