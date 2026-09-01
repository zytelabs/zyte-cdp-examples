# Python with Playwright

Connects to Zyte's remote browser over CDP. The same Basic authorization header is sent to `/json/version` and the WebSocket handshake. No local browser is installed.

Requires Python 3.10 or newer.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
ZYTE_API_KEY=your_api_key python main.py
```

Do not run `playwright install`; this example only uses the remote browser.

The cleanup code sends the raw `Browser.close` command. Playwright's
`browser.close()` only disconnects from an attached CDP browser and would leave
the remote session running until its TTL.
