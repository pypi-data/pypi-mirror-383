"""
Playwright enables reliable end-to-end testing for modern web apps.
This package brings in additional features to enable using WebExtensions.
"""

from scenographer._shared.core._browser_storage import BrowserStorage

from scenographer._shared.core._default_storage import DEFAULT_STORAGE

from scenographer._shared.core._use_web_extensions import use_web_extensions

from scenographer.async_api.core._browser_feed import BrowserFeed
from scenographer.async_api.core._web_store import WebStore

from scenographer.async_api.core._use_feed import use_feed

from scenographer.async_api.stores._chrome import ChromeWebStore
from scenographer.async_api.stores._local import LocalWebStore

from scenographer.async_api.stores._stores import CHROME_STORE
from scenographer.async_api.stores._stores import LOCAL_STORE
