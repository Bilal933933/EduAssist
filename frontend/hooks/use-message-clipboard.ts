"use client";

import { useState } from "react";
import { toast } from "sonner";

// وظيفة واحدة: نسخ/مشاركة نص رسالة — بلا أي عرض.
export function useMessageClipboard(text: string) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast.success("تم نسخ الإجابة");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("فشل نسخ النص");
    }
  };

  const share = async () => {
    try {
      if (navigator.share) {
        await navigator.share({ title: "إجابة مساعد المدرس", text });
      } else {
        await navigator.clipboard.writeText(text);
        toast.success("تم نسخ النص للمشاركة");
      }
    } catch {
      /* إلغاء المستخدم */
    }
  };

  return { copied, copy, share };
}
