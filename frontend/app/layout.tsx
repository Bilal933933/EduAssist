import type { Metadata, Viewport } from "next";
import { IBM_Plex_Sans_Arabic } from "next/font/google";
import { Direction } from "radix-ui";
import { Providers } from "./providers";
import { PwaRegister } from "@/components/pwa-register";
import "./globals.css";

const ibmPlexArabic = IBM_Plex_Sans_Arabic({
  subsets: ["arabic", "latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-arabic",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "EduAssist — مساعد المدرس الذكي",
    template: "%s | EduAssist",
  },
  description: "EduAssist — مساعدك لتحضير الدروس وخطط الشرح وسير الحصة من مصادرك الخاصة، بحث عميق في محتواك وإجابات موثقة بالمصادر.",
  keywords: ["EduAssist", "مساعد المدرس", "تحضير دروس", "خطة شرح", "سير حصة", "RAG"],
  authors: [{ name: "EduAssist" }],
  manifest: "/manifest.json",
  icons: {
    icon: "/icon.svg",
    apple: "/icon.svg",
  },
  appleWebApp: {
    capable: true,
    title: "EduAssist",
    statusBarStyle: "default",
  },
};

export const viewport: Viewport = {
  themeColor: "#0f766e",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" className={ibmPlexArabic.variable} suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased selection:bg-primary/20 selection:text-primary">
        <PwaRegister />
        <Direction.Provider dir="rtl">
          <Providers>{children}</Providers>
        </Direction.Provider>
      </body>
    </html>
  );
}
