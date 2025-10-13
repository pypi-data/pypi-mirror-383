import os
from typing import Optional

DEFAULT_FOLDER = ".browser"
EXTENSIONS_FOLDER = "Extensions"


class BrowserStorage:
    """
    Represents a browser storage. It can be used to place profiles.
    """

    def __init__(self, base_directory: Optional[str] = None) -> None:
        """
        The constructor for BrowserStorage class.

        Parameters
        ----------
        base_directory : Optional[str]
            Base directory of browser storage.
        """

        self._base_directory = base_directory or os.path.join(
            os.getcwd(), DEFAULT_FOLDER)
        self._extensions_directory = os.path.join(
            self._base_directory, EXTENSIONS_FOLDER)

    def get_base_directory(self) -> str:
        """Gets the base directory of browser storage."""
        return self._base_directory

    def get_extensions_directory(self) -> str:
        """Gets the extensions directory of browser storage."""
        return self._extensions_directory
