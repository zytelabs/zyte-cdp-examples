# JavaScript with Playwright

Connects Playwright to Zyte's remote browser over CDP, attaches to its existing default context, and scrolls a dynamic page until all quotes load. The same Basic authorization header is sent during endpoint discovery and the WebSocket handshake; neither the API key nor the discovered WebSocket URL is printed.

Requires Node.js 20 or newer. No local browser installation is needed.

```sh
npm install
ZYTE_API_KEY=your_api_key npm start
```

The example explicitly sends the CDP `Browser.close` command when it finishes. This is required to end the Zyte browser session and stop billing before its TTL expires; Playwright's `browser.close()` only disconnects from a CDP browser.
