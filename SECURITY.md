# Security policy

## Reporting a vulnerability

Do not open a public issue for a vulnerability or exposed credential. Report security issues through [Zyte's security contact](https://www.zyte.com/security/) and include the affected file, impact, and reproduction steps.

## Credentials and browser data

A browser-level CDP connection can read and modify pages, cookies, storage, network traffic, and authenticated sessions. Treat it as browser-administrator access.

- Read `ZYTE_API_KEY` from the environment.
- Build the Basic authorization value in memory.
- Never print the API key, authorization header, or discovered WebSocket URL.
- Do not commit `.env`, session state, traces, HAR files, downloads, or screenshots from authenticated pages.
- Keep model credentials separate from the browser credential.

## Browser agents

Page content is untrusted input. A page can contain instructions intended to make an agent reveal data or invoke unrelated tools.

- Restrict agents to the domains required for the task.
- Require approval for uploads, downloads, arbitrary JavaScript, and destructive actions.
- Use one browser session per mutually untrusted agent or user.
- Do not treat MCP origin filters as a complete network security boundary.

The MCP examples use local stdio. If you expose MCP over HTTP, add TLS, authentication, origin and host validation, per-user browser ownership, rate limits, and audit-log redaction.
