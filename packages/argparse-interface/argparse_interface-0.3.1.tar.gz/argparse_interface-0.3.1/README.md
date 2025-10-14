# ArgUI

![ArgUI's Logo](https://github.com/Sorcerio/Argparse-Interface/blob/master/assets/ArgUILogo_transparent.png?raw=true)

An automatic, terminal based interactive interface for any Python 3 `argparse` command line with keyboard and mouse support.

* [ArgUI](#argui)
  * [See It in Action](#see-it-in-action)
  * [Usage](#usage)
    * [Install as a Dependency](#install-as-a-dependency)
    * [Setup Your Argparse](#setup-your-argparse)
    * [Run Your Program](#run-your-program)
    * [Navigation](#navigation)
    * [Advanced Argument Types](#advanced-argument-types)
      * [Example Usage](#example-usage)
      * [File Select](#file-select)
  * [Development Setup](#development-setup)
    * [Setup the Environment](#setup-the-environment)
    * [Build the Project](#build-the-project)

---

## See It in Action

![Demo of the features in ArgUI](https://github.com/Sorcerio/Argparse-Interface/blob/master/assets/ArgUIDemo_small.gif?raw=true)

Get a feel for the features of ArgUI using the [Demo.py](./argui/Demo.py) code included in this project.

## Usage

### Install as a Dependency

The ArgUI package is [available on PyPi](https://pypi.org/project/Argparse-Interface/).

It can be installed by calling: `pip install argparse-interface`

### Setup Your Argparse

ArgUI supports wrapping any implementation of the Python 3 `argparse` native library.
This will all you to use both standard terminal and interface modes to interact with your program.

```python
# Import
import argparse
import argui

# Setup your ArgumentParser normally
parser = argparse.ArgumentParser(prog="Demo")

# `add_argument`, `add_argument_group`, etc...

# Wrap your parser
interface = argui.Wrapper(parser)

# Get arguments
args: argparse.Namespace = interface.parseArgs()

# `args` is the same as if you had called `parser.parse_args()`
```

See [Demo.py](./argui/Demo.py) for more information.

### Run Your Program

Your program can now be run in both CLI and GUI modes.

To run in CLI mode, simply use your script as normal like `python foo.py -h`.

To run in GUI mode, provide only the `--gui` (by default) argument like `python foo.py --gui`.

### Navigation

Mouse navigation of the GUI is possible in _most_ terminals.

There are known issues with the VSCode terminal on Windows 10 and some others.
However, Mouse navigation does work in Powershell when opened on its own.

Keyboard navigation is always available using `Tab`, `Arrow Keys`, and `Enter`.
But make note that if you are using a terminal within another program (like VSCode), that some more advanced keyboard commands (like `CTRL+S`) may be captured by the container program and not sent to the GUI.

### Advanced Argument Types

ArgUI also provides a number of meta types to be used with the `.add_argument(type=...)` function to add additional functionality to the interface mode.

These can be accessed with `import argui.types`.

#### Example Usage

Meta Types can be used for the `type` keyword argument anywhere you call the `add_argument(...)` function.

```python
# Import
import argparse
import argui
from argui.types import FileSelectFile

# Setup your ArgumentParser normally
parser = argparse.ArgumentParser(prog="Demo")

# Define your arguments
parser.add_argument(
    "-p",
    "--path",
    type=FileSelectFile(exts=[".png", ".jpg"]), # Instantiate the Meta Type
    help="A file or directory path argument"
)

# Wrap the parser with ArgUI and use as normal (see above)
```

#### File Select

All options will show the File Select input in the GUI mode and operate as advanced types in the CLI mode.

| Type | Effect | Notes |
| ---- | ------ | ----- |
| `pathlib.Path`<br>_(native)_ | Allows for any file or directory to be selected. | Provided as an uninstantiated type like: `type=Path` |
| `FileSelectFile` | Allows only files to be selected. Optionally restricts selection to specified file types. | Accepts a list of extensions to whitelist. |
| `FileSelectDir` | Allows only directories to be selected. |    |


## Development Setup

These instructions assume you will be using the [uv](https://docs.astral.sh/uv/) Python package manager.

### Setup the Environment

1. Install [uv](https://docs.astral.sh/uv/).
1. Clone this repo and enter the directory with a terminal.
1. Run `uv run demo.py` to run the demo or any other scripts you create.

### Build the Project

1. [Setup the environment](#setup-the-environment) and successfully run the demo.
1. If necessary, bump the package version with `uv version`.
1. Run `uv build` to build to the `dist/` directory.
1. Ensure that only the package version you want to publish is in the `dist/` directory.
1. Run `python check.py` with your primary, clean, Python distribution to initiate the demo within an isolated test environment.
    * If the demo does not function, the package is broken and needs to be fixed.
1. Run `uv publish` to publish the package to PyPi.
1. Run `uv run --with argui --no-project -- python -c "import argui"` to test the package as pulled from PyPi.
