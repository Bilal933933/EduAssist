"use client";

import React from "react";

interface FormattedTextProps {
  content: string;
}

export function FormattedText({ content }: FormattedTextProps) {
  // Split into lines
  const lines = content.split("\n");

  return (
    <div className="space-y-2 text-foreground leading-relaxed text-sm sm:text-base">
      {lines.map((line, idx) => {
        const trimmed = line.trim();

        if (!trimmed) {
          return <div key={idx} className="h-1.5" />;
        }

        // Header 1 / 2 / 3
        if (trimmed.startsWith("### ")) {
          return (
            <h4 key={idx} className="text-base font-bold text-primary mt-3 mb-1">
              {parseInline(trimmed.replace(/^###\s+/, ""))}
            </h4>
          );
        }
        if (trimmed.startsWith("## ")) {
          return (
            <h3 key={idx} className="text-lg font-bold text-primary mt-4 mb-1 border-b border-primary/10 pb-1">
              {parseInline(trimmed.replace(/^##\s+/, ""))}
            </h3>
          );
        }
        if (trimmed.startsWith("# ")) {
          return (
            <h2 key={idx} className="text-xl font-extrabold text-primary mt-4 mb-2">
              {parseInline(trimmed.replace(/^#\s+/, ""))}
            </h2>
          );
        }

        // Bullet lists (* or -)
        if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
          const listText = trimmed.replace(/^[\*\-]\s+/, "");
          return (
            <div key={idx} className="flex items-start gap-2 pr-2 my-1">
              <span className="size-1.5 rounded-full bg-primary mt-2 shrink-0" />
              <div className="flex-1">{parseInline(listText)}</div>
            </div>
          );
        }

        // Numbered list (e.g. 1. or 2.)
        const numberedMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
        if (numberedMatch) {
          const num = numberedMatch[1];
          const listText = numberedMatch[2];
          return (
            <div key={idx} className="flex items-start gap-2.5 pr-1 my-1.5">
              <span className="size-5 rounded-md bg-primary/10 text-primary font-bold text-xs flex items-center justify-center shrink-0 mt-0.5 border border-primary/20">
                {num}
              </span>
              <div className="flex-1">{parseInline(listText)}</div>
            </div>
          );
        }

        // Quotes «...» or >
        if (trimmed.startsWith("> ")) {
          return (
            <blockquote key={idx} className="border-r-4 border-primary/60 bg-primary/5 px-4 py-2 rounded-l-lg my-2 font-serif text-primary/90 italic">
              {parseInline(trimmed.replace(/^>\s+/, ""))}
            </blockquote>
          );
        }

        return (
          <p key={idx} className="leading-relaxed">
            {parseInline(trimmed)}
          </p>
        );
      })}
    </div>
  );
}

// Helper to parse **bold**, *italic*, `code`, and «Arabic quotes» with nested support
function parseInline(text: string): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  let remaining = text;
  let keyIdx = 0;

  while (remaining.length > 0) {
    // Bold **text**
    const boldMatch = remaining.match(/\*\*(.*?)\*\*/);
    // Quotes «text»
    const quoteMatch = remaining.match(/«(.*?)»/);

    // Find earliest match
    let firstMatchIndex = Infinity;
    let matchType: "bold" | "quote" | null = null;
    let currentMatch: RegExpMatchArray | null = null;

    if (boldMatch && boldMatch.index! < firstMatchIndex) {
      firstMatchIndex = boldMatch.index!;
      matchType = "bold";
      currentMatch = boldMatch;
    }

    if (quoteMatch && quoteMatch.index! < firstMatchIndex) {
      firstMatchIndex = quoteMatch.index!;
      matchType = "quote";
      currentMatch = quoteMatch;
    }

    if (!matchType || !currentMatch) {
      parts.push(remaining);
      break;
    }

    // Push text before match
    if (firstMatchIndex > 0) {
      parts.push(remaining.substring(0, firstMatchIndex));
    }

    const matchedContent = currentMatch[1];

    if (matchType === "bold") {
      parts.push(
        <strong key={keyIdx++} className="font-bold text-foreground bg-primary/5 px-1 py-0.5 rounded">
          {parseInline(matchedContent)}
        </strong>
      );
    } else if (matchType === "quote") {
      parts.push(
        <span key={keyIdx++} className="font-semibold text-emerald-800 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/50 px-1.5 py-0.5 rounded border border-emerald-200/60 dark:border-emerald-800/60">
          «{parseInline(matchedContent)}»
        </span>
      );
    }

    remaining = remaining.substring(firstMatchIndex + currentMatch[0].length);
  }

  return parts;
}
