# Zyte Browser CDP examples

Runnable examples for controlling [Zyte Browser](https://www.zyte.com/zyte-api/headless-browser/) through the Chrome DevTools Protocol (CDP). Your Playwright or Puppeteer script runs locally while the Chromium browser, proxy routing, and access handling run on Zyte's infrastructure.

Use CDP for branching workflows, multi-step interactions, network inspection, and existing browser automation scripts. For a single rendered page or a fixed sequence of actions, a [Zyte API browser request](https://docs.zyte.com/zyte-api/usage/browser.html) is usually simpler.

## Before you start

CDP access requires a Zyte API subscription, or a pay-as-you-go plan with a spending limit, and completed business verification. It is not available on free trials. See the [CDP requirements](https://docs.zyte.com/zyte-api/usage/cdp.html#requirements).

Create an API key in the [Zyte dashboard](https://app.zyte.com/o/zyte-api/api-access), then export it:

```sh
export ZYTE_API_KEY="your-api-key"
```

The examples install client libraries only. Do not install or download a local browser.

## Start here

The shortest example is [Python with Playwright](languages/python-playwright):

```sh
cd languages/python-playwright
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
ZYTE_API_KEY=your_api_key python main.py
```

It connects to `https://browser.zyte.com/`, opens a JavaScript-rendered page, extracts data, calls raw CDP, and explicitly ends the remote browser session.

## Language examples

| Language | Client | Example |
| --- | --- | --- |
| Python | Playwright | [`languages/python-playwright`](languages/python-playwright) |
| JavaScript | Playwright | [`languages/javascript-playwright`](languages/javascript-playwright) |
| TypeScript | Puppeteer | [`languages/typescript-puppeteer`](languages/typescript-puppeteer) |
| Java | Playwright | [`languages/java-playwright`](languages/java-playwright) |
| C# | Playwright | [`languages/csharp-playwright`](languages/csharp-playwright) |
| Python | Scrapy and scrapy-playwright | [`languages/scrapy-playwright`](languages/scrapy-playwright) |

## How-to guides

The how-tos use Python and Playwright so each guide can focus on one browser task. Install their shared dependency once:

```sh
python -m pip install -r howtos/requirements.txt
```

| Task | What it demonstrates |
| --- | --- |
| [Dynamic content](howtos/dynamic-content) | Wait for and extract JavaScript-rendered content |
| [Forms](howtos/forms) | Select dependent form options, submit, and wait for the result |
| [Screenshots](howtos/screenshots) | Capture an element to a local image |
| [Network inspection](howtos/network-inspection) | Observe response status, type, and URL |
| [Cookies](howtos/cookies) | Set and read cookies in the existing context |
| [Proxy configuration](howtos/proxy-configuration) | Select proxy region, IP type, and session TTL |
| [Raw CDP](howtos/raw-cdp) | Send a CDP command not wrapped by Playwright |
| [Session lifecycle](howtos/session-lifecycle) | End a remote session with `Browser.close` |

## Agents and MCP

| Integration | What it demonstrates |
| --- | --- |
| [Playwright CLI](agents/playwright-cli) | A browser CLI suitable for coding-agent skills |
| [Browser Use](agents/browser-use) | An autonomous Python browser agent |
| [OpenAI Agents SDK](agents/openai-agents) | A persistent Playwright MCP subprocess |
| [Playwright MCP](mcp/playwright) | Configurations for MCP clients |
| [Chrome DevTools MCP](mcp/chrome-devtools) | Network and performance tools over MCP |

Agent examples also require the model credentials listed in their own READMEs. Keep model credentials separate from `ZYTE_API_KEY`.

## Connection rules

- Authenticate with HTTP Basic auth using the API key as the username and an empty password: `Basic base64(ZYTE_API_KEY + ":")`.
- Send authentication during CDP discovery and the WebSocket handshake.
- Use the browser's existing default context. Launch-time browser and context options cannot be changed after attachment.
- Configure `proxy_region`, `proxy_type`, and `ttl` on the CDP endpoint before connecting.
- Treat API keys and discovered WebSocket URLs as credentials. Do not log either value.
- End Playwright sessions by sending the raw `Browser.close` CDP command. Playwright's `browser.close()` only disconnects from an attached CDP browser.

Read [authentication and connection](docs/connection-contract.md), [sessions and pricing](docs/sessions-and-pricing.md), [compatibility](docs/compatibility.md), [troubleshooting](docs/troubleshooting.md), and [security](SECURITY.md) before adding a new client.

## Development

Each example owns its dependencies so developers can copy one directory without adopting a repository-wide build system. CI compiles and syntax-checks examples without starting paid browser or model sessions.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the local checks and requirements for new examples.

## License

Apache License 2.0. See [LICENSE](LICENSE).
