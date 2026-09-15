"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { deleteThread } from "@/lib/api";
import { queryKeys } from "@/lib/queries";

// وظيفة واحدة: عمليات المحادثات (اختيار/جديد/حذف) + التوجيه — بلا أي عرض.
export function useThreadActions(activeId: number | null) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [pendingDelete, setPendingDelete] = useState<number | null>(null);

  const select = (id: number) => {
    if (id === activeId) return;
    router.push(`/assistant/${id}`);
  };

  const createNew = () => {
    router.push("/assistant");
  };

  /** فتح نافذة التأكيد — الحذف الفعلي في confirmDelete */
  const requestDelete = (id: number) => setPendingDelete(id);
  const cancelDelete = () => setPendingDelete(null);

  const confirmDelete = async () => {
    const id = pendingDelete;
    if (id == null) return;
    setPendingDelete(null);
    try {
      await deleteThread(id);
      toast.success("تم حذف المحادثة");
      if (id === activeId) router.push("/assistant");
      queryClient.invalidateQueries({ queryKey: queryKeys.threads });
    } catch (error) {
      console.error("Delete thread error:", error);
      toast.error("تعذر حذف المحادثة.");
    }
  };

  return { select, createNew, remove: requestDelete, pendingDelete, confirmDelete, cancelDelete };
}
