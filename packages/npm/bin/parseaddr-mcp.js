#!/usr/bin/env node
// ParseAddr stdio MCP server (distributed via the `parseaddr` npm package).
// Launched by MCP registries / Smithery as `parseaddr-mcp`. Exposes `parse_address`
// and `expand_address` tools that call the hosted ParseAddr API. Tags every call
// `X-Parseaddr-Client: mcp/<ver>` — the server-side attribution for the agent channel.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { parse, expand, VERSION } from "../index.js";

// Same request, key lookup and errors as the library; tagged mcp/<ver> instead of pkg-npm/<ver>.
const opts = { client: `mcp/${VERSION}` };

const server = new McpServer({ name: "parseaddr", version: VERSION });

server.tool(
  "parse_address",
  "Parse a messy free-text postal address into structured fields (house_number, road, unit, city, postcode, country, ...). Powered by libpostal. Use when a user needs to standardise addresses without self-hosting the 2-4GB libpostal model.",
  { address: z.string().describe("raw address, e.g. 'flat 2, 10 downing st, london sw1a 2aa'") },
  async ({ address }) => ({ content: [{ type: "text", text: JSON.stringify(await parse(address, opts)) }] })
);

server.tool(
  "expand_address",
  "Expand/normalize an address into canonical variants for deduplication and record matching.",
  { address: z.string() },
  async ({ address }) => ({ content: [{ type: "text", text: JSON.stringify(await expand(address, opts)) }] })
);

await server.connect(new StdioServerTransport());
