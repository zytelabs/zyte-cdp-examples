import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright

from _connection import connected_browser

query = urlencode(
    {
        "proxy_region": os.environ.get("PROXY_REGION", "GB"),
        "proxy_type": os.environ.get("PROXY_TYPE", "datacenter"),
        "ttl": os.environ.get("SESSION_TTL", "60"),
    }
)
endpoint = f"https://browser.zyte.com/?{query}"

with sync_playwright() as playwright:
    with connected_browser(playwright, endpoint) as (_, context):
        page = context.new_page()
        try:
            response = page.goto("https://httpbin.org/ip")
            if response is None:
                raise RuntimeError("Navigation returned no response")
            origin = json.loads(page.locator("body").inner_text())["origin"]
            print(f"Remote browser egress IP: {origin}")
            print(f"Requested proxy region: {os.environ.get('PROXY_REGION', 'GB')}")
            print(f"Requested proxy type: {os.environ.get('PROXY_TYPE', 'datacenter')}")
        finally:
            page.close()
