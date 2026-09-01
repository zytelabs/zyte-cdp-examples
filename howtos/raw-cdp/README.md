# Raw CDP

Create a page-level CDP session and call `Runtime.evaluate` directly. Playwright locators are usually clearer, but raw protocol commands cover browser capabilities that Playwright does not wrap.

From the repository root, after installing `howtos/requirements.txt`:

```sh
ZYTE_API_KEY=your_api_key python howtos/raw-cdp/main.py
```

The script prints the quote count returned in the CDP result, detaches the page session, and closes the browser with the separate browser-level CDP session.
