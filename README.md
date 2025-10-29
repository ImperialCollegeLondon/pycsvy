# CSVY for Python

[![PyPI version shields.io](https://img.shields.io/pypi/v/pycsvy.svg)](https://pypi.python.org/pypi/pycsvy/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/pycsvy.svg)](https://anaconda.org/conda-forge/pycsvy)
[![PyPI status](https://img.shields.io/pypi/status/pycsvy.svg)](https://pypi.python.org/pypi/pycsvy/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pycsvy.svg)](https://pypi.python.org/pypi/pycsvy/)
[![PyPI license](https://img.shields.io/pypi/l/pycsvy.svg)](https://pypi.python.org/pypi/pycsvy/)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pycsvy/badges/platforms.svg)](https://anaconda.org/conda-forge/pycsvy)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pycsvy/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/pycsvy)
[![Test and build](https://github.com/ImperialCollegeLondon/csvy/actions/workflows/ci.yml/badge.svg)](https://github.com/ImperialCollegeLondon/csvy/actions/workflows/ci.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ImperialCollegeLondon/pycsvy/develop.svg)](https://results.pre-commit.ci/latest/github/ImperialCollegeLondon/pycsvy/develop)
[![codecov](https://codecov.io/gh/ImperialCollegeLondon/pycsvy/branch/develop/graph/badge.svg?token=N03KYNUD18)](https://codecov.io/gh/ImperialCollegeLondon/pycsvy)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/8d1b791b315f4814a128d94483499561)](https://app.codacy.com/gh/ImperialCollegeLondon/pycsvy/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ImperialCollegeLondon/pycsvy&amp;utm_campaign=Badge_Grade)
[![DOI](https://zenodo.org/badge/493810031.svg)](https://doi.org/10.5281/zenodo.7627691)
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-7-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

CSV is a popular format for storing tabular data used in many disciplines. Metadata
concerning the contents of the file is often included in the header, but it rarely
follows a format that is machine readable - sometimes is not even human readable! In
some cases, such information is provided in a separate file, which is not ideal as it is
easy for data and metadata to get separated.

CSVY is a small Python package to handle CSV files in which the metadata in the header
is formatted in YAML. It supports reading/writing tabular data contained in numpy
arrays, pandas DataFrames, polars DataFrames, and nested lists, as well as metadata using a standard python
dictionary. Ultimately, it aims to incorporate information about the [CSV
dialect](https://specs.frictionlessdata.io/csv-dialect/) used and a [Table
Schema](https://specs.frictionlessdata.io/table-schema/) specifying the contents of each
column to aid the reading and interpretation of the data.

## Installation

'pycsvy' is available in PyPI and conda-forge therefore its installation is as easy as:

```bash
pip install pycsvy
```

or

```bash
conda install --channel=conda-forge pycsvy
```

In order to support reading into `numpy` arrays, `pandas` DataFrames or `polars` DataFrames, you will
need to install those packages, too. This can be support by specifying extras, ie:

```bash
pip install pycsvy[pandas, polars]
```

## Usage

In the simplest case, to save some data contained in `data` and some metadata contained
in a `metadata` dictionary into a CSVY file `important_data.csv` (the extension is not
relevant), just do the following:

```python
import csvy

csvy.write("important_data.csv", data, metadata)
```

The resulting file will have the YAML-formatted header in between `---` markers with,
optionally, a comment character starting each header line. It could look something like
the following:

```text
---
name: my-dataset
title: Example file of csvy
description: Show a csvy sample file.
encoding: utf-8
schema:
  fields:
  - name: Date
    type: object
  - name: WTI
    type: number
---
Date,WTI
1986-01-02,25.56
1986-01-03,26.00
1986-01-06,26.53
1986-01-07,25.85
1986-01-08,25.87
```

For reading the information back:

```python
import csvy

# To read into a numpy array
data, metadata = csvy.read_to_array("important_data.csv")

# To read into a pandas DataFrame
data, metadata = csvy.read_to_dataframe("important_data.csv")

# To read into a polars LazyFrame
data, metadata = csvy.read_to_polars("important_data.csv")

# To read into a polars DataFrame
data, metadata = csvy.read_to_polars("important_data.csv", eager=True)
```

The appropriate writer/reader will be selected based on the type of `data`:

- numpy array: `np.savetxt` and `np.loadtxt`
- pandas DataFrame: `pd.DataFrame.to_csv` and `pd.read_csv`
- polars DataFrame/LazyFrame: `pl.DataFrame.write_csv` and `pl.scan_csv`
- nested lists:' `csv.writer` and `csv.reader`

Options can be passed to the tabular data writer/reader by setting the `csv_options`
dictionary. Likewise you can set the `yaml_options` dictionary with whatever options you
want to pass to `yaml.safe_load` and `yaml.safe_dump` functions, reading/writing the
YAML-formatted header, respectively.

You can also instruct a writer to use line buffering, instead of the usual chunk buffering.

Finally, you can control the character(s) used to indicate comments by setting the
`comment` keyword when writing a file. By default, there is no character ("").
During reading, the comment character is found automatically.

Note that, by default, these reader functions will assume UTF-8 encoding. You can choose a
different character encoding by setting the `encoding` keyword argument to any of these
reader or writer functions. For example, on Windows, Windows-1252 encoding is often used,
which can be specified via `encoding='cp1252'`.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://www.imperial.ac.uk/admin-services/ict/self-service/research-support/rcs/service-offering/research-software-engineering/"><img src="https://avatars.githubusercontent.com/u/6095790?v=4?s=100" width="100px;" alt="Diego Alonso Álvarez"/><br /><sub><b>Diego Alonso Álvarez</b></sub></a><br /><a href="#infra-dalonsoa" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#ideas-dalonsoa" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-dalonsoa" title="Maintenance">🚧</a> <a href="https://github.com/ImperialCollegeLondon/pycsvy/commits?author=dalonsoa" title="Tests">⚠️</a> <a href="https://github.com/ImperialCollegeLondon/pycsvy/issues?q=author%3Adalonsoa" title="Bug reports">🐛</a> <a href="https://github.com/ImperialCollegeLondon/pycsvy/commits?author=dalonsoa" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.imperial.ac.uk/research-software-engineering"><img src="https://avatars.githubusercontent.com/u/23149834?v=4?s=100" width="100px;" alt="Alex Dewar"/><br /><sub><b>Alex Dewar</b></sub></a><br /><a href="#ideas-alexdewar" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/ImperialCollegeLondon/pycsvy/commits?author=alexdewar" title="Tests">⚠️</a> <a href="https://github.com/ImperialCollegeLondon/pycsvy/commits?author=alexdewar" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/AdrianDAlessandro"><img src="https://avatars.githubusercontent.com/u/40875798?v=4?s=100" width="100px;" alt="Adrian D'Alessandro"/><br /><sub><b>Adrian D'Alessandro</b></sub></a><br /><a href="https://github.com/ImperialCollegeLondon/pycsvy/issues?q=author%3AAdrianDAlessandro" title="Bug reports">🐛</a> <a href="https://github.com/ImperialCollegeLondon/pycsvy/commits?author=AdrianDAlessandro" title="Code">💻</a> <a href="https://github.com/ImperialCollegeLondon/pycsvy/commits?author=AdrianDAlessandro" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.imperial.ac.uk/research-software-engineering"><img src="https://avatars.githubusercontent.com/u/6853046?v=4?s=100" width="100px;" alt="James Paul Turner"/><br /><sub><b>James Paul Turner</b></sub></a><br /><a href="#infra-jamesturner246" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/ImperialCollegeLondon/pycsvy/commits?author=jamesturner246" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://dc2917.github.io"><img src="https://avatars.githubusercontent.com/u/45606273?v=4?s=100" width="100px;" alt="Dan Cummins"/><br /><sub><b>Dan Cummins</b></sub></a><br /><a href="#infra-dc2917" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/ImperialCollegeLondon/pycsvy/commits?author=dc2917" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mikeheyns"><img src="https://avatars.githubusercontent.com/u/123199379?v=4?s=100" width="100px;" alt="mikeheyns"/><br /><sub><b>mikeheyns</b></sub></a><br /><a href="#infra-mikeheyns" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://nanamanu.com"><img src="https://avatars.githubusercontent.com/u/17507528?v=4?s=100" width="100px;" alt="Nana Adjei Manu"/><br /><sub><b>Nana Adjei Manu</b></sub></a><br /><a href="#infra-claeusdev" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Kaos599"><img src="https://avatars.githubusercontent.com/u/115716485?v=4?s=100" width="100px;" alt="Harsh "/><br /><sub><b>Harsh </b></sub></a><br /><a href="https://github.com/ImperialCollegeLondon/pycsvy/commits?author=Kaos599" title="Code">💻</a> <a href="https://github.com/ImperialCollegeLondon/pycsvy/commits?author=Kaos599" title="Tests">⚠️</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
