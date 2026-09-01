# Troubleshooting

## Authentication fails

Check that `ZYTE_API_KEY` is set in the process running the example. Basic authentication uses the API key as the username and an empty password. The encoded input must include the trailing colon.

Authentication must reach both the `/json/version` discovery request and the WebSocket handshake. Generic HTTP clients often remove `Authorization` when redirected to another host. Follow redirects manually and reapply the header, as the direct-client examples do.

Do not print the authorization header or discovered `webSocketDebuggerUrl` while debugging. Both grant access to the browser session.

## Connection returns 403

Confirm that the account has a subscription, or a pay-as-you-go spending limit, and has completed business verification. CDP is not available on free trials.

## Connection returns 503

A connection-time `503` can mean that no browser is currently available. Retry the complete connection with bounded exponential backoff. Do not retry individual commands forever after a WebSocket closes.

## No browser context exists

Zyte Browser exposes an existing default context. Read the first context returned by the client and create pages inside it. Do not request a new incognito or persistent context.

## The session remains active after the script exits

Playwright's `browser.close()` disconnects from a browser attached over CDP. Send `Browser.close` through a browser CDP session to end the Zyte session before its TTL. See [sessions and pricing](sessions-and-pricing.md).

## Browser options have no effect

Proxy settings, extensions, profiles, browser flags, and other launch-time options cannot be changed after connecting. Use Zyte endpoint query parameters for `proxy_region`, `proxy_type`, and `ttl`.

## Selenium cannot connect

The endpoint speaks browser-level CDP. It is not a Selenium Remote WebDriver or WebDriver BiDi endpoint. Use a CDP client that can authenticate both discovery and the WebSocket handshake.

## A page handle stops working

Remote sessions expire at their configured TTL. After the WebSocket closes, start a new session and reacquire pages, locators, and CDP sessions. Handles from the old browser cannot be reused.
