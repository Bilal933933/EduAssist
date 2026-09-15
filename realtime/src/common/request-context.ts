/** سياق الطلب — مقابل ContextVar في backend/app/core/request_context.py */
import { AsyncLocalStorage } from "node:async_hooks";
import { randomBytes } from "node:crypto";

const storage = new AsyncLocalStorage<{ requestId: string }>();

/** نفس بايثون: uuid4().hex[:12] */
export function newRequestId(): string {
  return randomBytes(6).toString("hex");
}

export function runWithRequestId<T>(requestId: string, fn: () => T): T {
  return storage.run({ requestId }, fn);
}

export function getRequestId(): string | null {
  return storage.getStore()?.requestId ?? null;
}
