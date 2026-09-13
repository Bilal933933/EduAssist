"use client";

import { ListOrdered } from "lucide-react";
import { WorksheetSection } from "@/hooks/use-worksheet-sections";

// وظيفة واحدة: فهرس أقسام الورقة للتنقل — بدون عرض المحتوى.
export function WorksheetToc({ sections }: { sections: WorksheetSection[] }) {
  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <nav aria-label="محتويات الورقة" className="py-3 border-y border-border">
      <p className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground mb-2">
        <ListOrdered className="size-3.5" />
        في هذه الإجابة ({sections.length})
      </p>
      <div className="flex flex-wrap gap-1.5">
        {sections.map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => scrollTo(s.id)}
            className="text-xs px-3 py-1.5 rounded-full border border-border text-foreground/80 hover:border-foreground/40 hover:text-foreground transition-colors"
          >
            {s.title}
          </button>
        ))}
      </div>
    </nav>
  );
}
