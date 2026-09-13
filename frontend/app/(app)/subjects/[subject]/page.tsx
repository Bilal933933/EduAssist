import Link from "next/link";
import { Clock, CheckCircle2, Play } from "lucide-react";
import { Button } from "@/components/ui/button";

const DATA: Record<string, { name: string; grade: string; units: { title: string; lessons: { title: string; status: string; time: string }[] }[] }> = {
  arabic: {
    name: "اللغة العربية",
    grade: "الصف الثالث الإعدادي",
    units: [
      { title: "01 — النحو", lessons: [{ title: "المبتدأ والخبر", status: "done", time: "12 دقيقة" }, { title: "كان وأخواتها", status: "done", time: "14 دقيقة" }, { title: "إن وأخواتها", status: "current", time: "12 دقيقة" }, { title: "الحال", status: "todo", time: "10 دقائق" }] },
      { title: "02 — القراءة", lessons: [{ title: "قصة أثر", status: "todo", time: "15 دقيقة" }] },
    ],
  },
};

export default async function SubjectDetail({ params }: { params: Promise<{ subject: string }> }) {
  const { subject } = await params;
  const data = DATA[subject] || DATA.arabic;
  return (
    <div className="container py-6 space-y-6">
      <div>
        <h1 className="text-xl font-extrabold">{data.name}</h1>
        <p className="text-sm text-muted-foreground">{data.grade}</p>
      </div>
      {data.units.map((u) => (
        <div key={u.title} className="space-y-3">
          <h2 className="font-bold text-sm bg-secondary px-3 py-1.5 rounded-full w-fit">{u.title}</h2>
          <div className="grid gap-3">
            {u.lessons.map((l) => (
              <div key={l.title} className="border border-border rounded-2xl p-4 bg-card flex items-center justify-between">
                <div>
                  <p className="font-bold text-sm flex items-center gap-2">
                    {l.status === "done" && <CheckCircle2 className="size-4 text-emerald-600" />}
                    {l.status === "current" && <Play className="size-4 text-primary" />}
                    {l.title}
                  </p>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1"><Clock className="size-3" />{l.time} • {l.status === "done" ? "مكتمل" : l.status === "current" ? "قيد التقدم" : "لم يبدأ"}</p>
                </div>
                <Button asChild size="sm" variant={l.status === "current" ? "default" : "outline"} className="rounded-full">
                  <Link href={l.status === "todo" ? "#" : "/assistant"}>{l.status === "done" ? "مراجعة" : l.status === "current" ? "متابعة" : "ابدأ"}</Link>
                </Button>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
