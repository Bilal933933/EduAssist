"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

// الحد العام الأخير — يمسك ما تفلته حدود المسارات.
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Global error:", error);
  }, [error]);

  return (
    <html lang="ar" dir="rtl">
      <body>
        <div className="min-h-dvh flex flex-col items-center justify-center gap-4 p-8 text-center">
          <p className="font-extrabold text-lg">حدث خطأ غير متوقع</p>
          <p className="text-sm text-muted-foreground">أعد تحميل الصفحة أو عُد للرئيسية.</p>
          <div className="flex items-center gap-2">
            <Button onClick={reset} className="rounded-full">
              إعادة المحاولة
            </Button>
            <Button asChild variant="outline" className="rounded-full">
              <a href="/">الرئيسية</a>
            </Button>
          </div>
        </div>
      </body>
    </html>
  );
}
