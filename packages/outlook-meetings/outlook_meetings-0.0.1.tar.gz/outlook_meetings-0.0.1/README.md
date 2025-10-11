# outlook-meetings

[![PyPI](https://img.shields.io/pypi/v/outlook-meetings.svg)](https://pypi.org/project/outlook-meetings/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/outlook-meetings?include_prereleases&label=changelog)](https://github.com/sukhbinder/outlook-meetings/releases)
[![Tests](https://github.com/sukhbinder/outlook-meetings/actions/workflows/test.yml/badge.svg)](https://github.com/sukhbinder/outlook-meetings/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/outlook-meetings/blob/master/LICENSE)

Create outlook meetings using cli

## Installation

Install this tool using `pip`:
```bash
pip install outlook-meetings
```
## Usage

For help, run:
```bash
meet --help
```
You can also use:
```bash
python -m meet --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd outlook-meetings
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
