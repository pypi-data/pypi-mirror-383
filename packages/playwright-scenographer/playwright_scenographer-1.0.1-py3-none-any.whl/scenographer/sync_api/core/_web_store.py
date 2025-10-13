from abc import ABC, abstractmethod


class WebStore(ABC):
    """
    Represent a web store for WebExtensions.
    """

    @abstractmethod
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
        pass
