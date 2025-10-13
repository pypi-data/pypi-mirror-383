# reloci

[![PyPI](https://img.shields.io/pypi/v/reloci)](https://pypi.org/project/reloci/)
[![License](https://img.shields.io/github/license/153957/reloci)](https://github.com/153957/reloci/blob/main/LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/153957/reloci/tests.yml?branch=main)](https://github.com/153957/reloci/actions)

This can be used to reorganise photos into directories by date.


## Usage

This is a command line utility to copy or move files from one location
to another location using the metadata in the files to order them
into logical directories.

    reloci current/path/to/files path/to/destination

To see all options use

    reloci --help

Currently the files will be ordered based on the creation date of the
files. Use the `dryrun` option to check if the planned move/copy matches
your expectations.

Specifically for time-lapse shooting there is a command to group photos
from the same sequence, based on a consistent interval between subsequent
photos. Use the `group` option to immediately group the found sequences in
directories.

    check_interval --pattern "APL_*.NEF" --group

Additionally, there is a command to view all relevant EXIF tags from a
single file, and how they are interpreted by the FileInfo class.

    reloci_info path/to/a/file.jpg


## Installation

If desired create a virtual environment then install this package from PyPI

    pip install reloci


## Setup for development

Create a new virtual env with Python 3.13 and install the requirements:

    pip install -e .[test]
