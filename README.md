# CSVY for Python

[![Test and build](https://github.com/ImperialCollegeLondon/csvy/actions/workflows/ci.yml/badge.svg)](https://github.com/ImperialCollegeLondon/csvy/actions/workflows/ci.yml)

CSV is a popular format for storing tabular data used in many disciplines. Metadata concerning the contents of the file is often included in the header, but it rarely follows a format that is machine readable - sometimes is not even human readable! In some cases, such information is provided in a separate file, which is not ideal as it is easy for data and metadata to get separated.

CSVY is a small Python package to handle CSV files in which the metadata in the header is formatted in YAML. It supports reading/writing tabular data contained in numpy arrays, pandas DataFrames and nested lists, as well as metadata using a standard python dictionary. Ultimately, it aims to incorporate information about the CSV dialect used and a Table Schema specifying the contents of each column to aid the reading and interpretation of the data.
