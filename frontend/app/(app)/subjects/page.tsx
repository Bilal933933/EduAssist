import Link from "next/link";
import { BookOpen, Calculator, FlaskConical, Globe, Languages } from "lucide-react";

const SUBJECTS = [
  { id: "arabic", name: "اللغة العربية", units: 4, lessons: "8/14", icon: BookOpen },
  { id: "math", name: "الرياضيات", units: 5, lessons: "6/18", icon: Calculator },
  { id: "science", name: "العلوم", units: 3, lessons: "4/12", icon: FlaskConical },
  { id: "social", name: "الدراسات الاجتماعية", units: 3, lessons: "3/10", icon: Globe },
  { id: "english", name: "اللغة الإنجليزية", units: 4, lessons: "5/12", icon: Languages },
];

export default function SubjectsPage() {
  return (
    <div className="container py-6 space-y-6">
      <div>
        <h1 className="text-xl font-extrabold">موادك الدراسية</h1>
        <p className="text-sm text-muted-foreground mt-1">اختر مادة للمتابعة — المنهج كامل مع المساعد</p>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {SUBJECTS.map((s) => (
          <Link key={s.id} href={`/subjects/${s.id}`} className="border border-border rounded-2xl p-5 bg-card hover:shadow-md hover:border-primary/30 transition-all group">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <s.icon className="size-5" />
              </div>
              <div>
                <p className="font-bold text-sm">{s.name}</p>
                <p className="text-xs text-muted-foreground">{s.units} وحدات • {s.lessons} درس</p>
              </div>
            </div>
            <div className="mt-4 h-1.5 bg-secondary rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full" style={{ width: s.id === "arabic" ? "60%" : "35%" }} />
            </div>
            <p className="text-xs text-muted-foreground mt-2">آخر درس: {s.id === "arabic" ? "كان وأخواتها" : "الوحدة الثانية"}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
