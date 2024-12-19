"""Module that contains validators for the table schema."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field

from .registry import register_validator


class TypeEnum(str, Enum):
    """Enumeration of the possible types for the Table Schema."""

    STRING = "string"
    NUMBER = "number"
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


class FormatDefault(str, Enum):
    """Enumeration of the possible formats for the Table Schema."""

    DEFAULT = "default"


class FormatString(str, Enum):
    """Enumeration of the possible formats for the Table Schema for the string type."""

    DEFAULT = "default"
    EMAIL = "email"
    URI = "uri"
    BINARY = "binary"
    UUID = "uuid"


class FormatDateTime(str, Enum):
    """Enumeration of the formats for the Table Schema for the datetime type.

    default: Declares that the datetime objects follows the ISO8601 format.
        - datetime: YYYY-MM-DD
        - time: hh:mm:ss in 24-hour time and UTC timezone.
        - datetime: YYYY-MM-DDThh:mm:ssZ in 24-hour time and UTC timezone.
    any: Any parsable datetime format.
    """

    DEFAULT = "default"
    ANY = "any"


class FormatGeoPoint(str, Enum):
    """Enumeration of the formats for the Table Schema for the geopoint type.

    default: Declares that the geopoint objects follows the ISO6709 format, ie.
        latitude and longitude, are provided as a string, eg. '37.7749,-122.4194'.
    array: Declares that the geopoint objects are an array with two numbers, eg.
        [37.7749, -122.4194].
    object: Declares that the geopoint objects are  JSON object with with 'lon'
        and 'lat' keys, eg. "{'lat': 37.7749, 'lon': -122.4194}".

    """

    DEFAULT = "default"
    ARRAY = "array"
    OBJECT = "object"


class FormatGeoJSON(str, Enum):
    """Enumeration of the formats for the Table Schema for the geojson type.

    default: Declares that the geojson objects are JSON objects that follow the
        GeoJSON specification.
    topojson: Declares that the geojson objects are JSON objects that follow the
        TopoJSON specification.

    """

    DEFAULT = "default"
    TOPOJSON = "topojson"


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


class CommonValidator(BaseModel):
    """Validator for the columns in the Table Schema.

    This class is used to validate the columns in the Table Schema. It is based on the
    columns defined in the Table Schema specification.

    Attributes:
        name: The name of the column.
        title: A nicer human readable label or title for the field.
        type_: A string specifying the type.
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


class DefaultColumnValidator(CommonValidator):
    """Default column validator for anything that does not have a specific one.

    Attributes:
        type_: A string specifying the type, valid values are any of the TypeEnum that
            do not have a specific validator.
        format_: A string specifying a format, with valid values being 'default' and
            None.

    """

    type_: Literal[
        TypeEnum.OBJECT,
        TypeEnum.ARRAY,
        TypeEnum.YEAR,
        TypeEnum.YEARMONTH,
        TypeEnum.DURATION,
        TypeEnum.ANY,
        None,
    ] = Field(None, alias="type", description="A string specifying the type.")
    format_: FormatDefault | None = Field(
        None, alias="format", description="A string specifying a format."
    )


class StringColumnValidator(CommonValidator):
    """Validator for the string columns in the Table Schema.

    This class is used to validate the string columns in the Table Schema. It is based
    on the columns defined in the Table Schema specification.

    Attributes:
        type_: A string specifying the type, with valid values being 'string'.
        format_: A string specifying a format, with valid values being 'default',
            'email', 'uri', 'binary', 'uuid' and None.

    """

    type_: Literal[TypeEnum.STRING] = Field(
        TypeEnum.STRING, alias="type", description="A string specifying the type."
    )
    format_: FormatString | None = Field(
        None, alias="format", description="A string specifying a format."
    )


class NumberColumnValidator(CommonValidator):
    """Validator for the number columns in the Table Schema.

    This class is used to validate the number columns in the Table Schema. It is based
    on the columns defined in the Table Schema specification.

    Attributes:
        type_: A string specifying the type, with valid values being 'number'.
        format_: A string specifying a format, with valid values being 'default' and
            None.
        decimalChar: The character used to separate the integer and fractional. If
            None, '.' is used.
        groupChar: The character used to separate groups of thousands. None assumed.
        bareNumber: If True, the number is a bare number, without any formatting. If
            None, True is used. If false the contents of this field may contain leading
            and/or trailing non-numeric characters that must be stripped to parse the
            number, eg. '95%', '£50.5'.

    """

    type_: Literal[TypeEnum.NUMBER] = Field(
        TypeEnum.NUMBER, alias="type", description="A string specifying the type."
    )
    format_: FormatDefault | None = Field(
        None, alias="format", description="A string specifying a format."
    )
    decimalChar: str | None = Field(
        None,
        description="The character used to separate the integer and fractional. "
        + "If None, '.' is used.",
    )
    groupChar: str | None = Field(
        None, description="The character used to separate groups of thousands."
    )
    bareNumber: bool | None = Field(
        None,
        description="If True, the number is a bare number, without any formatting."
        + "If None, True is used. If false the contents of this field may contain "
        + "leading and/or trailing non-numeric characters that must be stripped to "
        + "parse the number, eg. '95%', '£50.5'.",
    )


class IntegerColumnValidator(CommonValidator):
    """Validator for the integer columns in the Table Schema.

    This class is used to validate the integer columns in the Table Schema. It is based
    on the columns defined in the Table Schema specification.

    Attributes:
        type_: A string specifying the type, with valid values being 'integer'.
        format_: A string specifying a format, with valid values being 'default' and
            None.
        bareNumber: If True, the number is a bare number, without any formatting. If
            None, True is used. If false the contents of this field may contain leading
            and/or trailing non-numeric characters that must be stripped to parse the
            number, eg. '95%', '£50'.

    """

    type_: Literal[TypeEnum.INTEGER] = Field(
        TypeEnum.INTEGER, alias="type", description="A string specifying the type."
    )
    format_: FormatDefault | None = Field(
        None, alias="format", description="A string specifying a format."
    )
    bareNumber: bool | None = Field(
        None,
        description="If True, the number is a bare number, without any formatting."
        + "If None, True is used. If false the contents of this field may contain "
        + "leading and/or trailing non-numeric characters that must be stripped to "
        + "parse the number, eg. '95%', '£50'.",
    )


class BooleanColumnValidator(CommonValidator):
    """Validator for the boolean columns in the Table Schema.

    This class is used to validate the boolean columns in the Table Schema. It is based
    on the columns defined in the Table Schema specification.

    Attributes:
        type_: A string specifying the type, with valid values being 'boolean'.
        format_: A string specifying a format, with valid values being 'default' and
            None.
        trueValues: A list of strings that should be considered as True. If None,
            ['true', 'True', 'TRUE', '1'] is used.
        falseValues: A list of strings that should be considered as False. If None,
            ['false', 'False', 'FALSE', '0'] is used

    """

    type_: Literal[TypeEnum.BOOLEAN] = Field(
        TypeEnum.BOOLEAN, alias="type", description="A string specifying the type."
    )
    format_: FormatDefault | None = Field(
        None, alias="format", description="A string specifying a format."
    )
    trueValues: list[str] | None = Field(
        None,
        description="A list of strings that should be considered as True. If None, "
        + "['true', 'True', 'TRUE', '1'] is used.",
    )
    falseValues: list[str] | None = Field(
        None,
        description="A list of strings that should be considered as False. If None, "
        + "['false', 'False', 'FALSE', '0'] is used.",
    )


class DateTimeColumnValidator(CommonValidator):
    """Validator for the datetime columns in the Table Schema.

    This class is used to validate the datetime columns in the Table Schema. It is based
    on the columns defined in the Table Schema specification.

    Attributes:
        type_: A string specifying the type, with valid values being 'datetime'.
        format_: A string specifying a format. It can be 'default' or 'any', or a string
            with a custom format parsable by Python / C standard 'strptime', eg.
            '%d/%m/%y'.

    """

    type_: Literal[TypeEnum.DATETIME, TypeEnum.DATE, TypeEnum.TIME] = Field(
        TypeEnum.DATETIME, alias="type", description="A string specifying the type."
    )
    format_: FormatDateTime | str | None = Field(
        None,
        alias="format",
        description="A string specifying a format. It can be "
        + "'default' or 'any', or a string with a custom format parsable by Python / C "
        + "standard 'strptime', eg. '%d/%m/%y'.",
    )


class GeopointColumnValidator(CommonValidator):
    """Validator for the geopoint columns in the Table Schema.

    This class is used to validate the geopoint columns in the Table Schema. It is based
    on the columns defined in the Table Schema specification.

    Attributes:
        type_: A string specifying the type, with valid values being 'geopoint'.
        format_: A string specifying a format, with valid values being 'default',
            'array', 'object' and None.

    """

    type_: Literal[TypeEnum.GEOPOINT] = Field(
        TypeEnum.GEOPOINT, alias="type", description="A string specifying the type."
    )
    format_: FormatGeoPoint | None = Field(
        None, alias="format", description="A string specifying a format."
    )


class GeoJSONColumnValidator(CommonValidator):
    """Validator for the geojson columns in the Table Schema.

    This class is used to validate the geojson columns in the Table Schema. It is based
    on the columns defined in the Table Schema specification.

    Attributes:
        type_: A string specifying the type, with valid values being 'geojson'.
        format_: A string specifying a format, with valid values being 'default',
            'topojson' and None.

    """

    type_: Literal[TypeEnum.GEOJSON] = Field(
        TypeEnum.GEOJSON, alias="type", description="A string specifying the type."
    )
    format_: FormatGeoJSON | None = Field(
        None, alias="format", description="A string specifying a format."
    )


ColumnValidator = Annotated[
    StringColumnValidator
    | NumberColumnValidator
    | IntegerColumnValidator
    | BooleanColumnValidator
    | DateTimeColumnValidator
    | GeopointColumnValidator
    | GeoJSONColumnValidator,
    Field(discriminator="type_"),
]
"""Annotated type for the ColumnValidator."""


@register_validator("schema")
class SchemaValidator(BaseModel):
    """Validator for the Table Schema in the CSVY file.

    This class is used to validate the Table Schema in the CSVY file. It is based on the
    schema defined in the Table Schema specification.

    Attributes:
        fields: A list of column validators.

    """

    fields: list[ColumnValidator | DefaultColumnValidator] = Field(
        ..., description="A list of column validators."
    )
    missingValues: list[str] | None = Field(
        None,
        description="A list of strings that should be considered as missing values. "
        + "If None, [''] (an empty string) is used.",
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
        for field in output["fields"]:
            for key, value in field.items():
                if isinstance(value, Enum):
                    field[key] = value.value
        return output
