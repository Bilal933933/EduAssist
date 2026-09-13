---
name: arabic-rtl-ui
description: RTL layout patterns, Arabic typography, ICU pluralization, font loading (Noto Kufi, Amiri), text direction handling for Arabic RTL interfaces. Use when building or modifying Arabic RTL UIs with Tailwind v4 and shadcn/ui.
---

# Arabic RTL UI

دليل شامل لبناء واجهات عربية RTL صحيحة مع Tailwind v4، shadcn/ui، و Next.js 16.

## الأساسيات: HTML و CSS

```tsx
// app/layout.tsx - الجذر
<html lang="ar" dir="rtl" className="scroll-smooth">
  <head>
    {/* Preload Arabic fonts */}
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
    <link
      href="https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@300;400;500;600;700&family=Amiri:wght@400;700&family=Cairo:wght@300;400;500;600;700&display=swap"
      rel="stylesheet"
    />
  </head>
  <body className="font-arabic antialiased bg-background text-foreground">
    {children}
  </body>
</html>
```

```css
/* app/globals.css - CSS Variables للـ RTL */
@theme {
  --font-family-arabic: "Noto Kufi Arabic", "Amiri", "Cairo", system-ui, sans-serif;
  --font-family-sans: "Inter", var(--font-family-arabic);
  --leading-arabic: 2;           /* Arabic needs taller line height */
  --leading-arabic-relaxed: 2.25;
}
```

## Tailwind v4 RTL Utilities

```tsx
// استخدام الـ logical properties (موصى به)
<div className="ms-4 me-2 ps-6 pe-3 rounded-s-lg rounded-e-md border-s-4 border-primary">
  {/* ms = margin-inline-start, me = margin-inline-end */}
  {/* ps = padding-inline-start, pe = padding-inline-end */}
  {/* rounded-s = rounded-start, rounded-e = rounded-end */}
  {/* border-s = border-inline-start, border-e = border-inline-end */}
</div>

// Direction-aware utilities
<div className="rtl:rotate-180 ltr:rotate-0">
  <ArrowRightIcon /> {/* تقلب تلقائياً في RTL */}
</div>

// Flex/Grid direction
<div className="flex flex-row-reverse rtl:flex-row"> {/* أو استخدم logical */}
<div className="flex items-start justify-end rtl:justify-start">
```

## الشائع: RTL-aware Components

```tsx
// components/ui/rtl-aware.tsx
import { cn } from "@/lib/utils";

export function RTLBox({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      dir="rtl"
      className={cn("rtl", className)}
      {...props}
    >
      {children}
    </div>
  );
}

// Icon wrapper يقلب الأيقونات الاتجاهية
export function RTLIcon({ children, className, ...props }: React.SVGAttributes<SVGSVGElement>) {
  return (
    <span className={cn("inline-flex rtl:rotate-180", className)} {...props}>
      {children}
    </span>
  );
}

// Input مع placeholder RTL
export function RTLInput({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      dir="rtl"
      className={cn("text-right placeholder:text-muted-foreground", className)}
      {...props}
    />
  );
}
```

## ICU MessageFormat للجمع العربي

```tsx
// lib/i18n.ts
import { MessageFormat } from "@formatjs/icu-messageformat-parser";
// أو استخدم intl-messageformat

const messages = {
  itemsCount: {
    zero: "لا يوجد عناصر",
    one: "عنصر واحد",
    two: "عنصران",
    few: "{count} عناصر",      // 3-10
    many: "{count} عنصراً",    // 11-99
    other: "{count} عنصر",     // 100+
  },
  lessonsCompleted: {
    zero: "لم تكمل أي درس",
    one: "أكملت درساً واحداً",
    two: "أكملت درسين",
    few: "أكملت {count} دروس",
    many: "أكملت {count} درساً",
    other: "أكملت {count} درس",
  },
};

function pluralCategory(count: number): "zero" | "one" | "two" | "few" | "many" | "other" {
  if (count === 0) return "zero";
  if (count === 1) return "one";
  if (count === 2) return "two";
  if (count >= 3 && count <= 10) return "few";
  if (count >= 11 && count <= 99) return "many";
  return "other";
}

export function t(key: keyof typeof messages, count: number, params?: Record<string, string>) {
  const msg = messages[key];
  const category = pluralCategory(count);
  let text = msg[category] || msg.other;
  return text.replace(/{count}/g, count.toLocaleString("ar-EG")).replace(/{(\w+)}/g, (_, k) => params?.[k] || "");
}

// الاستخدام
{t("itemsCount", 5)}      // "5 عناصر"
{t("itemsCount", 1)}      // "عنصر واحد"
{t("itemsCount", 2)}      // "عنصران"
{t("itemsCount", 15)}     // "15 عنصراً"
{t("itemsCount", 105)}    // "105 عنصر"
```

## Font Loading Optimization

```tsx
// app/fonts.ts
import { Noto_Kufi_Arabic, Amiri, Cairo, Inter } from "next/font/google";

export const notoKufi = Noto_Kufi_Arabic({
  subsets: ["arabic"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-noto-kufi",
  display: "swap",
  preload: true,
});

export const amiri = Amiri({
  subsets: ["arabic"],
  weight: ["400", "700"],
  variable: "--font-amiri",
  display: "swap",
});

export const cairo = Cairo({
  subsets: ["arabic"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-cairo",
  display: "swap",
});

export const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

// app/layout.tsx
import { notoKufi, amiri, cairo, inter } from "./fonts";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl" className={`${notoKufi.variable} ${amiri.variable} ${cairo.variable} ${inter.variable}`}>
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
```

```css
/* app/globals.css - استخدام المتغيرات */
@theme {
  --font-family-arabic: var(--font-noto-kufi), var(--font-amiri), var(--font-cairo), system-ui, sans-serif;
  --font-family-sans: var(--font-inter), var(--font-family-arabic);
}
```

## شريط التنقل RTL (Navbar)

```tsx
// components/layout/navbar.tsx
import { cn } from "@/lib/utils";
import { Menu, X, ChevronLeft, ChevronRight } from "lucide-react";

export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { href: "/", label: "الرئيسية", icon: Home },
    { href: "/chat", label: "محادثة", icon: MessageCircle },
    { href: "/lessons", label: "الدروس", icon: BookOpen },
    { href: "/progress", label: "التقدم", icon: BarChart },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <nav className="mx-auto flex max-w-7xl items-center justify-between p-4" dir="rtl">
        {/* Logo - على اليمين في RTL */}
        <Link href="/" className="flex items-center gap-2 font-bold text-xl text-foreground">
          <span className="text-primary">مساعد</span> النحو
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex md:items-center md:gap-6">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden p-2 rounded-lg text-muted-foreground hover:bg-accent"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label={mobileMenuOpen ? "إغلاق القائمة" : "فتح القائمة"}
          aria-expanded={mobileMenuOpen}
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </nav>

      {/* Mobile Menu Sheet */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border bg-background animate-slide-down">
          <nav className="px-4 py-4 space-y-2" dir="rtl">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-base font-medium text-foreground hover:bg-accent"
                onClick={() => setMobileMenuOpen(false)}
              >
                <item.icon className="w-5 h-5" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
```

## الشائعات الشائعة والحلول

| المشكلة | الحل |
|----------|-------|
| الأيقونات لا تقلب | استخدم `rtl:rotate-180` على الأيقونات الاتجاهية فقط |
| Flexbox يعكس الترتيب | استخدم `flex-row-reverse` مع `rtl:flex-row` أو logical properties |
| `margin-left` لا يعمل | استخدم `ms-` (margin-inline-start) بدلاً من `ml-` |
| `text-left` لا يعمل | استخدم `text-start` / `text-end` |
| `rounded-l` / `rounded-r` | استخدم `rounded-s` / `rounded-e` |
| `border-l` / `border-r` | استخدم `border-s` / `border-e` |
| Scrollbar على اليسار | `dir="rtl"` على `html` يضعها تلقائياً على اليسار |

## shadcn/ui RTL Adaptations

```tsx
// components/ui/dropdown-menu.tsx - تعديل القائمة المنسدلة
<DropdownMenuContent
  className="min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md
    rtl:origin-top-right ltr:origin-top-left
    data-[side=bottom]:slide-in-from-top-2
    data-[side=left]:slide-in-from-right-2
    data-[side=right]:slide-in-from-left-2
    data-[side=top]:slide-in-from-bottom-2"
  sideOffset={5}
>
  {/* المحتوى */}
</DropdownMenuContent>

// Tooltip positioning
<TooltipContent
  className="z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md
    rtl:origin-top-right ltr:origin-top-left"
  sideOffset={5}
>
  {/* المحتوى */}
</TooltipContent>

// Dialog - لا يحتاج تعديل، يعمل تلقائياً مع dir="rtl" على html
```

## مفاتيح التشغيل
- `rtl`، `arabic`، `direction`، `بوسترب`، `Noto Kufi`، `Amiri`، `Cairo`، `ICU`، `plural`، `logical properties`، `font loading`، `shadcn rtl`