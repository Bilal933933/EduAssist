"use client";

import { User } from "lucide-react";
import { ChatMessage } from "@/lib/types";

interface UserMessageProps {
  message: ChatMessage;
  formattedTime: string | null;
}

export function UserMessage({ message, formattedTime }: UserMessageProps) {
  return (
    <div className="flex justify-start items-start gap-3 my-4 group">
      <div className="size-9 rounded-full bg-primary/15 text-primary flex items-center justify-center shrink-0 mt-0.5 border border-primary/25 shadow-xs">
        <User className="size-4" />
      </div>
      <div className="flex flex-col items-end max-w-[85%] sm:max-w-[75%]" dir="rtl">
        <div 
          className="bg-primary text-white !text-white px-5 py-3.5 rounded-2xl rounded-tr-none shadow-md text-sm sm:text-base leading-relaxed break-words font-medium text-right w-full"
          style={{ color: '#ffffff', backgroundColor: 'var(--primary)' }}
        >
          {message.content}
        </div>
        {formattedTime && (
          <span className="text-[11px] text-muted-foreground mt-1.5 px-1 opacity-70 font-medium">
            {formattedTime}
          </span>
        )}
      </div>
    </div>
  );
}
