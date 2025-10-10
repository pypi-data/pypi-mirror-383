# Dazbo Commons

## Table of Contents

- [Overview](#overview)
- [To Install and Use](#to-install-and-use)
- [Coloured Logging Module](#coloured-logging-module)
- [To Build From Package Source](#to-build-from-package-source)

## Overview

A reusable utility library.

```text
dazbo-commons/
│
├── src/
│   └── dazbo_commons/
│       ├── __init__.py
│       └── colored_logging.py
│
├── tests/
│   └── test_colored_logging.py
│
├── .env
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

## To Install and Use

You can simply install the package from [PyPi](https://pypi.org/project/dazbo-commons/). There's no need to clone this repo.

```bash
pip install --upgrade dazbo-commons
```

Then, in your Python code, include this `import`:

```python
import dazbo_commons as dc
```

### Coloured Logging Module

This module provides a function to retrieve a logger that logs to the console, with colour.

Example:

```python
import logging
import dazbo_commons as dc

logger_name = __name__ # or just pass in a str
logger = dc.retrieve_console_logger(logger_name)
logger.setLevel(logging.INFO) # Set threshold. E.g. INFO, DEBUG, or whatever

logger.info("Some msg") # log at info level
```

### File Locations Module

This module is used to retrieve a `Locations` class, which stores directory paths 
based on the location of a specified script. 
This makes it convenient to manage and access different file and directory paths 
relative to a given script's location.

Example:

```python
import dazbo_commons as dc
APPNAME = "My_App"

locations = get_locations(APP_NAME)

with open(locations.input_file, mode="rt") as f:
    input_data = f.read().splitlines()
```

## To Build From Package Source

1. Create a Python virtual and install dependencies. E.g.

```bash
make install # runs uv sync
```

2. Run tests. E.g.

```bash
make test

# Or for more verbose logging
py -m unittest discover -v -s tests -p '*.py'
```

3. Make any required updates to the `pyproject.toml` file. E.g. the `version` attribute.

4. Build the package.

```bash
make build-dist
```

This generates a `dist` folder in your project folder and uploads it to PyPi.

You'll be prompted for your API token. In my experience, when doing this from a terminal inside VS Code, Ctrl-V doesn't work here. So I use Paste from the menu, and this works.

And we're done!