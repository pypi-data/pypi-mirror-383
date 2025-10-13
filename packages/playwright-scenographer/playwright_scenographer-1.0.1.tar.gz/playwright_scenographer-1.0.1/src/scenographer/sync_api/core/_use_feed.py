from scenographer._shared.core._browser_storage import BrowserStorage
from scenographer.sync_api.core._browser_feed import BrowserFeed
from scenographer.sync_api.core._web_store import WebStore


def use_feed(storage: BrowserStorage, store: WebStore) -> BrowserFeed:
    """
    Creates a browser feed to configure extensions.

    Parameters
    ----------
    storage : BrowserStorage
        Browser storage.
    store : WebStore
        Web Store.

    Returns
    -------
    BrowserFeed
        Browser feed.
    """

    return BrowserFeed(storage, store)
