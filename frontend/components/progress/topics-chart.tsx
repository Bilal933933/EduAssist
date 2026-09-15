import { CheckCircle2, TrendingUp } from "lucide-react";
import { formatCount } from "@/lib/utils";

interface TopicsChartProps {
  topics: { topic: string; count: number }[];
  maxCount: number;
}

// وظيفة واحدة: عرض المواضيع — أشرطة التكرار + شارات المواضيع المتكررة.
export function TopicsChart({ topics, maxCount }: TopicsChartProps) {
  const repeated = topics.filter((t) => t.count >= 2).slice(0, 6);

  return (
    <div className="space-y-4">
      <div className="border border-border rounded-2xl p-5 bg-card">
        <p className="font-bold text-sm flex items-center gap-2">
          <TrendingUp className="size-4 text-primary" /> مواضيعك الأكثر تكراراً
        </p>
        {topics.length > 0 ? (
          <ul className="mt-4 space-y-3">
            {topics.slice(0, 8).map((t) => (
              <li key={t.topic}>
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium truncate">{t.topic}</span>
                  <span className="text-xs text-muted-foreground tabular-nums">{formatCount(t.count)}</span>
                </div>
                <div className="h-1.5 bg-secondary rounded-full mt-1.5 overflow-hidden">
                  <div className="h-full bg-primary rounded-full" style={{ width: `${Math.round((t.count / maxCount) * 100)}%` }} />
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground mt-3">
            لا مواضيع مسجلة بعد — ستُبنى تلقائياً من أسئلتك.
          </p>
        )}
      </div>

      <div className="border border-border rounded-2xl p-5 bg-card">
        <p className="font-bold text-sm flex items-center gap-2">
          <CheckCircle2 className="size-4 text-emerald-600" /> مواضيع تتكرر في سجلك
        </p>
        {repeated.length > 0 ? (
          <div className="flex flex-wrap gap-2 mt-3">
            {repeated.map((t) => (
              <span key={t.topic} className="text-xs bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 px-2.5 py-1 rounded-full">
                {t.topic}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground mt-3">ستظهر هنا المواضيع التي تعود إليها أكثر من مرة.</p>
        )}
      </div>
    </div>
  );
}
