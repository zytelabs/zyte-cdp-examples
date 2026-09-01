import puppeteer from "puppeteer-core";

const endpoint = "https://browser.zyte.com";
const apiKey = process.env.ZYTE_API_KEY;

if (!apiKey) {
  throw new Error("ZYTE_API_KEY is required");
}

const headers = {
  Authorization: `Basic ${Buffer.from(`${apiKey}:`).toString("base64")}`,
};

let discoveryUrl = new URL("/json/version", endpoint);
let response: Response | undefined;
for (let redirects = 0; redirects < 5; redirects++) {
  const candidate = await fetch(discoveryUrl, { headers, redirect: "manual" });
  if (candidate.status < 300 || candidate.status >= 400) {
    response = candidate;
    break;
  }

  const location = candidate.headers.get("location");
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
}
if (!response) {
  throw new Error("CDP discovery exceeded the redirect limit");
}
if (!response.ok) {
  throw new Error(`CDP discovery failed with HTTP ${response.status}`);
}

const { webSocketDebuggerUrl } = (await response.json()) as {
  webSocketDebuggerUrl?: string;
};
if (!webSocketDebuggerUrl) {
  throw new Error("CDP discovery response has no webSocketDebuggerUrl");
}

const browser = await puppeteer.connect({
  browserWSEndpoint: webSocketDebuggerUrl,
  headers,
});

try {
  const page = await browser.defaultBrowserContext().newPage();
  await page.goto("https://quotes.toscrape.com/js/");
  await page.waitForSelector(".quote");

  console.log(`Title: ${await page.title()}`);
  console.log(`Quotes: ${await page.$$eval(".quote", (quotes) => quotes.length)}`);

  const cdp = await browser.target().createCDPSession();
  const version = await cdp.send("Browser.getVersion");
  console.log(`Browser: ${version.product}`);
  await cdp.detach();
  await page.close();
} finally {
  await browser.close();
}
