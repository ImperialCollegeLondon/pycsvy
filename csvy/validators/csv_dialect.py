"""CSV Dialect-related validation."""

from __future__ import annotations

import csv
from enum import Enum
from typing import Any, TypeVar

from pydantic import BaseModel, Field

from .registry import register_validator

# CSV Dialect-related validation

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
    escapechar: str | None = Field(default=None)
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
            quotechar=excel.quotechar or '"',
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
            quotechar=excel_tab.quotechar or '"',
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
            quotechar=unix.quotechar or '"',
            skipinitialspace=unix.skipinitialspace,
        )


# Table Schema-related validation


class TypeEnum(str, Enum):
    """Enumeration of the possible types for the Table Schema."""

    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    YEAR = "year"
    YEARMONTH = "yearmonth"
    DURATION = "duration"
    GEOPOINT = "geopoint"
    GEOJSON = "geojson"
    ANY = "any"


class ConstraintsValidator(BaseModel):
    """Validator for the constraints in the Table Schema.

    This class is used to validate the constraints in the Table Schema. It is based on
    the constraints defined in the Table Schema specification.

    Attributes:
        required: A boolean indicating if the value is required.
        unique: A boolean indicating if the value is unique.
        minimum: The minimum of the value. Applies to types: integer, number, date,
            time, datetime, year, yearmonth.
        maximum: The maximum value. Applies to types: integer, number, date,
            time, datetime, year, yearmonth.
        minLength: The minimum length of the field. Applies to collections (string,
            array, object).
        maxLength: The maximum length of the field. Applies to collections (string,
            array, object).
        pattern: A regular expression pattern that the value must match. Applies to
            types: string.
        enum: A list of possible values for the field.

    """

    required: bool | None = Field(None)
    unique: bool | None = Field(None)
    minimum: int | float | None = Field(None)
    maximum: int | float | None = Field(None)
    minLength: int | None = Field(None)
    maxLength: int | None = Field(None)
    pattern: str | None = Field(None)
    enum: list[Any] | None = Field(None)


class ColumnValidator(BaseModel):
    """Validator for the columns in the Table Schema.

    This class is used to validate the columns in the Table Schema. It is based on the
    columns defined in the Table Schema specification.

    Attributes:
        name: The name of the column.
        title: A nicer human readable label or title for the field.
        type_: A string specifying the type.
        format_: A string specifying a format.
        example: An example value for the field.
        description: A description for the field.
        constraints: A dictionary of constraints for the field.

    """

    name: str = Field(..., description="Column name.")
    title: str | None = Field(
        None, description="A nicer human readable label or title for the field."
    )
    type_: TypeEnum | None = Field(
        None, alias="type", description="A string specifying the type."
    )
    format_: str | None = Field(
        None, alias="format", description="A string specifying a format."
    )
    example: str | None = Field(None, description="An example value for the field.")
    description: str | None = Field(None, description="A description for the field.")
    constraints: ConstraintsValidator | None = Field(
        None, description="A dictionary of constraints for the field."
    )

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        """Dump the model to a dictionary.

        This method dumps the model to a dictionary. It sets exclude_unset to True and
        by_alias to True, so that only the attributes that were set are included in the
        dictionary and their aliases are always used.

        Finally, it converts the attributes that are Enum instances to their values.

        Returns:
            A dictionary with the model attributes.

        """
        kwargs["exclude_unset"] = True
        kwargs["by_alias"] = True
        output = super().model_dump(*args, **kwargs)
        for key, value in output.items():
            if isinstance(value, Enum):
                output[key] = value.value
        return output
