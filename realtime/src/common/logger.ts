/** اللوجر المركزي — نسخة TypeScript من backend/app/core/logging.py
 * 3 قنوات JSONL تحت realtime/logs/ + كونسول UTF-8:
 * app.jsonl / retrieval.jsonl / errors.jsonl — نفس أسماء بايثون.
 * إخفاء: AIza... + قيم GEMINI_API_KEY/INTERNAL_API_KEY/JWT_SECRET.
 */
import { appendFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { getRequestId } from "./request-context";

const REDACT_PATTERNS = [/AIza[0-9A-Za-z\-_]{10,}/g, /(gemini_api_key|internal_api_key|jwt_secret)\s*[:=]\s*['"]?[^'"\s,}]+/gi];

function redact(msg: string): string {
  let out = msg;
  for (const pat of REDACT_PATTERNS) out = out.replace(pat, "[REDACTED]");
  for (const key of ["GEMINI_API_KEY", "INTERNAL_API_KEY", "JWT_SECRET"]) {
    const secret = process.env[key];
    if (secret && secret.length >= 8 && out.includes(secret)) out = out.split(secret).join("[REDACTED]");
  }
  return out;
}

function logDir(): string {
  const dir = process.env.LOG_DIR && process.env.LOG_DIR.length > 0 ? process.env.LOG_DIR : join(__dirname, "..", "..", "logs");
  mkdirSync(dir, { recursive: true });
  return dir;
}

function write(channel: "app" | "retrieval" | "errors", line: string): void {
  try {
    appendFileSync(join(logDir(), `${channel}.jsonl`), `${line}\n`, { encoding: "utf-8" });
  } catch {
    /* السجل ثانوي — لا يكسر الطلب */
  }
}

function base(channel: string, level: string, payload: unknown): void {
  const rid = getRequestId() ?? "-";
  const text = typeof payload === "string" ? payload : JSON.stringify(payload);
  const safe = redact(text);
  if (channel === "app" || channel === "errors" || process.env.LOG_LEVEL?.toUpperCase() === "DEBUG") {
    const fn = level === "error" || level === "warn" ? console.error : console.log;
    fn(`${new Date().toISOString()} ${level.toUpperCase()} [eduassist.${channel}] rid=${rid} ${safe}`);
  }
  write(channel as "app" | "retrieval" | "errors", safe.startsWith("{") ? safe : JSON.stringify({ rid, msg: safe }));
}

export function getLogger(channel: "app" | "retrieval" | "errors" = "app") {
  return {
    info: (payload: unknown) => base(channel, "info", payload),
    warn: (payload: unknown) => base(channel, "warn", payload),
    error: (payload: unknown) => base(channel, "error", payload),
  };
}
