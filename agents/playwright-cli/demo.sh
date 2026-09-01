#!/usr/bin/env bash
set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cli="$script_dir/zyte-playwright-cli"
session="zyte-example"
ws_url="$(ZYTE_BROWSER_ENDPOINT="${ZYTE_BROWSER_ENDPOINT:-https://browser.zyte.com/?ttl=600}" \
  node "$script_dir/session.mjs" discover)"
export PLAYWRIGHT_MCP_CDP_ENDPOINT="$ws_url"

cleanup() {
  "$cli" -s="$session" close >/dev/null 2>&1 || true
  ZYTE_BROWSER_WS_URL="$ws_url" node "$script_dir/session.mjs" close >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

"$cli" -s="$session" delete-data
# The pinned CLI accepts the attach target only as an argument, so the
# WebSocket URL is visible in the local process list while attach runs.
# Output is suppressed because attach echoes the target.
"$cli" attach --cdp="$ws_url" --session="$session" >/dev/null
"$cli" -s="$session" goto https://quotes.toscrape.com/
"$cli" -s="$session" eval 'document.title'
"$cli" -s="$session" close
ZYTE_BROWSER_WS_URL="$ws_url" node "$script_dir/session.mjs" close
trap - EXIT INT TERM
