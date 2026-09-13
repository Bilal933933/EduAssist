"use client";

import { Menu, PanelRightOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatsResponse } from "@/lib/types";

interface ChatHeaderProps {
  stats: StatsResponse | null;
  onOpenMenu: () => void;
  status?: "idle" | "generating" | "done";
  sidebarOpen?: boolean;
}

// وظيفة واحدة: ترويسة نحيفة بأسلوب Gemini — بدون شعار ضخم أو حبوب.
export function ChatHeader({ stats, onOpenMenu, status = "idle", sidebarOpen = true }: ChatHeaderProps) {
  return (
    <header className="sticky top-0 z-20 w-full border-b border-border bg-background">
      <div className="max-w-2xl mx-auto px-3 sm:px-4 h-12 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          <Button
            variant="ghost"
            size="icon"
            onClick={onOpenMenu}
            aria-label={sidebarOpen ? "طي قائمة المحادثات" : "فتح قائمة المحادثات"}
            title={sidebarOpen ? "طي القائمة" : "فتح القائمة"}
            className="size-8 rounded-full text-muted-foreground hover:text-foreground shrink-0"
          >
            {sidebarOpen ? <Menu className="size-[18px]" /> : <PanelRightOpen className="size-[18px]" />}
          </Button>
          <h1 className="font-bold text-sm text-foreground truncate">مساعد المدرس</h1>
          {status === "generating" && (
            <span className="text-[11px] text-muted-foreground">· جارٍ التوليد...</span>
          )}
        </div>

        {stats && (
          <p className="text-[11px] text-muted-foreground tabular-nums shrink-0">
            {stats.total_chunks} مقتطف مفهرس
          </p>
        )}
      </div>
    </header>
  );
}
