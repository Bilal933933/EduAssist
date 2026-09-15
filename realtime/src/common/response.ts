/** المغلف الموحد — نسخة TypeScript من backend/app/core/response.py
 * نجاح: { ok:true, data, meta:{requestId} }
 * فشل:  { ok:false, error:{code,message}, meta:{requestId} }
 * الفرونت يفك data فقط عندما ok===true.
 */
export interface ApiMeta {
  requestId: string | null;
}

export interface ApiSuccess<T = unknown> {
  ok: true;
  data: T;
  meta: ApiMeta;
}

export interface ApiFailure {
  ok: false;
  error: { code: string; message: string };
  meta: ApiMeta;
}

export type ApiEnvelope<T = unknown> = ApiSuccess<T> | ApiFailure;

export function ok<T>(data: T, requestId: string | null = null): ApiSuccess<T> {
  return { ok: true, data, meta: { requestId } };
}

export function fail(
  code: string,
  message: string,
  requestId: string | null = null,
): ApiFailure {
  return { ok: false, error: { code, message }, meta: { requestId } };
}

/** هل الرد مغلف جاهز من بايثون؟ لا نعيد تغليفه. */
export function isEnvelope<T = unknown>(value: unknown): value is ApiEnvelope<T> {
  if (typeof value !== "object" || value === null) return false;
  return (value as Record<string, unknown>).ok === true || (value as Record<string, unknown>).ok === false;
}
