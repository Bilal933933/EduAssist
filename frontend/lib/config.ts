/** عنوان بوابة Realtime — كل طلبات الفرونت تمر من هنا فقط */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

/** عنوان داخلي لطلبات السيرفر (SSR) — داخل Docker اضبطه على اسم الخدمة.
 * مثال: INTERNAL_API_URL=http://realtime:3001 (فارغ محلياً = نفس العام) */
export const SERVER_API_BASE_URL =
  process.env.INTERNAL_API_URL || API_BASE_URL;
