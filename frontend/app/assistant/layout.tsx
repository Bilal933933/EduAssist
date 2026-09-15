import { AssistantShell } from "@/components/chat/assistant-shell";

// تخطيط مسار المساعد: سايدبار التنقل ثابت + محتوى الصفحة (جديدة أو محفوظة).
export default function AssistantLayout({ children }: { children: React.ReactNode }) {
  return <AssistantShell>{children}</AssistantShell>;
}
