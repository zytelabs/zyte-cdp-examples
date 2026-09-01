import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from playwright.sync_api import sync_playwright


endpoint = "https://browser.zyte.com/"
api_key = os.environ.get("ZYTE_API_KEY")
if not api_key:
    raise RuntimeError("ZYTE_API_KEY is required")
authorization = "Basic " + base64.b64encode(f"{api_key}:".encode()).decode()
headers = {"Authorization": authorization}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, response_headers, newurl):
        return None


opener = urllib.request.build_opener(NoRedirect)
discovery_url = urllib.parse.urljoin(endpoint, "json/version")
websocket_url = None
for _ in range(5):
    request = urllib.request.Request(discovery_url, headers=headers)
    try:
        response = opener.open(request)
    except urllib.error.HTTPError as error:
        with error:
            if error.code not in {301, 302, 303, 307, 308}:
                raise
            location = error.headers.get("Location")
        if not location:
            raise RuntimeError("CDP discovery redirect has no Location header")
        discovery_url = urllib.parse.urljoin(discovery_url, location)
        parsed_url = urllib.parse.urlparse(discovery_url)
        hostname = parsed_url.hostname or ""
        if parsed_url.scheme != "https" or not (
            hostname == "browser.zyte.com"
            or hostname.endswith(".browser.zyte.com")
        ):
            raise RuntimeError("CDP discovery refused an untrusted redirect")
        continue
    with response:
        websocket_url = json.load(response).get("webSocketDebuggerUrl")
    break
else:
    raise RuntimeError("CDP discovery exceeded the redirect limit")

if not websocket_url:
    raise RuntimeError("CDP discovery response has no webSocketDebuggerUrl")

with sync_playwright() as playwright:
    browser = playwright.chromium.connect_over_cdp(websocket_url, headers=headers)
    browser_session = browser.new_browser_cdp_session()
    try:
        if not browser.contexts:
            raise RuntimeError("The CDP browser has no default context")
        context = browser.contexts[0]
        page = context.new_page()
        page.goto("https://quotes.toscrape.com/js/")
        page.wait_for_selector(".quote")

        print(f"Title: {page.title()}")
        print(f"Quotes: {page.locator('.quote').count()}")

        cdp = context.new_cdp_session(page)
        version = cdp.send("Browser.getVersion")
        print(f"Browser: {version['product']}")
        cdp.detach()
        page.close()
    finally:
        if browser.is_connected():
            browser_session.send("Browser.close")
