import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright

from _connection import connected_browser


with sync_playwright() as playwright:
    with connected_browser(playwright) as (_, context):
        page = context.new_page()
        session = context.new_cdp_session(page)
        try:
            page.goto("https://quotes.toscrape.com/")
            result = session.send(
                "Runtime.evaluate",
                {"expression": "document.querySelectorAll('.quote').length"},
            )
            print(f"Quote count from Runtime.evaluate: {result['result']['value']}")
        finally:
            session.detach()
            page.close()
