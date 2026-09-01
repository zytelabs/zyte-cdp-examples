# TypeScript with puppeteer-core

Connects to Zyte's remote browser over CDP. The same Basic authorization header is sent to `/json/version` and the WebSocket handshake. No local browser is installed.

Requires Node.js 22.12 or newer.

```sh
npm install
npm run build
ZYTE_API_KEY=your_api_key npm start
```

Unlike Playwright, Puppeteer's `browser.close()` sends the CDP `Browser.close` command, so it ends the remote Zyte session immediately; no separate cleanup command is needed.
