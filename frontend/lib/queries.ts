"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchMemory, fetchStats, fetchThreads } from "@/lib/api";
import { AuthUser, getAuthToken, getStoredUser } from "@/lib/auth";

// مصادر الحقيقة الوحيدة لحالة السيرفر (AGENTS.md: TanStack Query وليس fetch في useEffect).
export const queryKeys = {
  stats: ["stats"] as const,
  threads: ["threads"] as const,
  memory: (grade?: string) => ["memory", grade ?? "all"] as const,
};

export function useStats(initialData?: Awaited<ReturnType<typeof fetchStats>> | null) {
  return useQuery({
    queryKey: queryKeys.stats,
    queryFn: fetchStats,
    initialData: initialData ?? undefined,
    staleTime: 60_000,
  });
}

export function useThreads(enabled: boolean) {
  return useQuery({
    queryKey: queryKeys.threads,
    queryFn: fetchThreads,
    enabled: enabled && !!getAuthToken(),
  });
}

export function useMemory(enabled: boolean, grade?: string) {
  return useQuery({
    queryKey: queryKeys.memory(grade),
    queryFn: () => fetchMemory(grade),
    enabled: enabled && !!getAuthToken(),
  });
}

// بيانات المدرس المحفوظة محلياً — تُقرأ بعد التركيب لتفادي اختلاف الترطيب.
export function useStoredUser(): AuthUser | null {
  const [user, setUser] = useState<AuthUser | null>(null);
  useEffect(() => setUser(getStoredUser()), []);
  return user;
}
