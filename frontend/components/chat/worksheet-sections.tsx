"use client";

import { useWorksheetSections } from "@/hooks/use-worksheet-sections";
import { WorksheetToc } from "./worksheet-toc";
import { WorksheetSectionCard } from "./worksheet-section-card";
import { MarkdownRender } from "./markdown-render";

// وظيفة واحدة: تنسيق عرض الورقة (فهرس + أقسام مفتوحة) — بدون تقسيم أو تنسيق داخلي.
export function WorksheetSections({ content }: { content: string }) {
  const sections = useWorksheetSections(content);

  if (sections.length <= 1) {
    return <MarkdownRender content={content} />;
  }

  return (
    <div className="space-y-6">
      <WorksheetToc sections={sections} />
      <div className="space-y-7">
        {sections.map((s, i) => (
          <WorksheetSectionCard key={s.id} id={s.id} index={i} title={s.title} body={s.body} />
        ))}
      </div>
    </div>
  );
}
