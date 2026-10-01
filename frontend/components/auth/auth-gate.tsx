"use client";

import { useEffect, useState } from "react";
import { AuthPanel } from "@/components/auth/auth-panel";
import { Spinner } from "@/components/ui/spinner";
import { getAuthToken } from "@/lib/auth";

// بوابة المصادقة الموحدة: زائر بلا جلسة ← شاشة الدخول، وإلا المحتوى.
export function AuthGate({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<"checking" | "guest" | "authed">("checking");

  useEffect(() => {
    let settled = false;
    const decide = () => {
      if (settled) return;
      settled = true;
      try {
        setState(getAuthToken() ? "authed" : "guest");
      } catch {
        setState("guest");
      }
    };
    decide();
    // شبكة أمان: لا بقاء في checking أبداً — أي عطل يعني زائراً لا تعليقاً.
    const t = setTimeout(decide, 2500);
    return () => clearTimeout(t);
  }, []);

  if (state === "checking") {
    return (
      <div className="min-h-dvh flex items-center justify-center bg-background" data-state="checking">
        <Spinner className="size-8" />
      </div>
    );
  }
  if (state === "guest") {
    return <AuthPanel onSuccess={() => setState("authed")} />;
  }
  return <>{children}</>;
}
