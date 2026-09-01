import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright

from _connection import connected_browser


with sync_playwright() as playwright:
    with connected_browser(playwright) as (_, context):
        page = context.new_page()
        try:
            context.add_cookies(
                [
                    {
                        "name": "howto",
                        "value": "playwright",
                        "url": "https://httpbin.org/",
                        "sameSite": "Lax",
                    }
                ]
            )
            page.goto("https://httpbin.org/cookies")
            cookie_names = [
                cookie["name"] for cookie in context.cookies("https://httpbin.org/")
            ]
            print(f"Cookie names in context: {', '.join(cookie_names)}")
            received = "playwright" in page.locator("body").inner_text()
            print(f"Server received howto cookie: {received}")
        finally:
            page.close()
