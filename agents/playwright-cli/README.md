# Playwright CLI agent

A compact Playwright CLI example connected to Zyte Browser over CDP. The wrapper derives the Basic authorization header from `ZYTE_API_KEY` and passes it through the environment, never a process argument. One exception: the pinned CLI accepts the `attach` target only as an argument, so while `attach` runs, the discovered WebSocket URL — which identifies the browser session — is visible in the local process list.

## Run

Requires Node.js 18 or newer.

```sh
npm install
npm run agent-setup
export ZYTE_API_KEY="your-api-key"
npm run demo
```

`agent-setup` writes the Playwright CLI skill to `.agents/skills/playwright-cli`
so compatible coding agents can discover the command reference for the pinned
CLI. The generated skill documents the stock CLI, so its quick start opens a
local browser instead of Zyte Browser. Instruct agents to run
`./zyte-playwright-cli` instead of `playwright-cli` and to start sessions with
`attach` rather than `open`, as in the example below. See the note at the end
about session cleanup.

The demo opens `https://quotes.toscrape.com`, prints its title, and closes the named CLI session. It suppresses the attach command's output because the CLI otherwise prints the discovered WebSocket credential. It then reconnects to send raw CDP `Browser.close`; a shell trap performs the same cleanup after an error or signal. The example requests a 600-second TTL as a fallback because an agent task can exceed the 60-second default.

Agents can call `./zyte-playwright-cli` directly. For example:

```sh
./zyte-playwright-cli -s=research attach --cdp='https://browser.zyte.com/?ttl=600' >/dev/null
./zyte-playwright-cli -s=research goto https://quotes.toscrape.com/
./zyte-playwright-cli -s=research snapshot
./zyte-playwright-cli -s=research close
```

The project pins `@playwright/cli` to `0.1.18`. It uses the local binary, so it cannot silently download a newer CLI at runtime.

The pinned CLI's `close` command disconnects Playwright but does not send the
raw CDP `Browser.close` command required to end Zyte Browser immediately. The
demo adds that command after closing the CLI. When using the wrapper directly,
the remote session remains reserved until its TTL, so keep the TTL close to the
time the task needs.
