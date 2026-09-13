"use client";

import { useState } from "react";
import { BookOpen, ChevronDown } from "lucide-react";
import { KnowledgeHit } from "@/lib/types";

interface MessageSourcesProps {
  hits: KnowledgeHit[];
}

// وظيفة واحدة: عرض مصادر الإجابة بأسلوب خافت — بدون أي منطق بحث.
export function MessageSources({ hits }: MessageSourcesProps) {
  const [open, setOpen] = useState(false);

  if (!hits || hits.length === 0) return null;

  return (
    <div className="border-t border-border pt-2">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <BookOpen className="size-3.5" />
        <span>المصادر ({hits.length})</span>
        <ChevronDown className={`size-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <ul className="mt-2 space-y-1.5">
          {hits.map((hit, i) => (
            <li key={i} className="text-xs leading-6 text-foreground/80">
              <span className="font-semibold text-foreground">{hit.title || "مرجع"}</span>
              {hit.page !== null && <span className="text-muted-foreground"> · صفحة {hit.page}</span>}
              {hit.similarity !== undefined && (
                <span className="text-muted-foreground">
                  {" "}· تطابق {Math.min(100, Math.max(0, Math.round(hit.similarity * 100)))}%
                </span>
              )}
              <span className="block text-muted-foreground line-clamp-2">{hit.text}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
