import { TeacherTopic } from "@/lib/types";

// التقرير يأتي مجمّعاً حسب (موضوع، صف) — ندمج الصفوف ليظهر كل موضوع مرة واحدة.
export function mergeTopics(topics: TeacherTopic[] | undefined): { topic: string; count: number }[] {
  const merged = new Map<string, number>();
  for (const t of topics ?? []) {
    const topic = (t.topic || "").trim();
    if (!topic) continue;
    merged.set(topic, (merged.get(topic) ?? 0) + t.count);
  }
  return [...merged.entries()]
    .map(([topic, count]) => ({ topic, count }))
    .sort((a, b) => b.count - a.count);
}

// صفوف grades القديمة تحتوي بيانات فاسدة من إدخال نصي حر — لا نعرضها.
const JUNK_GRADE = /^custom_bad|ScopeField|value=|^primary_\d+/i;

export function cleanGradeLabel(label: string | null | undefined): string | null {
  if (!label || JUNK_GRADE.test(label)) return null;
  return label;
}
