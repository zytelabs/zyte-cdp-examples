# Network inspection

Listen for responses before navigation. Each line contains the status, resource type, host, and path. Query strings and headers are deliberately omitted so logs cannot expose credentials or tokens.

From the repository root, after installing `howtos/requirements.txt`:

```sh
ZYTE_API_KEY=your_api_key python howtos/network-inspection/main.py
```

The output includes the document and its static resources. Exact resource lines may change when the demo site changes.
