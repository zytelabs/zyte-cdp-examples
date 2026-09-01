import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import Response, sync_playwright

from _connection import connected_browser


def show_response(response: Response) -> None:
    url = urlsplit(response.url)
    print(f"{response.status} {response.request.resource_type} {url.netloc}{url.path}")


with sync_playwright() as playwright:
    with connected_browser(playwright) as (_, context):
        page = context.new_page()
        try:
            page.on("response", show_response)
            page.goto("https://quotes.toscrape.com/")
            page.wait_for_load_state("networkidle")
        finally:
            page.close()
