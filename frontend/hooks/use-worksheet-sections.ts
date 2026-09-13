import { useMemo } from "react";

export interface WorksheetSection {
  id: string;
  title: string;
  body: string;
}

// وظيفة واحدة: تقسيم نص الورقة إلى أقسام حسب العناوين — بدون أي عرض.
export function useWorksheetSections(content: string): WorksheetSection[] {
  return useMemo(() => {
    const lines = content.split("\n");
    const sections: WorksheetSection[] = [];
    let current: WorksheetSection = { id: "intro", title: "المقدمة", body: "" };
    let idx = 0;
    for (const line of lines) {
      const t = line.trim();
      if (/^#{1,3}\s+/.test(t)) {
        if (current.body.trim() || idx > 0) sections.push(current);
        idx += 1;
        current = { id: `sec-${idx}`, title: t.replace(/^#{1,3}\s+/, ""), body: "" };
      } else {
        current.body += line + "\n";
      }
    }
    if (current.body.trim() || current.title !== "المقدمة") sections.push(current);
    if (sections.length === 0) return [{ id: "all", title: "المحتوى", body: content }];
    if (sections.length > 1 && sections[0].id === "intro" && !sections[0].body.trim()) {
      return sections.slice(1);
    }
    return sections;
  }, [content]);
}
