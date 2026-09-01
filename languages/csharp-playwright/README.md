# C# (.NET) with Playwright

Connects to Zyte's remote browser over CDP. The same Basic authorization header is sent to `/json/version` and the WebSocket handshake. No local browser is installed.

Requires the .NET 8 SDK or newer.

```sh
dotnet build
ZYTE_API_KEY=your_api_key dotnet run
```

Do not run Playwright's browser installation CLI; this example only uses the remote browser.

The cleanup code sends the raw `Browser.close` command so the remote session
ends before its TTL.
