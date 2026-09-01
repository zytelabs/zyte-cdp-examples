# Playwright MCP launcher

`launch.sh` connects the pinned Playwright MCP server to Zyte Browser. It refuses to run without `ZYTE_API_KEY`, resolves its local installation independently of the client's working directory, and never puts the generated Basic credential in process arguments.

## Install

Requires Node.js 18 or newer.

```sh
npm install
export ZYTE_API_KEY="your-api-key"
```

The launcher uses `@playwright/mcp@0.0.79` from `node_modules`. It does not use `npx` or download code when an MCP client starts. Each MCP process attaches to the remote browser's existing default context, omits image responses, blocks service workers, and limits normal requests to `https://quotes.toscrape.com`. Edit `PLAYWRIGHT_MCP_ALLOWED_ORIGINS` in `launch.sh` for another target. This origin setting reduces accidental navigation but is not a security boundary and does not prevent redirects.

Set `ZYTE_BROWSER_ENDPOINT` to change the endpoint parameters, for example `https://browser.zyte.com/?ttl=900&proxy_region=GB`. The default requests a 600-second TTL.

## Configure a client

Copy the matching object from `configs/` into the client's configuration, then replace `/absolute/path/to/cdp` with this checkout's absolute path. Keep `ZYTE_API_KEY` in the environment that starts the client.

| Client | Template destination |
| --- | --- |
| Claude Code | Project `.mcp.json` |
| Cursor | Project `.cursor/mcp.json` |
| OpenCode | Project or user `opencode.json` |
| VS Code | Project `.vscode/mcp.json` |

Restart the client after changing its configuration. Claude Code asks for approval for project MCP servers. OpenCode also reads its MCP configuration only at startup.

Try this prompt after the server connects:

```text
Open https://quotes.toscrape.com, report the page title, then close the browser.
```

The MCP client owns the stdio process. Stopping or restarting the server closes stdin and terminates Playwright MCP. The launcher then reconnects to the same browser and sends raw CDP `Browser.close`. It requests a 600-second TTL as a fallback because an MCP task can exceed the 60-second default.

Playwright MCP is not a security boundary. Review tool calls and do not use an API key with broader access than the task needs.
