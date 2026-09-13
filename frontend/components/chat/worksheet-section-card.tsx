"use client";

import { MarkdownRender } from "./markdown-render";

// وظيفة واحدة: عرض قسم واحد من الورقة — بدون فهرس أو منطق.
export function WorksheetSectionCard({
  id,
  index,
  title,
  body,
}: {
  id: string;
  index: number;
  title: string;
  body: string;
}) {
  return (
    <section id={id} aria-label={title} className="scroll-mt-32 pt-2">
      <h3 className="flex items-center gap-2 text-sm font-bold text-foreground mb-1">
        <span className="text-xs font-bold text-muted-foreground tabular-nums">{index + 1}</span>
        {title}
      </h3>
      <MarkdownRender content={body.trim() || "—"} />
    </section>
  );
}
