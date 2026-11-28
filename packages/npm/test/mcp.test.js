import { test } from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import http from "node:http";

const bin = fileURLToPath(new URL("../bin/parseaddr-mcp.js", import.meta.url));

test("stdio MCP server lists parse_address and expand_address", async () => {
  const child = spawn(process.execPath, [bin], { stdio: ["pipe", "pipe", "inherit"] });
  const send = (msg) => child.stdin.write(JSON.stringify({ jsonrpc: "2.0", ...msg }) + "\n");
  let buf = "";
  const tools = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("no tools/list reply in 5s")), 5000);
    child.stdout.on("data", (d) => {
      buf += d;
      for (const line of buf.split("\n").slice(0, -1)) {
        const msg = JSON.parse(line);
        if (msg.id === 1) {
          send({ method: "notifications/initialized" });
          send({ id: 2, method: "tools/list" });
        }
        if (msg.id === 2) { clearTimeout(timer); resolve(msg.result.tools.map((t) => t.name)); }
      }
      buf = buf.slice(buf.lastIndexOf("\n") + 1);
    });
    send({ id: 1, method: "initialize", params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "test", version: "0" } } });
  });
  child.kill();
  assert.deepEqual(tools.sort(), ["expand_address", "parse_address"]);
});

test("a tool call goes through the client with the mcp/<ver> tag", async () => {
  let seen;
  const api = http.createServer((req, res) => {
    seen = req.headers;
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ input: "x", components: [], parsed: { road: "downing st" } }));
  });
  await new Promise((r) => api.listen(0, "127.0.0.1", r));
  const env = { ...process.env, PARSEADDR_API_KEY: "pa_agent", PARSEADDR_API_BASE: `http://127.0.0.1:${api.address().port}` };
  const child = spawn(process.execPath, [bin], { stdio: ["pipe", "pipe", "inherit"], env });
  const send = (msg) => child.stdin.write(JSON.stringify({ jsonrpc: "2.0", ...msg }) + "\n");
  let buf = "";
  const text = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("no tools/call reply in 5s")), 5000);
    child.stdout.on("data", (d) => {
      buf += d;
      for (const line of buf.split("\n").slice(0, -1)) {
        const msg = JSON.parse(line);
        if (msg.id === 1) {
          send({ method: "notifications/initialized" });
          send({ id: 2, method: "tools/call", params: { name: "parse_address", arguments: { address: "10 downing st" } } });
        }
        if (msg.id === 2) { clearTimeout(timer); resolve(msg.result.content[0].text); }
      }
      buf = buf.slice(buf.lastIndexOf("\n") + 1);
    });
    send({ id: 1, method: "initialize", params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "test", version: "0" } } });
  });
  child.kill();
  api.close();
  assert.deepEqual(JSON.parse(text).parsed, { road: "downing st" });
  assert.equal(seen.authorization, "Bearer pa_agent");
  assert.match(seen["x-parseaddr-client"], /^mcp\//);
});
