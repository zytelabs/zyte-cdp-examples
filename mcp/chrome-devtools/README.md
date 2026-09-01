# Chrome DevTools MCP launcher

`launch.sh` connects the pinned Chrome DevTools MCP server to Zyte Browser. Chrome DevTools MCP exposes Chrome-native tools beyond page automation: network request inspection, performance tracing, CPU and heap profiling, and script evaluation over the DevTools protocol.

The launcher performs the authenticated `/json/version` discovery first, then starts the server with `--wsEndpoint` and `--wsHeaders`. It refuses to run without `ZYTE_API_KEY`, resolves its local installation independently of the client's working directory, and never prints the API key, authorization header, or discovered WebSocket URL.

## Install

Requires Node.js 18 or newer.

```sh
npm install
export ZYTE_API_KEY="your-api-key"
```

The launcher uses `chrome-devtools-mcp@1.8.0` from `node_modules`. It does not use `npx` or download code when an MCP client starts.

## Configure a client

Copy the matching object from `configs/` into the client's configuration, then replace `/absolute/path/to/cdp` with this checkout's absolute path. Keep `ZYTE_API_KEY` in the environment that starts the client.

| Client | Template destination |
| --- | --- |
| Claude Code | Project `.mcp.json` |
| Cursor | Project `.cursor/mcp.json` |
| OpenCode | Project or user `opencode.json` |
| VS Code | Project `.vscode/mcp.json` |

Restart the client after changing its configuration. The server runs on stdio. When it stops, the launcher reconnects to the same browser and sends `Browser.close`. A 600-second TTL provides a fallback if cleanup cannot reconnect. Override it with `ZYTE_BROWSER_TTL`, and set `ZYTE_BROWSER_ENDPOINT` to change other endpoint parameters, for example `https://browser.zyte.com/?proxy_region=GB`.

Try this prompt after the server connects:

```text
Open https://quotes.toscrape.com/js/, count the rendered quotes, then list the network requests for the page.
```

## Launcher behavior

- Retries discovery with backoff; a persistent `503` means no browser is currently available.
- Reapplies authorization only to HTTPS redirects under `browser.zyte.com`.
- Disables usage statistics, CrUX field-data lookups, and returns network headers redacted to limit captured traffic in tool output.
- Passes any extra arguments through to the server: append them in the client config if needed (for example `--blockedUrlPattern`, since `--allowedUrlPattern` needs Chrome 149+).

## Credential exposure note

Unlike the Playwright MCP launcher, which passes headers through environment variables, chrome-devtools-mcp 1.8.0 accepts the WebSocket endpoint and headers only as command-line arguments. A local user able to inspect process arguments may read the live session URL and API key while the server runs. Use this launcher only on a single-user machine or in an isolated container, or wait for upstream environment-variable support before using it on shared hosts.

Chrome DevTools MCP is not a security boundary. Review tool calls and do not use an API key with broader access than the task needs.
