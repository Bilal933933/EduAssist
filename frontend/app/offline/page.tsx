import Link from "next/link";
import { Button } from "@/components/ui/button";

export const metadata = {
  title: "دون اتصال",
};

// صفحة الانقطاع التي يعرضها الـ service worker عند غياب الشبكة.
export default function OfflinePage() {
  return (
    <div className="min-h-dvh flex flex-col items-center justify-center gap-4 p-8 text-center bg-background">
      <p className="font-extrabold text-lg">لا يوجد اتصال بالإنترنت</p>
      <p className="text-sm text-muted-foreground max-w-sm">
        تحقق من اتصالك ثم أعد المحاولة. المحادثات المحفوظة ستظهر فور عودة الشبكة.
      </p>
      <div className="flex items-center gap-2">
        <Button asChild className="rounded-full">
          <Link href="/assistant">إعادة المحاولة</Link>
        </Button>
        <Button asChild variant="outline" className="rounded-full">
          <Link href="/">الرئيسية</Link>
        </Button>
      </div>
    </div>
  );
}
