"use client";

import { ChatMessage } from "@/lib/types";
import { UserMessage } from "./user-message";
import { AssistantMessage } from "./assistant-message";

interface MessageItemProps {
  message: ChatMessage;
}

export function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === "user";

  const formattedTime = message.createdAt
    ? new Date(message.createdAt).toLocaleTimeString("ar-SA", {
        hour: "2-digit",
        minute: "2-digit",
      })
    : null;

  if (isUser) {
    return <UserMessage message={message} formattedTime={formattedTime} />;
  }

  return <AssistantMessage message={message} formattedTime={formattedTime} />;
}
