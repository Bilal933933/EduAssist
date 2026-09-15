"use client";

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { useParams } from "next/navigation";
import { AuthGate } from "@/components/auth/auth-gate";
import { ChatSidebar } from "./chat-sidebar";
import { DeleteThreadDialog } from "./delete-thread-dialog";
import { useThreads } from "@/lib/queries";
import { useThreadActions } from "@/hooks/use-thread-actions";

interface SidebarControls {
  desktopSidebar: boolean;
  setDesktopSidebar: (v: boolean) => void;
  openMenu: () => void;
}

const SidebarControlsContext = createContext<SidebarControls | null>(null);

// حالة واجهة محلية بسيطة (زر القائمة) — تُستهلك من الترويسة داخل اللوحة.
export function useSidebarControls(): SidebarControls {
  const ctx = useContext(SidebarControlsContext);
  if (!ctx) throw new Error("useSidebarControls خارج AssistantShell");
  return ctx;
}

// الغلاف الوحيد لمسار /assistant: سايدبار التنقل + محتوى الصفحة.
// currentThreadId من الـ URL — الضغط على محادثة = انتقال لمسارها.
export function AssistantShell({ children }: { children: ReactNode }) {
  return (
    <AuthGate>
      <AssistantFrame>{children}</AssistantFrame>
    </AuthGate>
  );
}

function AssistantFrame({ children }: { children: ReactNode }) {
  const params = useParams();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [desktopSidebar, setDesktopSidebar] = useState(true);

  const activeId = (() => {
    const raw = params?.threadId;
    const n = Number(Array.isArray(raw) ? raw[0] : raw);
    return Number.isInteger(n) && n > 0 ? n : null;
  })();

  const { data: threads = [] } = useThreads(true);
  const { select, createNew, remove, pendingDelete, confirmDelete, cancelDelete } = useThreadActions(activeId);

  const openMenu = useCallback(() => {
    if (window.innerWidth < 1024) setSidebarOpen(true);
    else setDesktopSidebar((v) => !v);
  }, []);

  const controls = useMemo<SidebarControls>(
    () => ({ desktopSidebar, setDesktopSidebar, openMenu }),
    [desktopSidebar, openMenu]
  );

  return (
    <SidebarControlsContext.Provider value={controls}>
      <div className="flex h-dvh overflow-hidden bg-background">
        <ChatSidebar
          threads={threads}
          currentThreadId={activeId}
          onSelectThread={select}
          onNewChat={createNew}
          onDeleteThread={remove}
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          desktopHidden={!desktopSidebar}
          onCollapse={() => setDesktopSidebar(false)}
        />
        <DeleteThreadDialog
          open={pendingDelete != null}
          onConfirm={confirmDelete}
          onCancel={cancelDelete}
        />
        {children}
      </div>
    </SidebarControlsContext.Provider>
  );
}
