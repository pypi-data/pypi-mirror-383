# Argparse Interface: File Select File Type
# A meta type that indicates the interface should only accept files.

# MARK: Imports
import argparse
from pathlib import Path
from typing import Optional, Iterable

from .MetaType import MetaType

# MARK: Classes
class FileSelectFile(MetaType):
    """
    A meta type that indicates the interface should only accept files.

    This class should be instantiated when used as in an `argparse.add_argument(...)` call's `type` as such: `argparse.add_argument(type=(...))`.

    No unnamed arguments can be provided to this class.
    Providing any will raise an `argparse.ArgumentTypeError` as this indicates the user is trying to use this class incorrectly.
    """
    # Constructor
    def __init__(self, *args, exts: Optional[Iterable[str]] = None):
        """
        exts: The file extensions to accept. Case-insensitive. Provide `None` to accept any file extension.
        """
        # Super
        super().__init__(*args)

        # Setup file extensions
        self.validExts = exts

    # Python Functions
    def __call__(self, value: str) -> Path:
        # Get the path
        try:
            path = Path(value)
        except:
            raise argparse.ArgumentTypeError(f"Value is not a file system path: {value}")

        # Check if the path is a file
        if not path.is_file():
            raise argparse.ArgumentTypeError(f"Path does not indicate a file: {path}")

        # Check file extensions
        if self.validExts is not None:
            cleanExt = path.suffix.lower().lstrip(".")
            if cleanExt not in [ext.lower().lstrip(".") for ext in self.validExts]:
                raise argparse.ArgumentTypeError(f"File extension `.{cleanExt}` is not a valid extension for this argument. Valid extensions are: {', '.join(self.validExts)}")

        return path
