import { BookOpen, Calculator, FlaskConical, Globe, Languages, Library, type LucideIcon } from "lucide-react";
import { SubjectCount } from "@/lib/types";

export const UNCLASSIFIED = "غير مصنّف";

export interface SubjectStage {
  stage: string | null;
  chunks: number;
}

export interface SubjectGroup {
  subject: string;
  chunks: number;
  stages: SubjectStage[];
}

// تجميع صفوف (مادة، مرحلة) القادمة من /api/stats في بطاقات مواد قابلة للعرض.
export function aggregateSubjects(rows: SubjectCount[] | undefined): SubjectGroup[] {
  const groups = new Map<string, SubjectGroup>();
  for (const row of rows ?? []) {
    const subject = row.subject || UNCLASSIFIED;
    const group = groups.get(subject) ?? { subject, chunks: 0, stages: [] };
    group.chunks += row.chunks;
    group.stages.push({ stage: row.stage, chunks: row.chunks });
    groups.set(subject, group);
  }
  return [...groups.values()].sort((a, b) => b.chunks - a.chunks);
}

const ICON_MATCHERS: { pattern: RegExp; icon: LucideIcon }[] = [
  { pattern: /عربي/, icon: BookOpen },
  { pattern: /رياض/, icon: Calculator },
  { pattern: /علوم/, icon: FlaskConical },
  { pattern: /اجتماع/, icon: Globe },
  { pattern: /إنجليز|انجليز/, icon: Languages },
];

export function subjectIcon(subject: string): LucideIcon {
  return ICON_MATCHERS.find((m) => m.pattern.test(subject))?.icon ?? Library;
}
