import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright

from _connection import connected_browser


output = Path(__file__).with_name("quotes.png")

with sync_playwright() as playwright:
    with connected_browser(playwright) as (_, context):
        page = context.new_page()
        try:
            page.goto("https://quotes.toscrape.com/")
            page.locator(".quote").first.screenshot(path=output)
            print(f"Saved {output.name} ({output.stat().st_size} bytes)")
        finally:
            page.close()
