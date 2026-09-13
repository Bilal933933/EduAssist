"use client";

import { ChatMessage } from "@/lib/types";

interface UserMessageProps {
  message: ChatMessage;
  formattedTime: string | null;
}

// وظيفة واحدة: فقاعة المستخدم بأسلوب Gemini — بدون أفاتار أو ظل.
export function UserMessage({ message, formattedTime }: UserMessageProps) {
  return (
    <div className="flex justify-start my-4" dir="rtl">
      <div className="max-w-[92%] sm:max-w-[80%]">
        <div className="bg-muted px-4 py-2 rounded-2xl text-sm leading-7 break-words text-foreground text-right">
          {message.content}
        </div>
        {formattedTime && (
          <p className="text-[11px] text-muted-foreground mt-1 px-2">{formattedTime}</p>
        )}
      </div>
    </div>
  );
}
