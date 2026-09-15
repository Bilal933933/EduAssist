"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface DeleteThreadDialogProps {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

// وظيفة واحدة: تأكيد حذف المحادثة — قرار الحذف نفسه في useThreadActions.
export function DeleteThreadDialog({ open, onConfirm, onCancel }: DeleteThreadDialogProps) {
  return (
    <Dialog open={open} onOpenChange={(v) => !v && onCancel()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>حذف المحادثة؟</DialogTitle>
          <DialogDescription>
            سيُحذف سجل هذه المحادثة نهائياً ولا يمكن استرجاعه.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="destructive" onClick={onConfirm} className="rounded-full">
            حذف نهائي
          </Button>
          <Button variant="outline" onClick={onCancel} className="rounded-full">
            تراجع
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
