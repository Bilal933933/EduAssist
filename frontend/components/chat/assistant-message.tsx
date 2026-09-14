"use client";

import { useMemo, useState } from "react";
import { Sparkles } from "lucide-react";
import { ChatMessage } from "@/lib/types";
import { AgentTrace } from "./agent-trace";
import { WorksheetSections } from "./worksheet-sections";
import { MarkdownRender } from "./markdown-render";
import { MessageActions } from "./message-actions";
import { LessonExtrasView } from "./lesson-extras-view";
import { MessageSources } from "./message-sources";
import { useWorksheetDetection } from "@/hooks/use-worksheet-detection";
import { useLessonExtras } from "@/hooks/use-lesson-extras";
import { useMessageClipboard } from "@/hooks/use-message-clipboard";

interface AssistantMessageProps {
  message: ChatMessage;
  formattedTime: string | null;
}

// وظيفة واحدة: تنسيق رسالة المساعد بأسلوب Gemini — بدون منطق كشف أو جلب داخلي.
export function AssistantMessage({ message, formattedTime }: AssistantMessageProps) {
  const [editing, setEditing] = useState(false);
  const [edited, setEdited] = useState<string | null>(null);
  const [draft, setDraft] = useState(message.content);

  const text = editing ? draft : edited ?? message.content;
  const { copied, copy, share } = useMessageClipboard(text);

  const { isWorksheet, isError } = useWorksheetDetection(text);
  const topic = useMemo(
    () => message.content.match(/درس\s+(\S+)/)?.[1] || message.hits?.[0]?.title || "الدرس",
    [message.content, message.hits]
  );
  const { cards, quiz, loading, load } = useLessonExtras(topic);

  const toggleEdit = () => {
    if (editing) setEdited(draft.trim() ? draft : null);
    else setDraft(edited ?? message.content);
    setEditing((v) => !v);
  };

  return (
    <div className="flex items-start gap-2 my-4" dir="rtl">
      <div className="size-7 rounded-full bg-muted text-foreground flex items-center justify-center shrink-0 mt-0.5">
        <Sparkles className="size-3.5" />
      </div>

      <div className="flex-1 min-w-0 max-w-3xl">
        {(message.trace?.length || message.streaming) && (
          <div className="mb-2">
            <AgentTrace
              steps={message.trace || []}
              isStreaming={!!message.streaming}
              durationMs={message.durationMs}
            />
          </div>
        )}

        {editing ? (
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={10}
            aria-label="تعديل الإجابة"
            className="w-full rounded-xl border border-input bg-background p-3 text-sm leading-7 outline-none focus:ring-2 focus:ring-ring"
          />
        ) : isWorksheet ? (
          <WorksheetSections content={text} />
        ) : (
          <MarkdownRender content={text} />
        )}

        <MessageActions
          copied={copied}
          editing={editing}
          loading={loading}
          isError={isError}
          onCopy={copy}
          onCards={() => load("cards")}
          onQuiz={() => load("quiz")}
          onPrint={() => window.print()}
          onToggleEdit={toggleEdit}
          onShare={share}
        />

        <LessonExtrasView cards={cards} quiz={quiz} />

        {(message.hits?.length ?? 0) > 0 && (
          <div className="mt-3">
            <MessageSources hits={message.hits || []} />
          </div>
        )}

        {formattedTime && (
          <p className="text-[11px] text-muted-foreground mt-2">{formattedTime}</p>
        )}
      </div>
    </div>
  );
}
