import { AppNav } from "@/components/edu/app-nav";
import { AuthGate } from "@/components/auth/auth-gate";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGate>
      <div className="min-h-dvh bg-background flex">
        <AppNav />
        <div className="flex-1 min-w-0 flex flex-col">
          <div className="flex-1 pb-16 md:pb-0">{children}</div>
        </div>
        <AppNav mobile />
      </div>
    </AuthGate>
  );
}
