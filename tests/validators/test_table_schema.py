"""Tests for the table_schema module."""

from csvy.validators.table_schema import (
    BooleanColumnValidator,
    CommonValidator,
    ConstraintsValidator,
    DateTimeColumnValidator,
    DefaultColumnValidator,
    FormatDateTime,
    FormatDefault,
    FormatGeoJSON,
    FormatGeoPoint,
    FormatString,
    GeoJSONColumnValidator,
    GeopointColumnValidator,
    IntegerColumnValidator,
    NumberColumnValidator,
    SchemaValidator,
    StringColumnValidator,
    TypeEnum,
)


def test_common_validator():
    """Test the CommonValidator class."""
    validator = CommonValidator(
        **{
            "name": "test_column",
            "title": "Test Column",
            "example": "example_value",
            "description": "This is a test column.",
            "constraints": {
                "required": True,
                "unique": True,
            },
        }
    )
    assert validator.name == "test_column"
    assert validator.title == "Test Column"
    assert validator.example == "example_value"
    assert validator.description == "This is a test column."
    assert validator.constraints.required is True
    assert validator.constraints.unique is True

    # Test model_dump
    dumped = validator.model_dump()
    assert dumped["name"] == "test_column"
    assert dumped["title"] == "Test Column"
    assert dumped["example"] == "example_value"
    assert dumped["description"] == "This is a test column."
    assert dumped["constraints"]["required"] is True
    assert dumped["constraints"]["unique"] is True


def test_constraints_validator():
    """Test the ConstraintsValidator class."""
    validator = ConstraintsValidator(
        **{
            "required": True,
            "unique": True,
            "minimum": 1,
            "maximum": 10,
            "minLength": 2,
            "maxLength": 5,
            "pattern": "^[a-z]+$",
            "enum": ["a", "b", "c"],
        }
    )
    assert validator.required is True
    assert validator.unique is True
    assert validator.minimum == 1
    assert validator.maximum == 10
    assert validator.minLength == 2
    assert validator.maxLength == 5
    assert validator.pattern == "^[a-z]+$"
    assert validator.enum == ["a", "b", "c"]

    # Test model_dump
    dumped = validator.model_dump()
    assert dumped["required"] is True
    assert dumped["unique"] is True
    assert dumped["minimum"] == 1
    assert dumped["maximum"] == 10
    assert dumped["minLength"] == 2
    assert dumped["maxLength"] == 5
    assert dumped["pattern"] == "^[a-z]+$"
    assert dumped["enum"] == ["a", "b", "c"]


def test_default_column_validator():
    """Test the DefaultColumnValidator class."""
    validator = DefaultColumnValidator(
        **{
            "name": "test_column",
            "type": TypeEnum.OBJECT.value,
            "format": FormatDefault.DEFAULT.value,
        }
    )
    assert validator.name == "test_column"
    assert validator.type_ == TypeEnum.OBJECT
    assert validator.format_ == FormatDefault.DEFAULT

    # Test model_dump
    dumped = validator.model_dump()
    assert dumped["name"] == "test_column"
    assert dumped["type"] == "object"
    assert dumped["format"] == "default"


def test_string_column_validator():
    """Test the StringColumnValidator class."""
    validator = StringColumnValidator(
        **{
            "name": "test_column",
            "type": TypeEnum.STRING.value,
            "format": FormatString.EMAIL.value,
        }
    )
    assert validator.name == "test_column"
    assert validator.type_ == TypeEnum.STRING
    assert validator.format_ == FormatString.EMAIL

    # Test model_dump
    dumped = validator.model_dump()
    assert dumped["name"] == "test_column"
    assert dumped["type"] == "string"
    assert dumped["format"] == "email"


def test_number_column_validator():
    """Test the NumberColumnValidator class."""
    validator = NumberColumnValidator(
        **{
            "name": "test_column",
            "type": TypeEnum.NUMBER.value,
            "format": FormatDefault.DEFAULT.value,
            "decimalChar": ",",
            "groupChar": ".",
            "bareNumber": False,
        }
    )
    assert validator.name == "test_column"
    assert validator.type_ == TypeEnum.NUMBER
    assert validator.format_ == FormatDefault.DEFAULT
    assert validator.decimalChar == ","
    assert validator.groupChar == "."
    assert validator.bareNumber is False

    # Test model_dump
    dumped = validator.model_dump()
    assert dumped["name"] == "test_column"
    assert dumped["type"] == "number"
    assert dumped["format"] == "default"
    assert dumped["decimalChar"] == ","
    assert dumped["groupChar"] == "."
    assert dumped["bareNumber"] is False


def test_integer_column_validator():
    """Test the IntegerColumnValidator class."""
    validator = IntegerColumnValidator(
        **{
            "name": "test_column",
            "type": TypeEnum.INTEGER.value,
            "format": FormatDefault.DEFAULT.value,
            "bareNumber": True,
        }
    )
    assert validator.name == "test_column"
    assert validator.type_ == TypeEnum.INTEGER
    assert validator.format_ == FormatDefault.DEFAULT
    assert validator.bareNumber is True

    # Test model_dump
    dumped = validator.model_dump()
    assert dumped["name"] == "test_column"
    assert dumped["type"] == "integer"
    assert dumped["format"] == "default"
    assert dumped["bareNumber"] is True


def test_boolean_column_validator():
    """Test the BooleanColumnValidator class."""
    validator = BooleanColumnValidator(
        **{
            "name": "test_column",
            "type": TypeEnum.BOOLEAN.value,
            "format": FormatDefault.DEFAULT.value,
            "trueValues": ["yes", "true"],
            "falseValues": ["no", "false"],
        }
    )
    assert validator.name == "test_column"
    assert validator.type_ == TypeEnum.BOOLEAN
    assert validator.format_ == FormatDefault.DEFAULT
    assert validator.trueValues == ["yes", "true"]
    assert validator.falseValues == ["no", "false"]

    # Test model_dump
    dumped = validator.model_dump()
    assert dumped["name"] == "test_column"
    assert dumped["type"] == "boolean"
    assert dumped["format"] == "default"
    assert dumped["trueValues"] == ["yes", "true"]
    assert dumped["falseValues"] == ["no", "false"]


def test_datetime_column_validator():
    """Test the DateTimeColumnValidator class."""
    validator = DateTimeColumnValidator(
        **{
            "name": "test_column",
            "type": TypeEnum.DATETIME.value,
            "format": FormatDateTime.ANY.value,
        }
    )
    assert validator.name == "test_column"
    assert validator.type_ == TypeEnum.DATETIME
    assert validator.format_ == FormatDateTime.ANY

    # Test model_dump
    dumped = validator.model_dump()
    assert dumped["name"] == "test_column"
    assert dumped["type"] == "datetime"
    assert dumped["format"] == "any"


def test_geopoint_column_validator():
    """Test the GeopointColumnValidator class."""
    validator = GeopointColumnValidator(
        **{
            "name": "test_column",
            "type": TypeEnum.GEOPOINT.value,
            "format": FormatGeoPoint.ARRAY.value,
        }
    )
    assert validator.name == "test_column"
    assert validator.type_ == TypeEnum.GEOPOINT
    assert validator.format_ == FormatGeoPoint.ARRAY

    # Test model_dump
    dumped = validator.model_dump()
    assert dumped["name"] == "test_column"
    assert dumped["type"] == "geopoint"
    assert dumped["format"] == "array"


def test_geojson_column_validator():
    """Test the GeoJSONColumnValidator class."""
    validator = GeoJSONColumnValidator(
        **{
            "name": "test_column",
            "type": TypeEnum.GEOJSON.value,
            "format": FormatGeoJSON.TOPOJSON.value,
        }
    )
    assert validator.name == "test_column"
    assert validator.type_ == TypeEnum.GEOJSON
    assert validator.format_ == FormatGeoJSON.TOPOJSON

    # Test model_dump
    dumped = validator.model_dump()
    assert dumped["name"] == "test_column"
    assert dumped["type"] == "geojson"
    assert dumped["format"] == "topojson"


def test_schema_validator():
    """Test the SchemaValidator class."""
    validator = SchemaValidator(
        **{
            "fields": [
                {"name": "string_column", "type": "string"},
                {"name": "number_column", "type": "number"},
            ],
            "missingValues": ["N/A", ""],
        }
    )
    assert len(validator.fields) == 2
    assert validator.fields[0].name == "string_column"
    assert validator.fields[1].name == "number_column"
    assert validator.missingValues == ["N/A", ""]

    # Test model_dump
    dumped = validator.model_dump()
    assert len(dumped["fields"]) == 2
    assert dumped["fields"][0]["name"] == "string_column"
    assert dumped["fields"][0]["type"] == "string"
    assert dumped["fields"][1]["name"] == "number_column"
    assert dumped["fields"][1]["type"] == "number"
    assert dumped["missingValues"] == ["N/A", ""]
