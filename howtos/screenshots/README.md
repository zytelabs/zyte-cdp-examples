# Screenshots

Capture one element instead of the whole page. This keeps the image focused and avoids viewport-dependent page dimensions.

From the repository root, after installing `howtos/requirements.txt`:

```sh
ZYTE_API_KEY=your_api_key python howtos/screenshots/main.py
```

The script writes `howtos/screenshots/quotes.png` and prints its size. The repository's `*.png` ignore rule excludes this generated file.
