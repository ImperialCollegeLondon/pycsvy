"""Module that contains validators for the CSVY file format."""

import csv
from typing import Any, Callable, Optional, TypeVar

from pydantic import BaseModel, Field

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


def validate_read(header: dict[str, Any]) -> dict[str, Any]:
    """Run the validators on the header in a read operation.

    This function runs the validators on the header. It uses the keys of the header to
    find the validators in the registry and runs them on the corresponding values.

    Args:
        header: The header of the CSVY file.

    Returns:
        The validated header.

    """
    validated_header = {}
    for key, value in header.items():
        if key in VALIDATORS_REGISTRY:
            validator = VALIDATORS_REGISTRY[key]
            validated_header[key] = validator(**value)
        else:
            validated_header[key] = value
    return validated_header


def validate_write(header: dict[str, Any]) -> dict[str, Any]:
    """Use the validators to create the header in a write operation.

    Transforms the header with validators to a header with dictionaries that can be
    saved as yaml. It is the reversed operation of validate_read, so calling
    validate_write(validate_read(header)) should return the original header.

    Args:
        header: Dictionary to be saved as the header of the CSVY file.

    Returns:
        The validated header.

    """
    validated_header = {}
    for key, value in header.items():
        validated_header[key] = (
            value.model_dump() if isinstance(value, BaseModel) else value
        )
    return validated_header


# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar("T", bound="CSVDialectValidator")


@register_validator("csv_dialect")
class CSVDialectValidator(BaseModel):
    r"""Implements a validator for CSV Dialects.

    This class is used to validate the CSV Dialects in the CSVY file. It is based on the
    `csv.Dialect` class from the Python Standard Library. It does not include the
    'quoting' attribute, as it is not serializable as JSON or easy to understand by
    other tools, but rather a python specific thing.

    Attributes:
        delimiter: A one-character string used to separate fields.
        doublequote: Controls how instances of quotechar appearing inside a field should
            themselves be quoted. When True, the character is doubled. When False, the
            escapechar is used as a prefix to the quotechar. It defaults to True.
        escapechar: A one-character string used by the writer to escape the delimiter.
            It defaults to None.
        lineterminator: The string used to terminate lines produced by the writer. It
            defaults to '\\r\\n'.
        quotechar: A one-character string used to quote fields containing special
            characters, such as the delimiter or quotechar, or which contain new-line
            characters. It defaults to '"'.
        skipinitialspace: When True, whitespace immediately following the delimiter is
            ignored. It defaults to False.

    """

    delimiter: str = Field(default=",")
    doublequote: bool = Field(default=True)
    escapechar: Optional[str] = Field(default=None)
    lineterminator: str = Field(default="\r\n")
    quotechar: str = Field(default='"')
    skipinitialspace: bool = Field(default=False)

    def to_dialect(self) -> csv.Dialect:
        """Convert the validator to a custom csv.Dialect object.

        This method converts the validator to a custom csv.Dialect object that can be
        used to read or write CSV files with the specified dialect.

        For 'quoting', the default value is used, as it is not serializable.

        Returns:
            A custom csv.Dialect object with the specified attributes.

        """
        dialect = type(
            "CustomDialect",
            (csv.Dialect,),
            {
                "delimiter": self.delimiter,
                "doublequote": self.doublequote,
                "escapechar": self.escapechar,
                "lineterminator": self.lineterminator,
                "quotechar": self.quotechar,
                "skipinitialspace": self.skipinitialspace,
                "quoting": csv.QUOTE_MINIMAL,  # This is not serializable.
            },
        )
        return dialect()

    @classmethod
    def excel(cls: type[T]) -> T:
        """Return a validator for the Excel CSV Dialect.

        This method returns a validator for the Excel CSV Dialect, which is a common
        dialect used in Excel files.

        Returns:
            A validator for the Excel CSV Dialect.

        """
        excel = csv.excel()
        return cls(
            delimiter=excel.delimiter,
            doublequote=excel.doublequote,
            escapechar=excel.escapechar,
            lineterminator=excel.lineterminator,
            quotechar=excel.quotechar,
            skipinitialspace=excel.skipinitialspace,
        )

    @classmethod
    def excel_tab(cls: type[T]) -> T:
        """Return a validator for the Excel Tab CSV Dialect.

        This method returns a validator for the Excel Tab CSV Dialect, which is a common
        dialect used in Excel files with tab delimiters.

        `excel` has not parameter `strict` so that one is ignored.

        Returns:
            A validator for the Excel Tab CSV Dialect.

        """
        excel_tab = csv.excel_tab()
        return cls(
            delimiter=excel_tab.delimiter,
            doublequote=excel_tab.doublequote,
            escapechar=excel_tab.escapechar,
            lineterminator=excel_tab.lineterminator,
            quotechar=excel_tab.quotechar,
            skipinitialspace=excel_tab.skipinitialspace,
        )

    @classmethod
    def unix_dialect(cls: type[T]) -> T:
        """Return a validator for the Unix CSV Dialect.

        This method returns a validator for the Unix CSV Dialect, which is a common
        dialect used in Unix files.

        Returns:
            A validator for the Unix CSV Dialect.

        """
        unix = csv.unix_dialect()
        return cls(
            delimiter=unix.delimiter,
            doublequote=unix.doublequote,
            escapechar=unix.escapechar,
            lineterminator=unix.lineterminator,
            quotechar=unix.quotechar,
            skipinitialspace=unix.skipinitialspace,
        )
