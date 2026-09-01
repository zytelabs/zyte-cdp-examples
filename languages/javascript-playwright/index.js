const { chromium } = require("playwright");

const endpoint = "https://browser.zyte.com";
const apiKey = process.env.ZYTE_API_KEY;

if (!apiKey) {
  throw new Error("ZYTE_API_KEY is required");
}

const headers = {
  Authorization: `Basic ${Buffer.from(`${apiKey}:`).toString("base64")}`,
};

async function discoverWebSocketUrl() {
  let discoveryUrl = new URL("/json/version", endpoint);

  for (let redirects = 0; redirects < 5; redirects += 1) {
    const response = await fetch(discoveryUrl, {
      headers,
      redirect: "manual",
    });

    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get("location");
      if (!location) {
        throw new Error("CDP discovery redirect has no location");
      }

      discoveryUrl = new URL(location, discoveryUrl);
      if (
        discoveryUrl.protocol !== "https:" ||
        (discoveryUrl.hostname !== "browser.zyte.com" &&
          !discoveryUrl.hostname.endsWith(".browser.zyte.com"))
      ) {
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
    return webSocketDebuggerUrl;
  }

  throw new Error("CDP discovery exceeded the redirect limit");
}

async function main() {
  const websocketUrl = await discoverWebSocketUrl();
  const browser = await chromium.connectOverCDP(websocketUrl, { headers });

  try {
    const context = browser.contexts()[0];
    if (!context) {
      throw new Error("The CDP browser has no default context");
    }

    const page = await context.newPage();
    await page.goto("https://quotes.toscrape.com/scroll");
    await page.evaluate(async () => {
      let quoteCount = 0;
      while (true) {
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise((resolve) => setTimeout(resolve, 500));
        const newCount = document.querySelectorAll(".quote").length;
        if (newCount === quoteCount) break;
        quoteCount = newCount;
      }
    });

    console.log(`Quotes: ${await page.locator(".quote").count()}`);
    await page.close();
  } finally {
    if (browser.isConnected()) {
      const cdp = await browser.newBrowserCDPSession();
      await cdp.send("Browser.close");
    }
  }
}

main().catch((error) => {
  // Playwright errors can embed the WebSocket URL, which identifies the
  // browser session, so redact it before printing.
  const detail = String(error?.stack ?? error);
  console.error(detail.replace(/wss:\/\/\S+/g, "wss://[redacted]"));
  process.exitCode = 1;
});
