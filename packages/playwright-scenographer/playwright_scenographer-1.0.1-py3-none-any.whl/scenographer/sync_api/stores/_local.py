import os
from typing import Optional

from scenographer.sync_api.core._web_store import WebStore
from scenographer.sync_api.utils._bytes_from_file import bytes_from_file


class LocalWebStore(WebStore):
    """
    Represents a web store using the file system.
    """

    def __init__(self, base_directory: Optional[str] = None) -> None:
        """
        The constructor for LocalWebStore class.

        Parameters
        ----------
        base_directory : Optional[str]
            Base directory of browser storage.
        """

        self._base_directory = base_directory or os.path.join(
            os.getcwd(), ".webextensions")

    def download(self, extension_id: str) -> bytes:
        """
        Downloads a WebExtension.

        Parameters
        ----------
        extension_id : str
            The extension identifier.

        Returns
        -------
        bytes
            WebExtension content.
        """

        filename = f"{extension_id}.crx"
        path = os.path.join(self._base_directory, filename)

        content = bytes_from_file(path)

        return bytes(content)
