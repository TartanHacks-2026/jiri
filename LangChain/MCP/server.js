import express from "express";
import { spawn } from "child_process";

const app = express();
app.use(express.json({ limit: "10mb" }));

// Spawn mcp-uber (stdio MCP server)
const child = spawn("npx", ["mcp-uber"], {
  stdio: ["pipe", "pipe", "inherit"],
  env: process.env,
});

// Pending HTTP responses by request id (best-effort)
const pending = new Map();

// Read from mcp-uber stdout
child.stdout.setEncoding("utf8");
let buffer = "";

child.stdout.on("data", (chunk) => {
  buffer += chunk;
  let lines = buffer.split("\n");
  buffer = lines.pop() || "";

  for (const line of lines) {
    if (!line.trim()) continue;

    try {
      const msg = JSON.parse(line);

      // Try to route by id if present
      const id = msg?.id;
      if (id && pending.has(id)) {
        const res = pending.get(id);

        res.write(`event: message\n`);
        res.write(`data: ${JSON.stringify(msg)}\n\n`);

        // End after first response (good enough for now)
        pending.delete(id);
        res.end();
      } else {
        // If no id match, just broadcast to all open streams (safe fallback)
        for (const [, res] of pending) {
          res.write(`event: message\n`);
          res.write(`data: ${JSON.stringify(msg)}\n\n`);
        }
      }
    } catch (e) {
      console.error("Failed to parse MCP message:", line);
    }
  }
});

// Main MCP endpoint (Streamable HTTP)
app.post("/mcp", (req, res) => {
  const msg = req.body;

  // Set SSE headers
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.flushHeaders?.();

  // Try to track by id if present
  const id = msg?.id;
  if (id !== undefined) {
    pending.set(id, res);
  } else {
    // No id → still keep stream open (session/control message)
    const key = Symbol("no-id");
    pending.set(key, res);

    // Cleanup on close
    req.on("close", () => pending.delete(key));
  }

  // Forward raw JSON to stdio MCP server
  child.stdin.write(JSON.stringify(msg) + "\n");
});

// Health check
app.get("/", (req, res) => {
  res.send("Uber MCP HTTP wrapper running (SSE passthrough)");
});

// Start server
const PORT = process.env.PORT || 3333;
app.listen(PORT, () => {
  console.log(`MCP HTTP wrapper listening on http://localhost:${PORT}/mcp`);
});
