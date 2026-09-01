import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright

from _connection import close_through_cdp, connect


with sync_playwright() as playwright:
    browser, context, browser_session = connect(playwright)
    page = None
    try:
        page = context.new_page()
        page.goto("https://quotes.toscrape.com/")
        print(f"Contexts in attached browser: {len(browser.contexts)}")
        print(f"Pages in existing context: {len(context.pages)}")
    finally:
        if page is not None:
            page.close()
        if browser.is_connected():
            close_through_cdp(browser_session)
            print("Sent Browser.close through CDP")
