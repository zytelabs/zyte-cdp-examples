import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright

from _connection import connected_browser


with sync_playwright() as playwright:
    with connected_browser(playwright) as (_, context):
        page = context.new_page()
        try:
            page.goto("https://quotes.toscrape.com/js/")
            quotes = page.locator(".quote")
            quotes.first.wait_for()
            print(f"Rendered quotes: {quotes.count()}")
            print(f"First quote: {quotes.first.locator('.text').inner_text()}")
        finally:
            page.close()
