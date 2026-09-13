import type { Metadata } from "next";
import { IBM_Plex_Sans_Arabic } from "next/font/google";
import { Direction } from "radix-ui";
import { Providers } from "./providers";
import "./globals.css";

const ibmPlexArabic = IBM_Plex_Sans_Arabic({
  subsets: ["arabic", "latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-arabic",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "EduAssist — مساعدي الذكي للتعلّم",
    template: "%s | EduAssist",
  },
  description: "EduAssist — مساعدك الذكي للتعلّم في المدرسة. يفهم منهجك، يشرح لك، يحل معك، ويختبر فهمك. Learn smarter. Understand better.",
  keywords: ["EduAssist", "مساعدي", "تعليم ذكي", "مساعد مدرسة", "RAG"],
  authors: [{ name: "EduAssist" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" className={ibmPlexArabic.variable} suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased selection:bg-primary/20 selection:text-primary">
        <Direction.Provider dir="rtl">
          <Providers>{children}</Providers>
        </Direction.Provider>
      </body>
    </html>
  );
}
