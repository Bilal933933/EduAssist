"use client";

import { useState } from "react";
import { BookOpen, ChevronDown, ChevronUp, Layers, Quote } from "lucide-react";
import { KnowledgeHit } from "@/lib/types";

interface MessageSourcesProps {
  hits: KnowledgeHit[];
}

export function MessageSources({ hits }: MessageSourcesProps) {
  const [showSources, setShowSources] = useState(false);

  if (!hits || hits.length === 0) return null;

  return (
    <div className="pt-2 border-t border-border/50">
      <button
        type="button"
        onClick={() => setShowSources((prev) => !prev)}
        className="w-full flex items-center justify-between text-xs font-semibold text-primary hover:text-primary/80 transition-colors py-2 px-3 rounded-xl bg-primary/5 hover:bg-primary/10 border border-primary/15"
      >
        <div className="flex items-center gap-2">
          <Layers className="size-4" />
          <span>
            المصادر والمراجع النحوية ({hits.length} مراجع)
          </span>
        </div>
        {showSources ? (
          <ChevronUp className="size-4" />
        ) : (
          <ChevronDown className="size-4" />
        )}
      </button>

      {showSources && (
        <div className="mt-3 space-y-3 transition-all animate-in fade-in-50 duration-200">
          {hits.map((hit: KnowledgeHit, index: number) => (
            <div
              key={index}
              className="bg-secondary/40 border border-primary/15 rounded-xl p-3.5 text-xs space-y-2 text-right"
            >
              <div className="flex items-center justify-between font-medium text-foreground">
                <div className="flex items-center gap-2">
                  <BookOpen className="size-4 text-primary" />
                  <span className="font-bold text-primary text-sm">{hit.title || "مرجع نحوي"}</span>
                  {hit.page !== null && (
                    <span className="text-muted-foreground text-xs bg-background px-2 py-0.5 rounded-md border border-border/60">
                      صفحة {hit.page}
                    </span>
                  )}
                </div>
                {hit.similarity !== undefined && (
                  <span className="text-[11px] bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800 font-semibold">
                    تطابق {Math.min(100, Math.max(0, Math.round(hit.similarity * 100)))}%
                  </span>
                )}
              </div>

              <p className="text-foreground/90 leading-relaxed text-xs bg-background/80 p-3 rounded-lg border border-border/60 font-sans text-right">
                <Quote className="size-3 text-primary/40 inline-block ml-1.5 -mt-1" />
                {hit.text}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
