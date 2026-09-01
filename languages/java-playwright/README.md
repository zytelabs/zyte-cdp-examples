# Java with Playwright

Connects to Zyte's remote browser over CDP. The same Basic authorization header is sent to `/json/version` and the WebSocket handshake. No local browser is installed.

Requires JDK 17 or newer and Maven.

```sh
mvn compile
ZYTE_API_KEY=your_api_key mvn exec:java
```

Do not run Playwright's browser installation CLI; this example only uses the remote browser.

The cleanup code sends the raw `Browser.close` command so the remote session
ends before its TTL.
