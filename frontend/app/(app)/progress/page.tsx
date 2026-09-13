import { TrendingUp, CheckCircle2, AlertTriangle } from "lucide-react";

export default function ProgressPage() {
  return (
    <div className="container py-6 space-y-6">
      <h1 className="text-xl font-extrabold">سجلي كمدرس</h1>
      <p className="text-sm text-muted-foreground">تغطية تحضيرك للمنهج من مصادرك الحقيقية — ليس بيانات تجريبية</p>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="border border-border rounded-2xl p-5 bg-card text-center">
          <p className="text-3xl font-extrabold">8 / 14</p>
          <p className="text-xs text-muted-foreground mt-1">خطة محضرة للثالث الإعدادي</p>
          <div className="h-2 bg-secondary rounded-full mt-3 overflow-hidden"><div className="h-full bg-primary rounded-full" style={{ width: "57%" }} /></div>
          <p className="text-[11px] text-muted-foreground mt-2">من منهج اللغة العربية الحقيقي</p>
        </div>
        <div className="border border-border rounded-2xl p-5 bg-card">
          <p className="font-bold text-sm">إنجازك كمدرس</p>
          <p className="text-sm mt-2">حضّرت 8 خطط دروس</p>
          <p className="text-sm">4 سير حصص كاملة</p>
          <p className="text-sm">ناقشت 12 أسلوب تدريس</p>
        </div>
        <div className="border border-primary/20 bg-primary/5 rounded-2xl p-5">
          <p className="font-bold text-sm flex items-center gap-1"><TrendingUp className="size-4" /> مساعدك يقترح</p>
          <p className="text-sm mt-2">حضّر درس الحال — لم تحضّره بعد</p>
          <button className="mt-3 w-full bg-primary text-primary-foreground rounded-full py-2 text-sm font-bold">حضّر الآن</button>
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        <div className="border border-border rounded-2xl p-5 bg-card">
          <p className="font-bold text-sm flex items-center gap-2"><CheckCircle2 className="size-4 text-emerald-600" /> دروس حضرتها</p>
          <p className="text-sm mt-3">✓ كان وأخواتها ✓ المبتدأ والخبر ✓ الفاعل</p>
        </div>
        <div className="border border-amber-500/20 bg-amber-500/5 rounded-2xl p-5">
          <p className="font-bold text-sm flex items-center gap-2"><AlertTriangle className="size-4 text-amber-600" /> لم تحضّر بعد</p>
          <p className="text-sm mt-3">○ الحال ○ التمييز ○ المفعول لأجله</p>
        </div>
      </div>
    </div>
  );
}
