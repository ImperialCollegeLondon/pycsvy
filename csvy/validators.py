import csv

from pydantic import BaseModel, Field


class CSVDialectValidator(BaseModel):
    """Implements a validator for CSV Dialects.

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
        strict: When True, raise exception Error on bad CSV input. It defaults to False.
    """

    delimiter: str = Field(default=",")
    doublequote: bool = Field(default=True)
    escapechar: str = Field(default=None)
    lineterminator: str = Field(default="\r\n")
    quotechar: str = Field(default='"')
    skipinitialspace: bool = Field(default=False)
    strict: bool = Field(default=False)

    def to_dialect(self) -> csv.Dialect:
        """Converts the validator to a custom csv.Dialect object."""
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
                "strict": self.strict,
            },
        )
        return dialect()
