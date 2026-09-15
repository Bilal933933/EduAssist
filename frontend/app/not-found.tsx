import Link from "next/link";
import { Button } from "@/components/ui/button";

// حد 404 العام: أي مسار غير موجود أصلاً (مثل /assistantعع بلا slash).
export default function RootNotFound() {
  return (
    <div className="min-h-dvh flex flex-col items-center justify-center gap-4 p-8 text-center bg-background">
      <p className="font-extrabold text-2xl tabular-nums">404</p>
      <p className="font-bold text-lg">الصفحة غير موجودة</p>
      <p className="text-sm text-muted-foreground max-w-sm">
        الرابط الذي طلبته غير صحيح أو الصفحة نُقلت. عُد للمساعد أو الرئيسية.
      </p>
      <div className="flex items-center gap-2">
        <Button asChild className="rounded-full">
          <Link href="/assistant">المساعد</Link>
        </Button>
        <Button asChild variant="outline" className="rounded-full">
          <Link href="/">الرئيسية</Link>
        </Button>
      </div>
    </div>
  );
}
