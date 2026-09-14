"use client";

import { PanelRightClose, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ChatThread } from "@/lib/types";
import { ThreadList } from "./thread-list";

interface ChatSidebarProps {
  threads: ChatThread[];
  currentThreadId: number | null;
  onSelectThread: (id: number) => void;
  onNewChat: () => void;
  onDeleteThread: (id: number) => void;
  open?: boolean;
  onClose?: () => void;
  desktopHidden?: boolean;
  onCollapse?: () => void;
}

// الغلاف البصري وحده: نسخة ديسكتوب ثابتة + درج موبايل — المحتوى في ThreadList.
export function ChatSidebar({
  threads,
  currentThreadId,
  onSelectThread,
  onNewChat,
  onDeleteThread,
  open = false,
  onClose,
  desktopHidden = false,
  onCollapse,
}: ChatSidebarProps) {
  const contentProps = {
    threads,
    currentThreadId,
    onSelectThread,
    onNewChat,
    onDeleteThread,
  };

  return (
    <>
      {/* الشريط الجانبي — الشاشات الكبيرة */}
      <aside
        className={cn(
          "hidden lg:flex flex-col w-64 shrink-0 border-l border-border bg-background",
          desktopHidden && "lg:hidden"
        )}
      >
        <div className="h-12 px-3 flex items-center justify-between shrink-0">
          <span className="font-bold text-[13px] text-foreground">المحادثات</span>
          <Button
            variant="ghost"
            size="icon"
            onClick={onCollapse}
            aria-label="طي القائمة الجانبية"
            className="size-8 rounded-full text-muted-foreground hover:text-foreground"
          >
            <PanelRightClose className="size-4" />
          </Button>
        </div>
        <ThreadList {...contentProps} />
      </aside>

      {/* الدرج المنزلق — الجوال */}
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="absolute inset-0 bg-black/40 animate-in fade-in duration-200"
            onClick={onClose}
            aria-hidden="true"
          />
          <aside
            role="dialog"
            aria-modal="true"
            aria-label="قائمة المحادثات"
            className="absolute inset-y-0 right-0 w-72 max-w-[85vw] bg-background border-l border-border shadow-xl flex flex-col animate-in slide-in-from-right duration-200"
          >
            <div className="h-14 px-4 flex items-center justify-between border-b border-border/80 shrink-0">
              <span className="font-bold text-sm text-foreground">
                المحادثات
              </span>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                aria-label="إغلاق القائمة"
                className="size-9 rounded-xl text-muted-foreground hover:text-foreground"
              >
                <X className="size-4" />
              </Button>
            </div>
            <ThreadList {...contentProps} onItemClick={onClose} />
          </aside>
        </div>
      )}
    </>
  );
}
