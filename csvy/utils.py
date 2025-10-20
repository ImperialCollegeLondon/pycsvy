"""Utility functions for CSVY operations."""

import warnings
from typing import Any

from .validators import CSVDialectValidator


def merge_csv_options_with_dialect(
    header: dict[str, Any],
    csv_options: dict[str, Any] | None,
    overrides: dict[str, str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Merge CSV options with dialect information from header.

    This function combines user-provided CSV options with dialect settings
    from the CSVY header. User options take precedence over dialect settings,
    and warnings are issued when conflicts are detected.

    Args:
        header: The CSVY header dictionary containing metadata including
            potential csv_dialect information.
        csv_options: User-provided CSV options dictionary. Can be None.
        overrides: Optional mapping from library-specific option names to
            dialect attribute names. For example, {"sep": "delimiter"} maps
            pandas' "sep" option to the dialect's "delimiter" attribute.

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

    # Create a copy of the dialect for updates to avoid modifying the original
    updated_dialect = None

    for dialect_attr in CSVDialectValidator.model_fields.keys():
        dialect_value = getattr(dialect_validator, dialect_attr)

        # Check if user provided this option, possibly under a different name
        user_value = None
        option_name = dialect_attr

        # First check if the dialect attribute name is provided directly
        if dialect_attr in merged_options:
            user_value = merged_options[dialect_attr]
        # Then check if a library-specific name maps to this dialect attribute
        elif overrides:
            for lib_name, mapped_attr in overrides.items():
                if mapped_attr == dialect_attr and lib_name in merged_options:
                    user_value = merged_options[lib_name]
                    option_name = lib_name
                    break

        # If no user value found, use the dialect default
        if user_value is None:
            user_value = dialect_value

        # Update the dialect validator, if needed
        if user_value != dialect_value:
            # Use the original option name in the warning if it was overridden
            option_name = dialect_attr
            if overrides and dialect_attr in overrides.values():
                # Find the original name used by the user
                for orig_name, mapped_name in overrides.items():
                    if mapped_name == dialect_attr and orig_name in merged_options:
                        option_name = orig_name
                        break

            warnings.warn(
                f"CSV option '{option_name}' ({user_value!r}) conflicts with "
                f"dialect setting ({dialect_value!r}). Using user option.",
                UserWarning,
                stacklevel=2,
            )

            # Create a copy of the dialect if this is the first update
            if updated_dialect is None:
                updated_dialect = CSVDialectValidator(**dialect_validator.model_dump())

            setattr(updated_dialect, dialect_attr, user_value)
            dialect_updated = True

        # Ensure the merged_options has the value in the appropriate format
        # For overridden attributes, keep the library-specific name
        if overrides and dialect_attr in overrides.values():
            # Find the library-specific name for this dialect attribute
            for lib_name, mapped_attr in overrides.items():
                if mapped_attr == dialect_attr:
                    if lib_name not in merged_options:
                        merged_options[lib_name] = user_value
                    break
        else:
            # Use the dialect attribute name
            if dialect_attr not in merged_options:
                merged_options[dialect_attr] = user_value

    if dialect_updated and updated_dialect is not None:
        updated_header["csv_dialect"] = updated_dialect

    return merged_options, updated_header
