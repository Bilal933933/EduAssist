"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { login, register } from "@/lib/auth";
import { toast } from "sonner";

interface AuthPanelProps {
  onSuccess: () => void;
}

export function AuthPanel({ onSuccess }: AuthPanelProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    try {
      if (mode === "login") {
        await login(email.trim(), password);
        toast.success("تم تسجيل الدخول بنجاح");
      } else {
        await register(email.trim(), password, name.trim() || undefined);
        toast.success("تم إنشاء الحساب وتسجيل الدخول");
      }
      onSuccess();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "حدث خطأ غير متوقع.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-dvh flex items-center justify-center bg-background px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 rounded-xl border border-border/60 bg-card p-6 shadow-sm"
      >
        <div className="text-center space-y-1">
          <h1 className="text-2xl font-bold">مساعد المدرس الذكي</h1>
          <p className="text-sm text-muted-foreground">
            {mode === "login"
              ? "سجّل دخولك لمواصلة تحضير دروسك"
              : "أنشئ حسابك لتبدأ تحضير دروسك"}
          </p>
        </div>

        {mode === "register" && (
          <Input
            type="text"
            placeholder="الاسم (اختياري)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={busy}
          />
        )}
        <Input
          type="email"
          dir="ltr"
          placeholder="email@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={busy}
        />
        <Input
          type="password"
          dir="ltr"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
          disabled={busy}
        />

        <Button type="submit" className="w-full" disabled={busy}>
          {busy && <Spinner className="size-4" />}
          {mode === "login" ? "تسجيل الدخول" : "إنشاء حساب"}
        </Button>

        <button
          type="button"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          className="w-full text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          disabled={busy}
        >
          {mode === "login"
            ? "ليس لديك حساب؟ أنشئ حساباً جديداً"
            : "لديك حساب بالفعل؟ سجّل دخولك"}
        </button>
      </form>
    </div>
  );
}
