"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, BookOpen, Sparkles, BarChart3, MessageCircle, User } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "الرئيسية", icon: LayoutDashboard },
  { href: "/subjects", label: "المواد", icon: BookOpen },
  { href: "/assistant", label: "مساعدي", icon: Sparkles, primary: true },
  { href: "/progress", label: "تقدمي", icon: BarChart3 },
];

export function AppNav({ mobile = false }: { mobile?: boolean }) {
  const pathname = usePathname();
  if (mobile) {
    return (
      <nav className="fixed bottom-0 inset-x-0 z-40 bg-card border-t border-border flex justify-around py-2 pb-[calc(0.5rem+env(safe-area-inset-bottom))] md:hidden">
        {NAV.map((item) => {
          const active = pathname?.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-col items-center gap-1 px-3 py-1 rounded-xl text-xs font-medium transition-colors",
                active ? "text-primary" : "text-muted-foreground",
                item.primary && active && "bg-primary text-primary-foreground px-4"
              )}
            >
              <Icon className={cn("size-5", item.primary && active && "size-5")} />
              <span className="text-[11px]">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    );
  }
  return (
    <aside className="hidden md:flex w-[240px] shrink-0 flex-col border-l border-border bg-card">
      <div className="h-16 flex items-center gap-2 px-5 border-b border-border">
        <div className="size-8 rounded-xl bg-primary text-primary-foreground flex items-center justify-center font-bold text-sm">م</div>
        <div>
          <p className="font-bold text-sm leading-none">EduAssist</p>
          <p className="text-[11px] text-muted-foreground">مساعدي الذكي</p>
        </div>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {NAV.map((item) => {
          const active = pathname?.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors",
                active ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                item.primary && !active && "border border-primary/20"
              )}
            >
              <Icon className="size-[18px]" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-3 border-t border-border">
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="size-8 rounded-full bg-secondary flex items-center justify-center"><User className="size-4" /></div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">أحمد</p>
            <p className="text-xs text-muted-foreground">الصف الثالث الإعدادي</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
