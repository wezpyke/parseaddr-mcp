import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { parse, expand, ParseAddrError, VERSION } from "../index.js";

let server, base, last;
const replies = {
  "/v1/parse": [200, { input: "10 downing st", components: [{ label: "house_number", value: "10" }, { label: "road", value: "downing st" }], parsed: { house_number: "10", road: "downing st" } }],
  "/v1/expand": [200, { input: "100 main st", variants: ["100 main street"] }],
};

before(async () => {
  server = http.createServer((req, res) => {
    let body = "";
    req.on("data", (c) => (body += c));
    req.on("end", () => {
      last = { method: req.method, url: req.url, headers: req.headers, body: JSON.parse(body) };
      const key = req.headers.authorization;
      const [status, json] = key === "Bearer bad" ? [401, { detail: "Invalid API key." }]
        : key === "Bearer capped" ? [429, { detail: "Monthly cap reached." }]
        : replies[req.url] || [404, { detail: "not found" }];
      if (key === "Bearer text") { res.writeHead(502); return res.end("Bad Gateway"); }
      res.writeHead(status, { "Content-Type": "application/json" });
      res.end(JSON.stringify(json));
    });
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${server.address().port}`;
});
after(() => server.close());

test("parse posts the address with the key and client header", async () => {
  const out = await parse("10 downing st", { apiKey: "pa_test", baseUrl: base });
  assert.deepEqual(out.parsed, { house_number: "10", road: "downing st" });
  assert.equal(last.method, "POST");
  assert.equal(last.url, "/v1/parse");
  assert.equal(last.headers.authorization, "Bearer pa_test");
  assert.equal(last.headers["x-parseaddr-client"], `pkg-npm/${VERSION}`);
  assert.deepEqual(last.body, { address: "10 downing st" });
});

test("parse sends the language hint only when given", async () => {
  await parse("10 downing st", { apiKey: "k", baseUrl: base, language: "en" });
  assert.deepEqual(last.body, { address: "10 downing st", language: "en" });
});

test("expand returns variants", async () => {
  const out = await expand("100 main st", { apiKey: "k", baseUrl: base + "/" });
  assert.deepEqual(out.variants, ["100 main street"]);
  assert.equal(last.url, "/v1/expand");
});

test("reads key and base from the environment", async () => {
  process.env.PARSEADDR_API_KEY = "pa_env";
  process.env.PARSEADDR_API_BASE = base;
  try {
    await parse("10 downing st");
    assert.equal(last.headers.authorization, "Bearer pa_env");
  } finally {
    delete process.env.PARSEADDR_API_KEY;
    delete process.env.PARSEADDR_API_BASE;
  }
});

test("missing key fails before any request", async () => {
  last = undefined;
  await assert.rejects(parse("10 downing st", { baseUrl: base }), /No API key/);
  assert.equal(last, undefined);
});

test("empty address fails before any request", async () => {
  last = undefined;
  await assert.rejects(parse("   ", { apiKey: "k", baseUrl: base }), TypeError);
  assert.equal(last, undefined);
});

test("HTTP errors raise ParseAddrError with status and detail", async () => {
  await assert.rejects(parse("x", { apiKey: "bad", baseUrl: base }), (e) => {
    assert.ok(e instanceof ParseAddrError);
    assert.equal(e.status, 401);
    assert.equal(e.detail, "Invalid API key.");
    return true;
  });
  await assert.rejects(expand("x", { apiKey: "capped", baseUrl: base }), { status: 429 });
  await assert.rejects(parse("x", { apiKey: "text", baseUrl: base }), { status: 502, detail: "Bad Gateway" });
});
