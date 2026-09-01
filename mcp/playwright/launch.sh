#!/usr/bin/env bash
set -euo pipefail
umask 077

: "${ZYTE_API_KEY:?Set ZYTE_API_KEY before your MCP client starts.}"

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
server="$script_dir/node_modules/.bin/playwright-mcp"
if [[ ! -x "$server" ]]; then
  printf 'Playwright MCP is not installed. Run npm install in %s.\n' "$script_dir" >&2
  exit 1
fi

basic_token="$(printf '%s:' "$ZYTE_API_KEY" | base64 | tr -d '\r\n')"
export PLAYWRIGHT_MCP_CDP_HEADERS="Authorization: Basic $basic_token"
export PLAYWRIGHT_MCP_IMAGE_RESPONSES="omit"
export PLAYWRIGHT_MCP_ALLOWED_ORIGINS="https://quotes.toscrape.com"
export PLAYWRIGHT_MCP_BLOCK_SERVICE_WORKERS="true"

ws_url="$(ZYTE_BROWSER_ENDPOINT="${ZYTE_BROWSER_ENDPOINT:-https://browser.zyte.com/?ttl=600}" \
  node "$script_dir/session.mjs" discover)"
export PLAYWRIGHT_MCP_CDP_ENDPOINT="$ws_url"

server_pid=""
cleaned_up=0
cleanup() {
  if (( cleaned_up )); then return; fi
  cleaned_up=1
  trap - EXIT INT TERM
  if [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  fi
  ZYTE_BROWSER_WS_URL="$ws_url" node "$script_dir/session.mjs" close || \
    printf 'Warning: the remote browser could not be closed; it will end at its TTL.\n' >&2
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

set +e
"$server" "$@" <&0 &
server_pid=$!
wait "$server_pid"
status=$?
set -e

server_pid=""
cleanup
exit "$status"
