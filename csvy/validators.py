"""This module contains validators for the CSVY file format."""

import csv
from typing import Optional, TypeVar

from pydantic import BaseModel, Field

# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar("T", bound="CSVDialectValidator")


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
        """Converts the validator to a custom csv.Dialect object.

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
        """Returns a validator for the Excel CSV Dialect.

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
        """Returns a validator for the Excel Tab CSV Dialect.

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
        """Returns a validator for the Unix CSV Dialect.

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
