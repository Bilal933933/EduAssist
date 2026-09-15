import Link from "next/link";
import { Button } from "@/components/ui/button";

// محادثة برقم غير موجود (/assistant/[threadId] → notFound).
export default function ThreadNotFound() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center">
      <p className="font-extrabold text-lg">المحادثة غير موجودة</p>
      <p className="text-sm text-muted-foreground max-w-sm">
        ربما حُذفت أو الرابط غير صحيح. ابدأ محادثة جديدة أو اختر من القائمة.
      </p>
      <Button asChild className="rounded-full">
        <Link href="/assistant">محادثة جديدة</Link>
      </Button>
    </div>
  );
}
