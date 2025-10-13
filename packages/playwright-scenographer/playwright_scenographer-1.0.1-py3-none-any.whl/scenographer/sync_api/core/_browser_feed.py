import os
import tempfile

from crx_unpack import extract_zip

from scenographer._shared.core._browser_storage import BrowserStorage
from scenographer.sync_api.core._web_store import WebStore


class BrowserFeed:
    """
    Represents a browser feed for WebExtensions.
    """

    def __init__(self, storage: BrowserStorage, store: WebStore) -> None:
        """
        The constructor for BrowserFeed class.

        Parameters
        ----------
        storage : BrowserStorage
            Browser storage.
        store : WebStore
            Web store.
        """

        self._storage = storage
        self._store = store

    def install_extension(self, extension_id: str) -> None:
        """
        Installs a WebExtension.

        Parameters
        ----------
        extension_id : str
            The extension identifier.
        """

        destination = os.path.join(
            self._storage.get_extensions_directory(),
            extension_id)

        if os.path.exists(destination):
            return

        download = self._store.download(extension_id)

        with tempfile.TemporaryFile() as temp:
            temp.write(download)
            temp.seek(0)
            extract_zip(temp, destination)
