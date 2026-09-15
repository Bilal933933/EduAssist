/** فك المغلف الموحد {ok,data,error} — يعمل مع بايثون و Realtime معاً.
 * توافق خلفي: إن لم يوجد حقل ok يُعاد JSON كما هو.
 */
import { handleUnauthorized } from "@/lib/auth";

export interface Envelope<T = unknown> {
  ok: boolean;
  data?: T;
  error?: { code: string; message: string };
}

export async function unwrap<T>(res: Response): Promise<T> {
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    // جلسة منتهية — خروج فوري لشاشة الدخول بدل التعليق الصامت
    if (res.status === 401) handleUnauthorized();
    // الفلاتر يعيد دائماً مغلف fail — نعرض رسالته العربية
    const msg = (json as Envelope)?.error?.message || `فشل الطلب (${res.status})`;
    throw new Error(msg);
  }
  if (typeof (json as Envelope)?.ok === "boolean") {
    if ((json as Envelope).ok) return (json as Envelope<T>).data as T;
    throw new Error((json as Envelope).error?.message || "فشلت العملية.");
  }
  return json as T;
}
