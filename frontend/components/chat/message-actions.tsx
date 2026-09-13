"use client";

import { Check, Copy, Layers, HelpCircle, Printer, Pencil, Share2 } from "lucide-react";
import { ExtrasKind } from "@/hooks/use-lesson-extras";

interface MessageActionsProps {
  copied: boolean;
  editing: boolean;
  loading: ExtrasKind | null;
  isError: boolean;
  onCopy: () => void;
  onCards: () => void;
  onQuiz: () => void;
  onPrint: () => void;
  onToggleEdit: () => void;
  onShare: () => void;
}

// وظيفة واحدة: صف أزرار الإجراءات بأسلوب Gemini — بدون أي منطق جلب.
export function MessageActions({
  copied,
  editing,
  loading,
  isError,
  onCopy,
  onCards,
  onQuiz,
  onPrint,
  onToggleEdit,
  onShare,
}: MessageActionsProps) {
  const btn =
    "h-7 w-7 rounded-full text-muted-foreground hover:text-foreground hover:bg-muted transition-colors flex items-center justify-center disabled:opacity-40";
  const label = "sr-only";

  return (
    <div className="flex items-center gap-0.5 pt-1" role="toolbar" aria-label="إجراءات على الإجابة">
      <button type="button" onClick={onCopy} className={btn} title={copied ? "تم النسخ" : "نسخ"}>
        {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
        <span className={label}>نسخ</span>
      </button>
      {!isError && (
        <>
          <button type="button" onClick={onCards} disabled={!!loading} className={btn} title="بطاقات مراجعة">
            <Layers className="size-3.5" />
            <span className={label}>بطاقات</span>
          </button>
          <button type="button" onClick={onQuiz} disabled={!!loading} className={btn} title="اختبار قصير">
            <HelpCircle className="size-3.5" />
            <span className={label}>اختبار</span>
          </button>
          <button type="button" onClick={onPrint} className={btn} title="طباعة / PDF">
            <Printer className="size-3.5" />
            <span className={label}>طباعة</span>
          </button>
          <button type="button" onClick={onToggleEdit} className={btn} title={editing ? "إلغاء التعديل" : "تعديل"}>
            <Pencil className="size-3.5" />
            <span className={label}>تعديل</span>
          </button>
          <button type="button" onClick={onShare} className={btn} title="مشاركة">
            <Share2 className="size-3.5" />
            <span className={label}>مشاركة</span>
          </button>
        </>
      )}
      {loading && <span className="text-[11px] text-muted-foreground mr-1">جارٍ التوليد...</span>}
    </div>
  );
}
