/** تصنيف الأخطاء — نسخة TypeScript من backend/app/core/errors.py
 * نفس الأكواد + نفس الرسائل العربية + نفس حالات HTTP.
 * أي تغيير هنا يجب أن يعكس errors.py والعكس.
 */
export class AppError extends Error {
  readonly code: string;
  constructor(code: string) {
    super(code);
    this.code = code;
  }
}

export const ERROR_MAP: Record<string, { status: number; message: string }> = {
  INTERNAL_ERROR: { status: 500, message: "حدث خطأ داخلي. حاول مرة أخرى." },
  NOT_FOUND: { status: 404, message: "المحادثة غير موجودة." },
  THREAD_NOT_FOUND: { status: 404, message: "المحادثة غير موجودة." },
  VALIDATION_ERROR: { status: 422, message: "البيانات المرسلة غير صالحة." },
  QUESTION_EMPTY: { status: 422, message: "السؤال فارغ. اكتب سؤالك أولاً." },
  QUESTION_TOO_SHORT: { status: 422, message: "السؤال قصير جداً. اكتب سؤالاً أوضح." },
  QUESTION_TOO_LONG: { status: 422, message: "السؤال طويل جداً. اختصره إلى أقل من 2000 حرف." },
  TOPIC_EMPTY: { status: 422, message: "الموضوع فارغ. حدد موضوع البطاقات." },
  TOPIC_TOO_LONG: { status: 422, message: "اسم الموضوع طويل جداً." },
  TEACHER_ID_INVALID: { status: 422, message: "معرف المدرس غير صالح." },
  GRADE_UNKNOWN: { status: 422, message: "الصف غير معروف. اختر صفاً من القائمة." },
  TITLE_TOO_LONG: { status: 422, message: "عنوان المحادثة طويل جداً." },
  UNAUTHORIZED: { status: 401, message: "غير مصرح. سجل الدخول أولاً." },
  INTERNAL_KEY_INVALID: { status: 401, message: "مفتاح داخلي مفقود أو غير صحيح." },
  KB_NOT_INDEXED: { status: 500, message: "قاعدة البيانات المتجهية غير مفهرسة. شغّل الفهرسة أولاً." },
  GEMINI_KEY_MISSING: { status: 500, message: "مفتاح Gemini غير مجهز في الإعدادات." },
  AI_UNREACHABLE: { status: 502, message: "خدمة الذكاء الاصطناعي لا تستجيب. حاول لاحقاً." },
  QUOTA_EXHAUSTED: { status: 429, message: "ضغط مؤقت على خدمة الذكاء الاصطناعي. انتظر قليلاً ثم اضغط Retry." },
  REINDEX_FAILED: { status: 500, message: "فشلت إعادة الفهرسة. حاول مرة أخرى." },
};

export function messageFor(code: string): { status: number; message: string } {
  return ERROR_MAP[code] ?? ERROR_MAP.INTERNAL_ERROR;
}
