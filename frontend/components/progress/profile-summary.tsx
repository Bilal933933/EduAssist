interface ProfileSummaryProps {
  summary: string | null;
  classContext: string | null;
}

// وظيفة واحدة: بطاقة ملخص المساعد عن المدرس — لا تُعرض إن خلت البيانات.
export function ProfileSummary({ summary, classContext }: ProfileSummaryProps) {
  if (!summary && !classContext) return null;
  return (
    <div className="border border-border rounded-2xl p-5 bg-card">
      <p className="font-bold text-sm">ملخص مساعدك عنك</p>
      {summary && <p className="text-sm leading-7 mt-2 text-foreground/90">{summary}</p>}
      {classContext && <p className="text-sm leading-7 mt-2 text-muted-foreground">{classContext}</p>}
    </div>
  );
}
