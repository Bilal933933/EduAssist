"use client";

import { BookOpen, Menu, Sparkles, Database, Circle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatsResponse } from "@/lib/types";

interface ChatHeaderProps {
  stats: StatsResponse | null;
  onOpenMenu: () => void;
}

export function ChatHeader({ stats, onOpenMenu }: ChatHeaderProps) {
  return (
    <header className="sticky top-0 z-20 w-full border-b border-border/80 bg-background/85 backdrop-blur-md transition-all shadow-2xs">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-3">
        {/* Brand Section */}
        <div className="flex items-center gap-3 min-w-0">
          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={onOpenMenu}
            aria-label="فتح قائمة المحادثات"
            className="lg:hidden size-9 rounded-xl text-muted-foreground hover:text-primary hover:bg-primary/10 shrink-0"
          >
            <Menu className="size-5" />
          </Button>

          <div className="size-10 rounded-2xl bg-gradient-to-tr from-primary via-emerald-800 to-teal-900 text-white flex items-center justify-center shadow-md shadow-primary/20 ring-2 ring-primary/20 shrink-0">
            <BookOpen className="size-5 text-amber-300" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-lg leading-none tracking-tight text-foreground truncate">
                مساعد المدرس
              </h1>
              <span className="text-[10px] font-bold tracking-wide uppercase bg-amber-500/10 text-amber-700 dark:text-amber-400 px-2 py-0.5 rounded-full border border-amber-500/25 flex items-center gap-1 shadow-2xs">
                <Sparkles className="size-2.5 text-amber-500" />
                Agentic RAG
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5 font-medium truncate">
              تحضير الدروس وخطط الشرح وسير الحصة
            </p>
          </div>
        </div>

        {/* Status */}
        {stats && (
          <div className="hidden lg:flex items-center gap-2 bg-card/90 text-foreground px-3.5 py-1.5 rounded-full text-xs font-semibold border border-border/80 shadow-2xs shrink-0">
            <Database className="size-3.5 text-primary" />
            <span>
              <strong className="font-bold text-primary">{stats.total_chunks}</strong>{" "}
              مقتطف مفهرس
            </span>
            <Circle className="size-2 fill-emerald-500 text-emerald-500 animate-pulse" />
          </div>
        )}
      </div>
    </header>
  );
}
