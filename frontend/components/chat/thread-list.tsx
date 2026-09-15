"use client";

import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { cn } from "@/lib/utils";
import type { ChatThread } from "@/lib/types";

export interface ThreadListProps {
  threads: ChatThread[];
  currentThreadId: number | null;
  onSelectThread: (id: number) => void;
  onNewChat: () => void;
  onDeleteThread: (id: number) => void;
  onItemClick?: () => void;
}

// وظيفة واحدة: قائمة المحادثات + زر الجديد + تبديل المظهر — تُستخدم في نسختي السايدبار.
export function ThreadList({
  threads,
  currentThreadId,
  onSelectThread,
  onNewChat,
  onDeleteThread,
  onItemClick,
}: ThreadListProps) {
  return (
    <>
      <div className="p-3 pb-2">
        <Button
          onClick={() => {
            onNewChat();
            onItemClick?.();
          }}
          className="w-full h-9 rounded-full gap-2 text-[13px] font-semibold"
        >
          <Plus className="size-4" />
          <span>محادثة جديدة</span>
        </Button>
      </div>

      <nav
        aria-label="المحادثات السابقة"
        className="flex-1 overflow-y-auto px-3 pb-2 space-y-1"
      >
        {threads.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-6 px-2 leading-relaxed">
            لا توجد محادثات سابقة بعد.
            <br />
            ابدأ أول سؤال لمساعدك!
          </p>
        ) : (
          threads.map((t) => (
            <ThreadItem
              key={t.id}
              thread={t}
              active={t.id === currentThreadId}
              onSelect={() => {
                onSelectThread(t.id);
                onItemClick?.();
              }}
              onDelete={() => onDeleteThread(t.id)}
            />
          ))
        )}
      </nav>

      <div className="border-t border-border/80 p-3 flex items-center justify-between">
        <span className="text-[11px] font-medium text-muted-foreground">
          المظهر
        </span>
        <ThemeToggle />
      </div>
    </>
  );
}

function ThreadItem({
  thread,
  active,
  onSelect,
  onDelete,
}: {
  thread: ChatThread;
  active: boolean;
  onSelect: () => void;
  onDelete: () => void;
}) {
  return (
    <div
      className={cn(
        "group flex items-center rounded-xl border transition-colors",
        active
          ? "bg-secondary border-primary/30"
          : "border-transparent hover:bg-muted/70"
      )}
    >
      <button
        type="button"
        onClick={onSelect}
        className="flex-1 min-w-0 text-right px-3 py-2.5 rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-ring cursor-pointer"
      >
        <span
          className={cn(
            "block text-[13px] font-semibold truncate",
            active ? "text-secondary-foreground" : "text-foreground"
          )}
        >
          {thread.title}
        </span>
        <span className="block text-[11px] text-muted-foreground mt-0.5">
          {thread.message_count} رسالة
        </span>
      </button>
      <Button
        variant="ghost"
        size="icon"
        aria-label={`حذف محادثة: ${thread.title}`}
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className="size-8 shrink-0 ml-1 opacity-60 lg:opacity-0 lg:group-hover:opacity-100 focus-visible:opacity-100 hover:bg-destructive/10 hover:text-destructive rounded-lg transition-opacity"
      >
        <Trash2 className="size-3.5" />
      </Button>
    </div>
  );
}
