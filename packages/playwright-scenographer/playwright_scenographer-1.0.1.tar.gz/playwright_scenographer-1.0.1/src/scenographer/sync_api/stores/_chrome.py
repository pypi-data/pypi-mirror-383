import requests

from scenographer.sync_api.core._web_store import WebStore


class ChromeWebStore(WebStore):
    """
    Represents a web store using Chrome Web Store.
    """

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

        PROD = "chromium"
        PROD_VERSION = "133.0"

        url = f"https://clients2.google.com/service/update2/crx" \
            f"?response=redirect" \
            f"&prod={PROD}" \
            f"&prodversion={PROD_VERSION}" \
            f"&acceptformat=crx3" \
            f"&x=id%3D{extension_id}%26installsource%3Dondemand%26uc"

        response = requests.get(url)

        return response.content
