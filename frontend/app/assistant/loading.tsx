import { Spinner } from "@/components/ui/spinner";

// شاشة تحميل مسار المساعد — نفس مؤشر بذر المحادثة.
export default function AssistantLoading() {
  return (
    <div className="flex-1 flex items-center justify-center gap-2 p-8 text-sm text-muted-foreground">
      <Spinner className="size-6" />
      تحميل المساعد...
    </div>
  );
}
