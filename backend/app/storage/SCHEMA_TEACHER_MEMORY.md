# مخطط ذاكرة المدرس (M1/M2)

## الجداول

| جدول | الغرض |
|------|--------|
| `grades` | بُعد معياري للصف (code, label_ar, stage, level_order) |
| `teachers` | كيان المدرس (UUID + external_key للتوافق مع default) |
| `teacher_grade_assignments` | صفوف المدرس (many-to-many) |
| `teacher_preferences` | تفضيلات أسلوب (صف واحد لكل مدرس) |
| `teacher_topic_stats` | إحصاء المواضيع المتكررة |
| `teacher_mistakes_v2` | أخطاء شائعة (grade_id + normalized_key) |
| `teacher_lesson_events` | أحداث تحضير/نقاش خفيفة للـ Agent |

## تدفق الحقن

```
teacher_key + current_grade_text
  → teachers.external_key
  → grades عبر قاموس المطابقة
  → mistakes/events مفلترة بـ grade_id
  → prompt block
```

## ملاحظات

- `external_key='default'` يبقى مدعوماً حتى ربط المصادقة.
- أخطاء NULL grade تُعرض كاحتياطي عند طلب صف محدد.
- النبرة الافتراضية: احترافي.
