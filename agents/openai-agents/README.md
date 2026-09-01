# OpenAI Agents SDK with Playwright MCP

This Python agent starts one persistent Playwright MCP stdio subprocess and connects that server to Zyte Browser. The subprocess receives the generated CDP authorization header through its environment, not through `args`.

## Run

Requires Python 3.10 or newer, Node.js 18 or newer, and an OpenAI API key.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
npm install
export ZYTE_API_KEY="your-zyte-api-key"
export OPENAI_API_KEY="your-openai-api-key"
python main.py
```

The agent opens `https://quotes.toscrape.com`, reports its title, and asks MCP to close the browser. `MCPServerStdio` remains open across all model turns. Its async context manager terminates the subprocess even when the run fails. Cleanup reconnects to the same browser and sends raw CDP `Browser.close`. The example requests a 600-second TTL as a fallback because model turns can exceed the 60-second default.

Pinned packages are `openai-agents==0.22.0`, `python-dotenv==1.2.2`, `playwright==1.62.0`, and `@playwright/mcp@0.0.79`.
