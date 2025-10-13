from scenographer.sync_api.core._web_store import WebStore
from scenographer.sync_api.stores._chrome import ChromeWebStore
from scenographer.sync_api.stores._local import LocalWebStore

CHROME_STORE: WebStore = ChromeWebStore()
LOCAL_STORE: WebStore = LocalWebStore()
