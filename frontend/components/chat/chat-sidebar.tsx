"use client";

import { PanelRightClose, Plus, Trash2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { cn } from "@/lib/utils";
import { ChatThread } from "@/lib/types";

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

interface SidebarContentProps {
  threads: ChatThread[];
  currentThreadId: number | null;
  onSelectThread: (id: number) => void;
  onNewChat: () => void;
  onDeleteThread: (id: number) => void;
  onItemClick?: () => void;
}

function SidebarContent({
  threads,
  currentThreadId,
  onSelectThread,
  onNewChat,
  onDeleteThread,
  onItemClick,
}: SidebarContentProps) {
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
            ابدأ أول سؤال نحوي!
          </p>
        ) : (
          threads.map((t) => {
            const active = t.id === currentThreadId;
            return (
              <div
                key={t.id}
                className={cn(
                  "group flex items-center rounded-xl border transition-colors",
                  active
                    ? "bg-secondary border-primary/30"
                    : "border-transparent hover:bg-muted/70"
                )}
              >
                <button
                  type="button"
                  onClick={() => {
                    onSelectThread(t.id);
                    onItemClick?.();
                  }}
                  className="flex-1 min-w-0 text-right px-3 py-2.5 rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-ring cursor-pointer"
                >
                  <span
                    className={cn(
                      "block text-[13px] font-semibold truncate",
                      active ? "text-secondary-foreground" : "text-foreground"
                    )}
                  >
                    {t.title}
                  </span>
                  <span className="block text-[11px] text-muted-foreground mt-0.5">
                    {t.message_count} رسالة
                  </span>
                </button>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`حذف محادثة: ${t.title}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteThread(t.id);
                  }}
                  className="size-8 shrink-0 ml-1 opacity-0 group-hover:opacity-100 focus-visible:opacity-100 hover:bg-destructive/10 hover:text-destructive rounded-lg transition-opacity"
                >
                  <Trash2 className="size-3.5" />
                </Button>
              </div>
            );
          })
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
        <SidebarContent {...contentProps} />
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
            <SidebarContent {...contentProps} onItemClick={onClose} />
          </aside>
        </div>
      )}
    </>
  );
}
