# Compatibility

This repository only includes integrations that can authenticate CDP discovery
and the WebSocket handshake without putting the API key in source code.

## Included

| Client | Authenticated discovery | WebSocket headers | Status |
| --- | --- | --- | --- |
| Puppeteer for Node.js | Yes | Yes | Included |
| Playwright for Python | Yes | Yes | Included |
| Playwright for Java | Yes | Yes | Included |
| Playwright for .NET | Yes | Yes | Included |
| Playwright CLI | Yes | Yes | Included |
| Playwright MCP | Yes | Yes | Included |
| Chrome DevTools MCP | Manual, in `launch.sh` | Yes | Included |
| Browser Use | Yes | Yes | Included |

## Good next additions

- Vercel AI SDK, LangGraph, PydanticAI, Google ADK, CrewAI, and AutoGen can all
  consume the existing MCP launchers. Add full examples only when they
  demonstrate more than another copy of the same MCP configuration.

## Deferred

### agent-browser

`agent-browser --cdp` accepts a local port or a WebSocket URL. Its documented
`--headers` option sets origin-scoped page headers, not CDP handshake headers,
and its browser-provider plugin response currently contains a CDP URL but no
connection headers. A Zyte example would need upstream handshake-header support
or a local credential-forwarding bridge. Neither should be hidden in a basic
example.

### Go chromedp

`chromedp.NewRemoteAllocator` discovers a browser URL, but its standard HTTP and
WebSocket transports do not expose the connection-header hooks required here.
A future Go example should use a reviewed authenticated transport rather than
embedding the API key in a URL.

### Selenium

Selenium Remote expects a WebDriver server. A browser CDP WebSocket is not a
Selenium Grid endpoint. WebDriver BiDi is also a separate protocol negotiated
through a WebDriver session.

### Stagehand

Current Stagehand releases depend on extension/runtime setup when attaching to
an existing browser. That is not a generic CDP-only example.
