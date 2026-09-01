# Browser Use agent

An autonomous Browser Use agent connected to Zyte Browser with `Browser(cdp_url=..., headers=...)`. The script performs authenticated discovery first because Browser Use drops authorization on Zyte's cross-host discovery redirect. It reads a JavaScript-rendered quote, prints the agent's final answer, and sends raw `Browser.close` cleanup in a `finally` block.

## Run

Requires Python 3.11 or newer and an OpenAI API key for the agent model.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export ZYTE_API_KEY="your-zyte-api-key"
export OPENAI_API_KEY="your-openai-api-key"
python main.py
```

`browser-use` is pinned to `0.13.8`, Playwright to `1.62.0`, and `python-dotenv` to `1.2.2`. The Zyte credential starts as `ZYTE_API_KEY`; the script generates the Basic header in memory and does not place it in process arguments.

The example requests a 600-second TTL because model turns can exceed the
60-second default. It still ends the session as soon as the agent finishes.
