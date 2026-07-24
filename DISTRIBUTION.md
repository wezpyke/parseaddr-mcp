# ParseAddr — Distribution / registry submission runbook
_Owner: Rift. Fire the moment Phase-0 is live (API deployed at api.parseaddr.com). All £0._
_Strategy detail: `../../PLANS/PARSEADDR_PHASE1_DISCOVERABILITY.md`._

## Prerequisites (the master dependency — must exist before submitting)
1. **Public GitHub repo** `github.com/wezpyke/parseaddr-mcp` (Wez's account — confirmed 2026-07-24). Registries auto-crawl it; several key off it entirely.
   - Then set the real URL in: `server.json` `repository.url`, `packages/npm/package.json`, `packages/pypi/pyproject.toml`.
2. **API live** at `https://api.parseaddr.com` (Fizz / Phase 0).
3. **Packages published** (names confirmed FREE 2026-07-24 on npm + PyPI):
   - PyPI: `cd packages/pypi && python -m build && twine upload dist/*`
   - npm:  `cd packages/npm && npm publish --access public`
   - Ownership check: npm uses `package.json` `mcpName` (set to `com.parseaddr/address-parse`). **PyPI: verify the required ownership marker in the MCP registry package-types doc before publishing** — do not assume; confirm the field.

## Submit — one pass, top registries
| # | Registry | Command / action | Notes |
|---|---|---|---|
| 1 | **Official MCP Registry** | `mcp-publisher init` (already have `server.json`) → `mcp-publisher login dns` (TXT challenge on parseaddr.com) → `mcp-publisher publish --dry-run` → `publish` | DNS auth lets us own the branded `com.parseaddr/*` namespace. No human review. |
| 2 | **Smithery** | `smithery mcp publish https://api.parseaddr.com -n parseaddr/address-parse` | Uses `smithery.yaml`; gives config UI + analytics. |
| 3 | **mcp.so** | Submit at https://mcp.so/submit (GitHub repo URL) → complete draft → save = publish | Public GitHub server. |
| 4 | **Glama** | Ensure repo public → claim listing via GitHub at glama.ai | Auto-crawled; just claim. |
| 5 | **PulseMCP** | Auto-crawled → claim ownership | Same as Glama. |
| 6 | **LobeHub** | Submit at lobehub.com/mcp (GitHub) | 1-click install for LobeHub agents. |
| 7 | **Cline Marketplace** | PR to `github.com/cline/mcp-marketplace` | High-value: large Cline dev base. |
| 8 | **MCP.Pub / MCP.Directory** | email repo link / submit → auto-pull | Bonus reach, live ~24h. |

## Also publish (non-MCP dev discovery)
- **RapidAPI** listing (Phase-1 roadmap item) — buyers who browse API marketplaces.
- Keep `llms.txt` (repo root, served at parseaddr.com/llms.txt) current — inference-time agent retrieval.

## Attribution (why the client headers matter — do not strip)
Every entry point tags its source so Phase-3 can prove the agent channel with no referrers:
`mcp/<ver>` (MCP server) · `pkg-pypi/<ver>` · `pkg-npm/<ver>` (package client calls) · web/ad via UTM.
Server side (Fizz): record `X-Parseaddr-Client` + first-touch `source` per API key in the meter.
Headline metric: **paying signups by first-touch channel.**
