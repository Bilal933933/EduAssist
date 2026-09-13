export function toArabicStepLabel(raw: string): string {
  const t = (raw || "").trim();
  if (!t) return "";
  const low = t.toLowerCase();
  if (low.includes("searchchunks") || low.includes("search") || t.includes("يبحث"))
    return "أبحث في المصادر المعتمدة";
  if (low.includes("readfile") || low.includes("read") || t.includes("يقرأ") || t.includes("قراءة"))
    return "أقرأ أهم المقتطفات";
  if (low.includes("rerank") || low.includes("rrf") || low.includes("rank") || t.includes("ترتيب") || t.includes("صلة"))
    return "أرتب النتائج حسب الصلة";
  if (low.includes("generate") || t.includes("يولّد") || t.includes("يولد") || t.includes("الإجابة"))
    return "أصيغ الإجابة النهائية";
  if (t.includes("دورة") || low.includes("think") || t.includes("يفكر") || t.includes("يفكك"))
    return "أحلل السؤال وأخطط";
  if (t.includes("يراجع")) return "أراجع صلة الأدلة";
  return t.replace(/searchChunks|readFile/gi, "").replace(/\s{2,}/g, " ").trim() || t;
}

export function summarizeSteps(labels: string[]): string[] {
  const mapped = labels.map(toArabicStepLabel).filter(Boolean);
  const uniq: string[] = [];
  for (const l of mapped) {
    if (!uniq.includes(l)) uniq.push(l);
    if (uniq.length >= 5) break;
  }
  return uniq.slice(0, 5);
}
