# MAC Formatter GUI

A simple Tkinter GUI to normalize and display MAC addresses in three common formats:

- Colon: `XX:XX:XX:XX:XX:XX`
- Dash: `XX-XX-XX-XX-XX-XX`
- Dotted: `XXXX.XXXX.XXXX`

It also lets you choose UPPERCASE or lowercase and copy the results to your clipboard.

## Installation

You can install from PyPI once published:

```
pip install mac-formatter-gui
```

For local development (from this repository root):

```
pip install -e .
```

## Usage

After installation, launch the app with the console command:

```
mac-formatter
```

Or via Python:

```
python -m mac_formatter.app
```

## Requirements

- Python 3.8+
- Tkinter (comes with standard CPython on most platforms)

## Development

Build and test the distribution locally:

```
python -m build
```

Upload to TestPyPI:

```
python -m twine upload -r testpypi dist/*
```

Upload to PyPI:

```
python -m twine upload dist/*
```

