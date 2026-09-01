import asyncio
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from browser_use import Agent, Browser, ChatOpenAI
from dotenv import load_dotenv
from playwright.async_api import async_playwright


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def discover_websocket_url(headers: dict[str, str]) -> str:
    opener = urllib.request.build_opener(NoRedirect)
    url = "https://browser.zyte.com/json/version?ttl=600"
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
            parsed = urllib.parse.urlparse(url)
            hostname = parsed.hostname or ""
            if parsed.scheme != "https" or not (
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


async def close_remote_browser(websocket_url: str, headers: dict[str, str]) -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(
            websocket_url, headers=headers
        )
        session = await browser.new_browser_cdp_session()
        await session.send("Browser.close")


async def main() -> None:
    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required")
    api_key = os.environ.get("ZYTE_API_KEY")
    if not api_key:
        raise RuntimeError("ZYTE_API_KEY is required")
    basic_token = base64.b64encode(f"{api_key}:".encode()).decode()
    headers = {"Authorization": f"Basic {basic_token}"}

    websocket_url = discover_websocket_url(headers)

    browser = Browser(
        cdp_url=websocket_url,
        headers=headers,
    )
    agent = Agent(
        task=(
            "Open https://quotes.toscrape.com/js/, report the first quote and its author, "
            "then stop. Do not visit any other site."
        ),
        llm=ChatOpenAI(model="gpt-5-mini"),
        browser=browser,
    )

    try:
        history = await agent.run(max_steps=12)
        print(history.final_result())
    finally:
        try:
            await browser.close()
        finally:
            await close_remote_browser(websocket_url, headers)


if __name__ == "__main__":
    asyncio.run(main())
