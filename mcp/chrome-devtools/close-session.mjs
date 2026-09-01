import puppeteer from "puppeteer-core";

const apiKey = process.env.ZYTE_API_KEY;
const websocketUrl = process.env.ZYTE_BROWSER_WS_URL;

if (!apiKey || !websocketUrl) {
  throw new Error("ZYTE_API_KEY and ZYTE_BROWSER_WS_URL are required");
}

const browser = await puppeteer.connect({
  browserWSEndpoint: websocketUrl,
  headers: {
    Authorization: `Basic ${Buffer.from(`${apiKey}:`).toString("base64")}`,
  },
});
await browser.close();
