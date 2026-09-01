import asyncio
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
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
    directory = Path(__file__).resolve().parent
    server_binary = directory / "node_modules" / ".bin" / "playwright-mcp"
    if not server_binary.is_file():
        raise RuntimeError(f"Playwright MCP is not installed; run npm install in {directory}")

    api_key = os.environ.get("ZYTE_API_KEY")
    if not api_key:
        raise RuntimeError("ZYTE_API_KEY is required")
    basic_token = base64.b64encode(f"{api_key}:".encode()).decode()
    headers = {"Authorization": f"Basic {basic_token}"}
    websocket_url = discover_websocket_url(headers)
    server_env = os.environ.copy()
    server_env.update(
        {
            "PLAYWRIGHT_MCP_CDP_ENDPOINT": websocket_url,
            "PLAYWRIGHT_MCP_CDP_HEADERS": f"Authorization: Basic {basic_token}",
            "PLAYWRIGHT_MCP_IMAGE_RESPONSES": "omit",
        }
    )

    # One stdio process stays connected for the whole agent run.
    try:
        async with MCPServerStdio(
            name="Zyte Playwright",
            params={
                "command": str(server_binary),
                "args": [],
                "cwd": str(directory),
                "env": server_env,
            },
            cache_tools_list=True,
        ) as server:
            agent = Agent(
                name="Browser agent",
                model="gpt-5-mini",
                instructions=(
                    "Use Playwright MCP for browser work. Visit only "
                    "https://quotes.toscrape.com, "
                    "report the page title, and call browser_close before finishing."
                ),
                mcp_servers=[server],
            )
            result = await Runner.run(agent, "Check the quotes page title.", max_turns=10)
            print(result.final_output)
    finally:
        await close_remote_browser(websocket_url, headers)


if __name__ == "__main__":
    asyncio.run(main())
