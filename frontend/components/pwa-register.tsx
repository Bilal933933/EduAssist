"use client";

import { useEffect } from "react";

// وظيفة واحدة: تسجيل الـ service worker مرة واحدة — صامت تماماً عند الفشل.
export function PwaRegister() {
  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;
    navigator.serviceWorker.register("/sw.js").catch(() => {
      /* بيئة لا تدعم أو ملف محجوب — التطبيق يعمل بدونه */
    });
  }, []);
  return null;
}
