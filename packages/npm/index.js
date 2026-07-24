// parseaddr — tiny client for the hosted ParseAddr (libpostal) API.
//
//   import { parse, expand } from "parseaddr";
//   await parse("flat 2, 10 downing st, london sw1a 2aa"); // { parsed: {...}, components: [...] }
//
// Key via PARSEADDR_API_KEY env or the apiKey option. Free tier: https://parseaddr.com
//
// Scaffold: correct shape, not yet published. Calls are tagged
// `X-Parseaddr-Client: pkg-npm/<ver>` so the package channel is attributable
// (the MCP server tags `mcp/<ver>`). Do NOT drop the header — Phase-3 proof metric.

export const VERSION = "0.1.0";
const API_BASE = process.env.PARSEADDR_API_BASE || "https://api.parseaddr.com";
const CLIENT = `pkg-npm/${VERSION}`;

function resolveKey(apiKey) {
  const k = apiKey || process.env.PARSEADDR_API_KEY || "";
  if (!k) throw new Error("No API key. Set PARSEADDR_API_KEY or pass { apiKey }. Free key: https://parseaddr.com");
  return k;
}

async function post(path, address, apiKey) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${resolveKey(apiKey)}`,
      "Content-Type": "application/json",
      "X-Parseaddr-Client": CLIENT,
    },
    body: JSON.stringify({ address }),
  });
  if (!res.ok) throw new Error(`parseaddr ${path} failed: ${res.status} ${await res.text()}`);
  return res.json();
}

export function parse(address, { apiKey } = {}) {
  return post("/v1/parse", address, apiKey);
}

export function expand(address, { apiKey } = {}) {
  return post("/v1/expand", address, apiKey);
}

export default { parse, expand, VERSION };
