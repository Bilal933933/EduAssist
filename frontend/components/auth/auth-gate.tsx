"use client";

import { useEffect, useState } from "react";
import { AuthPanel } from "@/components/auth/auth-panel";
import { Spinner } from "@/components/ui/spinner";
import { getAuthToken } from "@/lib/auth";

// بوابة المصادقة الموحدة: زائر بلا جلسة ← شاشة الدخول، وإلا المحتوى.
export function AuthGate({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<"checking" | "guest" | "authed">("checking");

  useEffect(() => {
    setState(getAuthToken() ? "authed" : "guest");
  }, []);

  if (state === "checking") {
    return (
      <div className="min-h-dvh flex items-center justify-center bg-background">
        <Spinner className="size-8" />
      </div>
    );
  }
  if (state === "guest") {
    return <AuthPanel onSuccess={() => setState("authed")} />;
  }
  return <>{children}</>;
}
