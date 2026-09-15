"""تصنيف الأخطاء — كل خطأ code ثابت + رسالة عربية + حالة HTTP، بلا تسريب داخلي."""


class AppError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


ERROR_MAP: dict[str, tuple[int, str]] = {
    "INTERNAL_ERROR": (500, "حدث خطأ داخلي. حاول مرة أخرى."),
    "NOT_FOUND": (404, "المحادثة غير موجودة."),
    "THREAD_NOT_FOUND": (404, "المحادثة غير موجودة."),
    "VALIDATION_ERROR": (422, "البيانات المرسلة غير صالحة."),
    "QUESTION_EMPTY": (422, "السؤال فارغ. اكتب سؤالك أولاً."),
    "QUESTION_TOO_SHORT": (422, "السؤال قصير جداً. اكتب سؤالاً أوضح."),
    "QUESTION_TOO_LONG": (422, "السؤال طويل جداً. اختصره إلى أقل من 2000 حرف."),
    "TOPIC_EMPTY": (422, "الموضوع فارغ. حدد موضوع البطاقات."),
    "TOPIC_TOO_LONG": (422, "اسم الموضوع طويل جداً."),
    "TEACHER_ID_INVALID": (422, "معرف المدرس غير صالح."),
    "GRADE_UNKNOWN": (422, "الصف غير معروف. اختر صفاً من القائمة."),
    "TITLE_TOO_LONG": (422, "عنوان المحادثة طويل جداً."),
    "UNAUTHORIZED": (401, "غير مصرح. سجل الدخول أولاً."),
    "INTERNAL_KEY_INVALID": (401, "مفتاح داخلي مفقود أو غير صحيح."),
    "KB_NOT_INDEXED": (500, "قاعدة البيانات المتجهية غير مفهرسة. شغّل الفهرسة أولاً."),
    "GEMINI_KEY_MISSING": (500, "مفتاح Gemini غير مجهز في الإعدادات."),
    "AI_UNREACHABLE": (502, "خدمة الذكاء الاصطناعي لا تستجيب. حاول لاحقاً."),
    "QUOTA_EXHAUSTED": (429, "ضغط مؤقت على خدمة الذكاء الاصطناعي. انتظر قليلاً ثم اضغط Retry."),
    "REINDEX_FAILED": (500, "فشلت إعادة الفهرسة. حاول مرة أخرى."),
}


def code_for(error: BaseException) -> str:
    """يصنف استثناءً غير متوقع لرمز خطأ: 429 من Google تعني نفاد حصة مؤقتاً."""
    if getattr(error, "code", None) == 429:
        return "QUOTA_EXHAUSTED"
    return "INTERNAL_ERROR"


def message_for(code: str) -> tuple[int, str]:
    return ERROR_MAP.get(code, ERROR_MAP["INTERNAL_ERROR"])
