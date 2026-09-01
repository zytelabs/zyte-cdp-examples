import os

from w3lib.http import basic_auth_header

api_key = os.environ.get("ZYTE_API_KEY")
if not api_key:
    raise RuntimeError("ZYTE_API_KEY is required")

BOT_NAME = "zyte_cdp"
SPIDER_MODULES = ["zyte_cdp.spiders"]
NEWSPIDER_MODULE = "zyte_cdp.spiders"

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_CDP_URL = "https://browser.zyte.com/"
PLAYWRIGHT_CDP_KWARGS = {
    "headers": {
        "Authorization": basic_auth_header(api_key, "").decode("ascii"),
    },
}
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_BROWSER_PROVIDER = "zyte_cdp.provider.ExistingContextProvider"
# The spider ends the remote session with Browser.close; a restart would
# silently start a new billed session.
PLAYWRIGHT_RESTART_DISCONNECTED_BROWSER = False

ROBOTSTXT_OBEY = True
LOG_LEVEL = "INFO"
