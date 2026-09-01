# Sessions and pricing

A CDP connection controls one browser with one IP address and one cookie jar for the connection's lifetime. State persists across pages in that connection, but it cannot be resumed from another CDP connection or shared with a Zyte API HTTP or browser request.

## Session duration

Set the time-to-live with the `ttl` query parameter:

```text
https://browser.zyte.com/?ttl=600
```

The default is 60 seconds. Accepted values range from 15 to 3600 seconds.

A session starts when the CDP client connects. It ends when Zyte receives the raw `Browser.close` CDP command or when the TTL expires. A dropped client connection does not immediately end the remote session.

Puppeteer's `browser.close()` sends `Browser.close`. Playwright's `browser.close()` disconnects the client from an attached browser, so the Playwright examples send the CDP command explicitly:

```python
session = browser.new_browser_cdp_session()
session.send("Browser.close")
```

Put this command in cleanup code so errors do not leave the browser reserved until its TTL.

## Billing

Zyte bills a started session according to the tier of the domain used in the first `page.goto()` call. The consumed tier units are the greater of:

- The number of `page.goto()` calls.
- The session duration divided into 15-second intervals and rounded up.

A session that never starts is not billed. Residential sessions also have a bandwidth allowance per unit and may incur per-GB overage charges.

Prices and billing behavior can change. Check the [official CDP pricing documentation](https://docs.zyte.com/zyte-api/usage/cdp.html#pricing) before estimating production costs.

## Choosing another Zyte API mode

Use [browser requests](https://docs.zyte.com/zyte-api/usage/browser.html) when you need a rendered page or a fixed action sequence rather than a live browser connection. Browser requests also support Zyte API client-managed and server-managed sessions. CDP sessions do not support those session APIs.
