#!/usr/bin/env bash
set -euo pipefail
umask 077

: "${ZYTE_API_KEY:?Set ZYTE_API_KEY before your MCP client starts.}"

endpoint="${ZYTE_BROWSER_ENDPOINT:-https://browser.zyte.com}"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
server="$script_dir/node_modules/.bin/chrome-devtools-mcp"
if [[ ! -x "$server" ]]; then
  printf 'Chrome DevTools MCP is not installed. Run npm install in %s.\n' "$script_dir" >&2
  exit 1
fi

basic_token="$(printf '%s:' "$ZYTE_API_KEY" | base64 | tr -d '\r\n')"

header_file="$(mktemp)"
dump_file="$(mktemp)"
body_file="$(mktemp)"
stderr_file="$(mktemp)"
trap 'rm -f -- "$header_file" "$dump_file" "$body_file" "$stderr_file"' EXIT

printf 'Authorization: Basic %s\n' "$basic_token" >"$header_file"

ws_url=""
# Build the discovery URL with the URL API so an endpoint override that
# already carries query parameters (for example ?proxy_region=GB) survives.
url="$(node -e '
  const endpoint = new URL(process.argv[1]);
  endpoint.pathname = `${endpoint.pathname.replace(/\/$/, "")}/json/version`;
  if (process.argv[2]) endpoint.searchParams.set("ttl", process.argv[2]);
  else if (!endpoint.searchParams.has("ttl")) endpoint.searchParams.set("ttl", "600");
  process.stdout.write(endpoint.href);
' "$endpoint" "${ZYTE_BROWSER_TTL:-}")"
for attempt in 1 2 3 4 5; do
  : >"$dump_file"; : >"$body_file"
  code="$(curl --silent --show-error \
    --max-redirs 0 --max-time 60 \
    --header "@$header_file" \
    --dump-header "$dump_file" \
    --output "$body_file" \
    --write-out '%{http_code}' \
    2>"$stderr_file" \
    "$url" || true)"

  case "$code" in
    000)
      if (( attempt < 5 )); then sleep "$((attempt))"; fi
      ;;
    503)
      if (( attempt < 5 )); then sleep "$((attempt * 2))"; fi
      ;;
    401|403)
      printf 'CDP discovery rejected the credentials (HTTP %s). Check ZYTE_API_KEY.\n' "$code" >&2
      exit 1
      ;;
    3*)
      location="$(grep -i '^location:' "$dump_file" | tail -1 | cut -d' ' -f2- | tr -d '\r')"
      next_url="$(node -e '
        try {
          const target = new URL(process.argv[1], process.argv[2]);
          const trusted = target.hostname === "browser.zyte.com" ||
            target.hostname.endsWith(".browser.zyte.com");
          if (target.protocol === "https:" && trusted)
            process.stdout.write(target.href);
        } catch {}
      ' "$location" "$url")"
      if [[ -z "$next_url" ]]; then
        printf 'CDP discovery refused an untrusted redirect.\n' >&2
        exit 1
      fi
      url="$next_url"
      ;;
    2*)
      ws_url="$(node -e '
        const fs = require("fs");
        try {
          const parsed = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
          process.stdout.write(typeof parsed.webSocketDebuggerUrl === "string" ? parsed.webSocketDebuggerUrl : "");
        } catch {
          process.stdout.write("");
        }
      ' "$body_file")"
      if [[ -n "$ws_url" ]]; then break; fi
      if (( attempt < 5 )); then sleep "$((attempt))"; fi
      ;;
    *)
      printf 'CDP discovery failed with HTTP %s.\n' "$code" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$ws_url" ]]; then
  printf 'CDP discovery did not return a WebSocket URL after 5 attempts. A persistent 503 means no browser is currently available; retry later.\n' >&2
  exit 1
fi

export CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS=1

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
  ZYTE_BROWSER_WS_URL="$ws_url" node "$script_dir/close-session.mjs" || \
    printf 'Warning: the remote browser could not be closed; it will end at its TTL.\n' >&2
  rm -f -- "$header_file" "$dump_file" "$body_file" "$stderr_file"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

set +e
"$server" \
  --wsEndpoint "$ws_url" \
  --wsHeaders "{\"Authorization\":\"Basic $basic_token\"}" \
  --no-performance-crux \
  --redact-network-headers \
  "$@" <&0 &
server_pid=$!
wait "$server_pid"
status=$?
set -e

server_pid=""
cleanup
exit "$status"
