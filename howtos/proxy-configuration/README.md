# Proxy configuration

Zyte Browser configures its network proxy before exposing the CDP session. Set `proxy_region`, `proxy_type`, and `ttl` as query parameters on the connection endpoint. Playwright's own `proxy` option cannot be changed after attaching to the existing context.

This example requests a British datacenter proxy with a 60-second session, then checks the remote browser's public egress address. Override the values with `PROXY_REGION`, `PROXY_TYPE`, and `SESSION_TTL`.

From the repository root, after installing `howtos/requirements.txt`:

```sh
ZYTE_API_KEY=your_api_key python howtos/proxy-configuration/main.py
```

For example:

```sh
PROXY_REGION=DE PROXY_TYPE=residential SESSION_TTL=120 \
  ZYTE_API_KEY=your_api_key python howtos/proxy-configuration/main.py
```

`proxy_region` accepts a two-letter country code. `proxy_type` is `datacenter` or `residential`, and `ttl` ranges from 15 to 3600 seconds. The output contains the remote browser's egress IP, not the machine's direct browser traffic.
