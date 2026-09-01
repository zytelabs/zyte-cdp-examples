import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager, suppress

from playwright.sync_api import Browser, BrowserContext, CDPSession, Playwright


ENDPOINT = "https://browser.zyte.com/"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _websocket_url(endpoint: str, headers: dict[str, str]) -> str:
    opener = urllib.request.build_opener(_NoRedirect)
    parsed_endpoint = urllib.parse.urlsplit(endpoint)
    discovery_path = parsed_endpoint.path.rstrip("/") + "/json/version"
    url = urllib.parse.urlunsplit(parsed_endpoint._replace(path=discovery_path))

    for _ in range(5):
        request = urllib.request.Request(url, headers=headers)
        try:
            response = opener.open(request)
        except urllib.error.HTTPError as error:
            with error:
                if error.code not in {301, 302, 303, 307, 308}:
                    raise
                location = error.headers.get("Location")
            if not location:
                raise RuntimeError("CDP discovery redirect has no Location header")
            url = urllib.parse.urljoin(url, location)
            parsed_url = urllib.parse.urlparse(url)
            hostname = parsed_url.hostname or ""
            if parsed_url.scheme != "https" or not (
                hostname == "browser.zyte.com"
                or hostname.endswith(".browser.zyte.com")
            ):
                raise RuntimeError("CDP discovery refused an untrusted redirect")
            continue

        with response:
            websocket_url = json.load(response).get("webSocketDebuggerUrl")
        if not websocket_url:
            raise RuntimeError("CDP discovery response has no webSocketDebuggerUrl")
        return websocket_url

    raise RuntimeError("CDP discovery exceeded the redirect limit")


def connect(
    playwright: Playwright, endpoint: str = ENDPOINT
) -> tuple[Browser, BrowserContext, CDPSession]:
    api_key = os.environ.get("ZYTE_API_KEY")
    if not api_key:
        raise RuntimeError("ZYTE_API_KEY is required")

    token = base64.b64encode(f"{api_key}:".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}
    browser = playwright.chromium.connect_over_cdp(
        _websocket_url(endpoint, headers), headers=headers
    )
    try:
        session = browser.new_browser_cdp_session()
        if not browser.contexts:
            close_through_cdp(session)
            raise RuntimeError("The remote browser has no default context")
    except Exception:
        # Disconnect so the local client does not linger; without a CDP
        # session the remote browser still runs until its TTL.
        with suppress(Exception):
            if browser.is_connected():
                browser.close()
        raise
    return browser, browser.contexts[0], session


def close_through_cdp(session: CDPSession) -> None:
    session.send("Browser.close")


@contextmanager
def connected_browser(playwright: Playwright, endpoint: str = ENDPOINT):
    browser, context, session = connect(playwright, endpoint)
    try:
        yield browser, context
    finally:
        if browser.is_connected():
            close_through_cdp(session)
