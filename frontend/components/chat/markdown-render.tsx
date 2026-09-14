"use client";

import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

// وظيفة واحدة: عرض Markdown بتنسيق Gemini نظيف — بدون منطق أو أزرار.
export function MarkdownRender({ content }: { content: string }) {
  return (
    <div dir="rtl" className="text-right text-sm leading-7 text-foreground">
      <Markdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h2 className="text-lg font-extrabold mt-5 mb-2 text-foreground">{children}</h2>
          ),
          h2: ({ children }) => (
            <h3 className="text-[15px] font-bold mt-5 mb-2 pb-1.5 border-b border-border text-foreground">{children}</h3>
          ),
          h3: ({ children }) => (
            <h4 className="text-sm font-bold mt-4 mb-1.5 text-foreground">{children}</h4>
          ),
          p: ({ children }) => <p className="my-2 leading-7">{children}</p>,
          ul: ({ children }) => (
            <ul className="my-3 space-y-2 pr-5 list-disc marker:text-foreground/40">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="my-3 space-y-2 pr-5 list-decimal marker:text-foreground/60 marker:font-semibold">{children}</ol>
          ),
          li: ({ children }) => <li className="leading-7 pl-1">{children}</li>,
          blockquote: ({ children }) => (
            <blockquote className="border-r-2 border-foreground/20 pr-4 my-3 text-foreground/80">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="my-4 overflow-x-auto rounded-xl border border-border">
              <table className="w-full text-sm">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="bg-muted/60 px-3 py-2 text-right font-bold border-b border-border">{children}</th>
          ),
          td: ({ children }) => (
            <td className="px-3 py-2 border-b border-border/50 align-top">{children}</td>
          ),
          code: ({ children }) => (
            <code dir="ltr" className="bg-muted px-1.5 py-0.5 rounded-md text-xs font-mono">
              {children}
            </code>
          ),
          pre: ({ children }) => (
            <pre dir="ltr" className="my-3 overflow-x-auto rounded-xl bg-muted/60 border border-border p-3 text-xs font-mono text-left">
              {children}
            </pre>
          ),
          hr: () => <hr className="my-6 border-border" />,
          strong: ({ children }) => <strong className="font-bold">{children}</strong>,
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noreferrer" className="underline underline-offset-4 hover:opacity-70">
              {children}
            </a>
          ),
        }}
      >
        {content}
      </Markdown>
    </div>
  );
}
