# Forms

Select options in a form, submit it by its accessible role, and wait for the result. The target is a public demo search form whose tag dropdown is filled in by the page's own script after an author is chosen, so the second selection depends on rendered form state rather than the static HTML.

From the repository root, after installing `howtos/requirements.txt`:

```sh
ZYTE_API_KEY=your_api_key python howtos/forms/main.py
```

Successful output prints the first quote matching the selected author and tag. The script does not print the API key.
