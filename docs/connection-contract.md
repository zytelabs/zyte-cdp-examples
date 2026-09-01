# Connection contract

Zyte Browser exposes a browser-level Chrome DevTools Protocol endpoint at
`https://browser.zyte.com`.

## Authentication

Use the Zyte API key as the HTTP Basic username with an empty password:

```text
Authorization: Basic base64(ZYTE_API_KEY + ":")
```

Clients commonly connect in two steps:

1. Send an authenticated `GET https://browser.zyte.com/json/version`.
2. Follow the redirect to the session host with the same authorization header.
3. Read `webSocketDebuggerUrl` and open it with the same authorization header.

Some clients can discover the WebSocket endpoint while connecting, but that is
only safe here when they preserve authorization across the cross-host redirect.
The examples perform discovery explicitly when a client's built-in discovery
does not meet that requirement.

Generic HTTP clients may remove `Authorization` when a redirect changes hosts.
When discovery is manual, disable automatic redirects and reapply the header to
each HTTPS redirect target under `browser.zyte.com`. Reject redirects to other
hosts before forwarding credentials. Never print the redirect target because it
identifies the browser session.

Do not pass a page endpoint such as `/devtools/page/...` to a browser-level
connection API.

## Browser state

CDP attachment exposes the existing default browser context. A client should:

- Read the first context returned by the library.
- Create a page in that context when no suitable page exists.
- Close pages it created.
- Send the browser-level `Browser.close` command when finished.

Launch-time options such as proxies, extensions, profiles, and browser flags
cannot be changed after attachment.

Playwright's `browser.close()` only disconnects from a browser attached over
CDP. It does not end the remote Zyte session. See
[`sessions-and-pricing.md`](sessions-and-pricing.md) for cleanup examples.

## Failures

A connection-time `503` is transient. Retry the complete connection with
bounded exponential backoff. Once connected, treat a closed WebSocket as an
expired session and start a new browser session rather than trying to reuse old
page or element handles.

Keep a single MCP or CLI session alive across related actions. Snapshot element
references belong to that session and may not survive reconnection.
