"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

// حد المساعد: أي crash في المحادثة يبقى داخل المسار مع زر إعادة — لا صفحة بيضاء.
export default function AssistantError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Assistant error:", error);
  }, [error]);

  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center">
      <p className="font-extrabold text-lg">تعثر المساعد مؤقتاً</p>
      <p className="text-sm text-muted-foreground max-w-sm">
        حدث خطأ غير متوقع أثناء عرض المحادثة. محادثاتك محفوظة — أعد المحاولة.
      </p>
      <div className="flex items-center gap-2">
        <Button onClick={reset} className="rounded-full">
          إعادة المحاولة
        </Button>
        <Button asChild variant="outline" className="rounded-full">
          <a href="/assistant">محادثة جديدة</a>
        </Button>
      </div>
    </div>
  );
}
