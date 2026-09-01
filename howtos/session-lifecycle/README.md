# Session lifecycle

Attach to Zyte Browser, use its existing default context, create and close one page, then terminate the remote browser with the CDP `Browser.close` command. Closing only a page does not end the browser session.

From the repository root, after installing `howtos/requirements.txt`:

```sh
ZYTE_API_KEY=your_api_key python howtos/session-lifecycle/main.py
```

The output reports context and page counts, then confirms that `Browser.close` was sent. The counts can include a startup page owned by the remote browser.
