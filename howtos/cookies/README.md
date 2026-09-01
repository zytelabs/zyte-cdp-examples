# Cookies

Add a cookie to the existing browser context, navigate, and verify that the server received it. `context.cookies()` is scoped to `httpbin.org` here, and the output prints cookie names rather than arbitrary cookie values.

From the repository root, after installing `howtos/requirements.txt`:

```sh
ZYTE_API_KEY=your_api_key python howtos/cookies/main.py
```

The output names the fixed `howto` cookie and reports whether httpbin returned its known value.
