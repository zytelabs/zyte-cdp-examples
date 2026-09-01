import { chromium } from "playwright-core";

const apiKey = process.env.ZYTE_API_KEY;
if (!apiKey) throw new Error("ZYTE_API_KEY is required");

const headers = {
  Authorization: `Basic ${Buffer.from(`${apiKey}:`).toString("base64")}`,
};

async function discover() {
  const endpoint = new URL(process.env.ZYTE_BROWSER_ENDPOINT);
  endpoint.pathname = `${endpoint.pathname.replace(/\/$/, "")}/json/version`;
  let url = endpoint;

  for (let redirects = 0; redirects < 5; redirects += 1) {
    const response = await fetch(url, { headers, redirect: "manual" });
    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get("location");
      if (!location) throw new Error("CDP discovery redirect has no location");
      url = new URL(location, url);
      const trusted =
        url.hostname === "browser.zyte.com" ||
        url.hostname.endsWith(".browser.zyte.com");
      if (url.protocol !== "https:" || !trusted) {
        throw new Error("CDP discovery refused an untrusted redirect");
      }
      continue;
    }
    if (!response.ok) {
      throw new Error(`CDP discovery failed with HTTP ${response.status}`);
    }
    const { webSocketDebuggerUrl } = await response.json();
    if (!webSocketDebuggerUrl) {
      throw new Error("CDP discovery response has no webSocketDebuggerUrl");
    }
    process.stdout.write(webSocketDebuggerUrl);
    return;
  }
  throw new Error("CDP discovery exceeded the redirect limit");
}

async function close() {
  const websocketUrl = process.env.ZYTE_BROWSER_WS_URL;
  if (!websocketUrl) throw new Error("ZYTE_BROWSER_WS_URL is required");
  const browser = await chromium.connectOverCDP(websocketUrl, { headers });
  const session = await browser.newBrowserCDPSession();
  await session.send("Browser.close");
}

if (process.argv[2] === "discover") {
  await discover();
} else if (process.argv[2] === "close") {
  await close();
} else {
  throw new Error("Expected discover or close");
}
