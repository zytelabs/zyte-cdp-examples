import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright

from _connection import connected_browser


with sync_playwright() as playwright:
    with connected_browser(playwright) as (_, context):
        page = context.new_page()
        try:
            page.goto("https://quotes.toscrape.com/search.aspx")
            page.get_by_label("Author").select_option("Albert Einstein")
            # Choosing an author makes the page submit itself and reload
            # with that author's tags; select_option retries until the
            # requested option exists, so no explicit wait is needed.
            page.get_by_label("Tag").select_option("world")
            page.get_by_role("button", name="Search").click()
            result = page.locator(".quote .content").first
            result.wait_for()
            print(f"First result: {result.inner_text()}")
        finally:
            page.close()
