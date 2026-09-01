from scrapy_playwright.provider import PlaywrightBrowserProvider


class ExistingContextBrowser:
    def __init__(self, browser):
        self.browser = browser

    def __getattr__(self, name):
        return getattr(self.browser, name)

    async def new_context(self, **kwargs):
        if kwargs:
            raise ValueError("Context launch options cannot be used with Zyte CDP")
        if not self.browser.contexts:
            raise RuntimeError("The CDP browser has no default context")
        return self.browser.contexts[0]


class ExistingContextProvider(PlaywrightBrowserProvider):
    async def launch_browser(self):
        browser = await super().launch_browser()
        return ExistingContextBrowser(browser)
