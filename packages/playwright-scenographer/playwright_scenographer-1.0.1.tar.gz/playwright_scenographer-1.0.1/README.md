# Scenographer

[![Build](https://github.com/scenographer/scenographer-python/actions/workflows/ci.yml/badge.svg)](https://github.com/scenographer/scenographer-python/actions/workflows/ci.yml)

WebExtension for Playwright for Python

## API Reference

```python
from playwright.async_api import async_playwright
from scenographer.async_api import (
    CHROME_STORE,
    DEFAULT_STORAGE,
    use_feed,
    use_web_extensions
)

# Installing AdBlock
# https://chrome.google.com/webstore/detail/gighmmpiobklfepjocnamgkkbiglidom

await use_feed(DEFAULT_STORAGE, CHROME_STORE).install_extension("gighmmpiobklfepjocnamgkkbiglidom")

async with async_playwright() as playwright:
    args = use_web_extensions()

    chromium = playwright.chromium
    browser = await chromium.launch_persistent_context(
        DEFAULT_STORAGE.get_base_directory(),
        args=args,
        headless=False
    )

    page = browser.pages[0]
    await page.goto("chrome://extensions")
```
