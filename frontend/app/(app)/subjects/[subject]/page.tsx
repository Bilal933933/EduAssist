"use client";

import Link from "next/link";
import { notFound, useParams } from "next/navigation";
import { ArrowLeft, Layers } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { useStats } from "@/lib/queries";
import { subjectIcon, UNCLASSIFIED } from "@/lib/subjects";
import { formatCount } from "@/lib/utils";

export default function SubjectDetailPage() {
  const params = useParams<{ subject: string }>();
  const subject = decodeURIComponent(params?.subject ?? "");
  const { data: stats, isPending, isError } = useStats();

  if (isPending) {
    return (
      <div className="container py-16 flex justify-center">
        <Spinner className="size-6" />
      </div>
    );
  }
  if (isError) {
    return (
      <div className="container py-16 text-center text-sm text-muted-foreground">
        تعذر جلب بيانات المادة — حاول تحديث الصفحة.
      </div>
    );
  }

  const rows = (stats?.by_subject ?? []).filter((r) => (r.subject || UNCLASSIFIED) === subject);
  if (rows.length === 0) notFound();

  const Icon = subjectIcon(subject);
  const totalChunks = rows.reduce((sum, r) => sum + r.chunks, 0);
  const stages = [...rows].sort((a, b) => b.chunks - a.chunks);

  return (
    <div className="container py-6 space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <div className="size-11 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
            <Icon className="size-6" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold">{subject}</h1>
            <p className="text-sm text-muted-foreground">
              {formatCount(totalChunks)} مقتطف مفهرس • {formatCount(stages.length)}{" "}
              {stages.length > 2 ? "مراحل" : "مرحلة"}
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <h2 className="font-bold text-sm bg-secondary px-3 py-1.5 rounded-full w-fit">المراحل</h2>
        <div className="grid gap-3">
          {stages.map((st) => (
            <div
              key={st.stage ?? "none"}
              className="border border-border rounded-2xl p-4 bg-card flex items-center justify-between gap-3"
            >
              <div className="min-w-0">
                <p className="font-bold text-sm flex items-center gap-2">
                  <Layers className="size-4 text-primary" />
                  {st.stage || "بدون مرحلة محددة"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatCount(st.chunks)} مقتطف من مصادر هذه المرحلة
                </p>
              </div>
              <Button asChild size="sm" variant="outline" className="rounded-full shrink-0">
                <Link href="/assistant">
                  حضّر منه <ArrowLeft className="size-4 mr-1.5" />
                </Link>
              </Button>
            </div>
          ))}
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        هذه القائمة مبنية على المصادر التي فهرستها بنفسك — لتحضير درس من هذه المادة افتح المساعد واسأل مباشرة.
      </p>
    </div>
  );
}
