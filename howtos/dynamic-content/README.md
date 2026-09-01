# Dynamic content

Wait for JavaScript-rendered content before reading it. The non-JavaScript HTML response does not contain the quote cards, so `wait_for()` is the important step.

From the repository root:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r howtos/requirements.txt
ZYTE_API_KEY=your_api_key python howtos/dynamic-content/main.py
```

The script prints the number of rendered quotes and the first quote. It closes the page, then sends `Browser.close` over CDP.
