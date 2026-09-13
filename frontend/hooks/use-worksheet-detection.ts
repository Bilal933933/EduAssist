import { useMemo } from "react";

// وظيفة واحدة: كشف هل نص الرسالة ورقة عمل أم خطأ — بدون أي عرض أو جلب.
export function useWorksheetDetection(content: string) {
  return useMemo(() => {
    const isError = /تعذّر|ضغط مؤقت|429|حدث خطأ/.test(content);
    const hasKeywords =
      /ورقة عمل|نموذج الإجابة|تدريب موجّه|عمل مستقل|نشاط ختامي/.test(content);
    const headingCount = (content.match(/^#{1,3}\s+/gm) || []).length;
    const isWorksheet = !isError && (hasKeywords || headingCount >= 2);
    return { isWorksheet, isError };
  }, [content]);
}
