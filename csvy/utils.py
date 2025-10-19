"""Utility functions for CSVY operations."""

import warnings
from typing import Any

from .validators import CSVDialectValidator


def merge_csv_options_with_dialect(
    header: dict[str, Any],
    csv_options: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Merge CSV options with dialect information from header.

    This function combines user-provided CSV options with dialect settings
    from the CSVY header. User options take precedence over dialect settings,
    and warnings are issued when conflicts are detected.

    Args:
        header: The CSVY header dictionary containing metadata including
            potential csv_dialect information.
        csv_options: User-provided CSV options dictionary. Can be None.

    Returns:
        A tuple containing:
        - merged_options: Dictionary with combined CSV options
        - updated_header: Header dictionary with potentially updated dialect info

    """
    merged_options = csv_options.copy() if csv_options is not None else {}
    updated_header = header.copy()

    if "csv_dialect" not in header or not isinstance(
        header["csv_dialect"], CSVDialectValidator
    ):
        return merged_options, updated_header

    dialect_validator = header["csv_dialect"]
    dialect_updated = False

    for dialect_attr in CSVDialectValidator.model_fields.keys():
        dialect_value = getattr(dialect_validator, dialect_attr)
        user_value = merged_options.get(dialect_attr, dialect_value)

        # Update the dialect validator, if needed
        if user_value != dialect_value:
            warnings.warn(
                f"CSV option '{dialect_attr}' ({user_value!r}) conflicts with "
                f"dialect setting ({dialect_value!r}). Using user option.",
                UserWarning,
                stacklevel=2,
            )
            setattr(dialect_validator, dialect_attr, user_value)
            dialect_updated = True

        # Complete the options dictionary
        merged_options[dialect_attr] = user_value

    if dialect_updated:
        updated_header["csv_dialect"] = dialect_validator

    return merged_options, updated_header
