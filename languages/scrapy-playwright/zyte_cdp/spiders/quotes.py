from scrapy import Request, Spider
from scrapy_playwright.page import PageMethod

SCROLL_TO_BOTTOM = """async () => {
    let quoteCount = 0;
    while (true) {
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise((resolve) => setTimeout(resolve, 500));
        const newCount = document.querySelectorAll(".quote").length;
        if (newCount === quoteCount) break;
        quoteCount = newCount;
    }
}"""


class QuotesSpider(Spider):
    name = "quotes"

    async def start(self):
        yield Request(
            "https://quotes.toscrape.com/scroll",
            callback=self.parse,
            errback=self.close_browser_on_error,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("evaluate", SCROLL_TO_BOTTOM),
                ],
            },
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        try:
            for quote in response.css(".quote"):
                yield {
                    "text": quote.css(".text::text").get(),
                    "author": quote.css(".author::text").get(),
                }
        finally:
            await self.close_remote_browser(page)

    async def close_browser_on_error(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page is not None:
            await self.close_remote_browser(page)
        self.logger.error("Request failed")

    @staticmethod
    async def close_remote_browser(page):
        cdp = await page.context.new_cdp_session(page)
        await cdp.send("Browser.close")
