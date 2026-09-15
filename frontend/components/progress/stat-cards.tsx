import { formatCount } from "@/lib/utils";

interface StatCardsProps {
  threadCount: number;
  messageTotal: number;
  interactionCount: number;
  totalChunks: number;
  topicCount: number;
  grades: string[];
}

// وظيفة واحدة: بطاقات الأرقام الثلاث في أعلى صفحة التقدم.
export function StatCards({
  threadCount,
  messageTotal,
  interactionCount,
  totalChunks,
  topicCount,
  grades,
}: StatCardsProps) {
  return (
    <div className="grid md:grid-cols-3 gap-4">
      <div className="border border-border rounded-2xl p-5 bg-card text-center">
        <p className="text-3xl font-extrabold">{formatCount(threadCount)}</p>
        <p className="text-xs text-muted-foreground mt-1">محادثة محفوظة</p>
        <p className="text-[11px] text-muted-foreground mt-2">
          {messageTotal > 0 ? `بإجمالي ${formatCount(messageTotal)} رسالة` : "ابدأ أول محادثة من المساعد"}
        </p>
      </div>
      <div className="border border-border rounded-2xl p-5 bg-card text-center">
        <p className="text-3xl font-extrabold">{formatCount(interactionCount)}</p>
        <p className="text-xs text-muted-foreground mt-1">تفاعل مع مساعدك</p>
        <p className="text-[11px] text-muted-foreground mt-2">
          {formatCount(totalChunks)} مقتطف مفهرس من مصادرك
        </p>
      </div>
      <div className="border border-border rounded-2xl p-5 bg-card text-center">
        <p className="text-3xl font-extrabold">{formatCount(topicCount)}</p>
        <p className="text-xs text-muted-foreground mt-1">موضوعاً في سجلك</p>
        {grades.length > 0 && (
          <p className="text-[11px] text-muted-foreground mt-2 truncate">{grades.join(" • ")}</p>
        )}
      </div>
    </div>
  );
}
