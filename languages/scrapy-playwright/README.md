# Scrapy with scrapy-playwright

A minimal Scrapy project that connects scrapy-playwright to Zyte's remote browser over CDP and attaches to its existing default context. The spider scrolls `quotes.toscrape.com/scroll` until no more quotes load, then yields every quote and author.

Requires Python 3.10 or newer.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
ZYTE_API_KEY=your_api_key scrapy crawl quotes -O quotes.jsonl
```

The API key is read only from `ZYTE_API_KEY` and sent as HTTP Basic authentication. The spider keeps the attached Playwright page until parsing finishes so it can explicitly send the CDP `Browser.close` command, ending the Zyte browser session and billing before its TTL expires.

Do not run `playwright install`; this project uses Zyte's remote browser and does not need a local browser binary.
