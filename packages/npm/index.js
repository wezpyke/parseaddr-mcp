// parseaddr: small client for the hosted ParseAddr (libpostal) API.
//
//   import { parse, expand } from "parseaddr";
//   await parse("flat 2, 10 downing st, london sw1a 2aa"); // { input, parsed: {...}, components: [...] }
//
// Key via PARSEADDR_API_KEY env or the apiKey option. Free key: https://parseaddr.com
//
// Calls are tagged `X-Parseaddr-Client: pkg-npm/<ver>` so the server can count calls from
// this package (the MCP server tags `mcp/<ver>`). Keep the header.

export const VERSION = "0.1.0";
const DEFAULT_BASE = "https://api.parseaddr.com";
const CLIENT = `pkg-npm/${VERSION}`;

export class ParseAddrError extends Error {
  constructor(status, detail) {
    super(`parseaddr: ${status} ${typeof detail === "string" ? detail : JSON.stringify(detail)}`);
    this.name = "ParseAddrError";
    this.status = status;
    this.detail = detail;
  }
}

function resolveKey(apiKey) {
  const k = apiKey || process.env.PARSEADDR_API_KEY || "";
  if (!k) throw new Error("No API key. Set PARSEADDR_API_KEY or pass { apiKey }. Free key: https://parseaddr.com");
  return k;
}

// `client` is internal: the MCP bin passes "mcp/<ver>" so its calls are counted separately.
async function post(path, body, { apiKey, baseUrl, timeoutMs = 15000, client = CLIENT } = {}) {
  if (typeof body.address !== "string" || !body.address.trim()) {
    throw new TypeError("address must be a non-empty string");
  }
  const base = (baseUrl || process.env.PARSEADDR_API_BASE || DEFAULT_BASE).replace(/\/+$/, "");
  const res = await fetch(`${base}${path}`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${resolveKey(apiKey)}`,
      "Content-Type": "application/json",
      "X-Parseaddr-Client": client,
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(timeoutMs),
  });
  if (!res.ok) {
    const text = await res.text();
    let detail = text;
    try { detail = JSON.parse(text).detail ?? text; } catch {}
    throw new ParseAddrError(res.status, detail);
  }
  return res.json();
}

export function parse(address, { language, ...opts } = {}) {
  return post("/v1/parse", language ? { address, language } : { address }, opts);
}

export function expand(address, opts = {}) {
  return post("/v1/expand", { address }, opts);
}

export default { parse, expand, ParseAddrError, VERSION };
