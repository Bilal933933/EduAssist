# 🎓 EduAssist - مساعدك التعليمي الذكي (نسخة محدثة)

## ✨ الميزات الجديدة المضافة

### 🏪 إدارة الحالة (State Management) مع Zustand
```typescript
// 5 Stores جديدة:
- useChatStore      // إدارة الرسائل والدردشات
- useLessonStore    // إدارة الدروس المحفوظة
- useNotesStore     // إدارة الملاحظات الشخصية
- useUIStore        // إدارة حالة الواجهة
- useQuestionsStore // إدارة الأسئلة المولدة
```

### 📚 نظام الدروس المحفوظة
```
الميزات:
✅ حفظ الدروس تلقائياً
✅ تثبيت الدروس المهمة
✅ البحث والتصفية حسب الموضوع/الصف
✅ ملاحظات شخصية لكل درس
✅ عرض تاريخ التحديث
```

### 🎯 توليد الأسئلة الذكية
```
الإمكانيات:
✅ اختيار مستوى الصعوبة (سهل/متوسط/صعب)
✅ اختيار نمط السؤال (اختيار متعدد/مقالي/صح/خطأ)
✅ شرح مفصل للإجابات الصحيحة
✅ ربط الأسئلة بالدروس
```

### 📝 الملاحظات الشخصية
```
الميزات:
✅ ملاحظة واحدة لكل درس
✅ حفظ تلقائي (Auto-save)
✅ تثبيت الملاحظات المهمة
✅ بحث في الملاحظات
```

### 🏗️ البنية المعمارية الجديدة

#### Frontend (Next.js)
```
app/
├── (app)/
│   ├── dashboard/       # لوحة التحكم الجديدة
│   └── assistant/       # الدردشة الرئيسية
│
components/
├── dashboard/           # مكونات Dashboard الجديدة
│   ├── lessons-grid.tsx
│   ├── lesson-card.tsx
│   ├── search-bar.tsx
│   └── filters.tsx
│
stores/                 # Zustand Stores (جديد)
├── chatStore.ts
├── lessonStore.ts
├── notesStore.ts
├── uiStore.ts
├── questionsStore.ts
└── index.ts

lib/api/
├── lessons.api.ts      # API Services للدروس
```

#### Realtime (NestJS)
```
database/
├── entities/           # ORM Entities
│   ├── lesson.entity.ts
│   ├── note.entity.ts
│   └── question.entity.ts
├── repositories/       # Repository Pattern
│   ├── lesson.repository.ts
│   └── question.repository.ts
└── migrations/         # Database Migrations

lessons/               # وحدة الدروس (جديدة)
├── lessons.service.ts
├── lessons.controller.ts
├── lessons.module.ts
└── dto/

common/
└── filters/
    └── global-exception.filter.ts
```

---

## 🚀 البدء السريع

### 1️⃣ التثبيت
```bash
# Frontend
cd frontend
npm install zustand immer

# Realtime
cd ../realtime
npm install typeorm pg class-validator class-transformer
npm install --save-dev @types/express

# Backend (اختياري - موجود بالفعل)
cd ../backend
pip install -r requirements.txt
```

### 2️⃣ قاعدة البيانات
```bash
cd realtime

# تشغيل migrations
npm run migration:run

# أو يدويًا (إذا لم تكن هناك CLI)
# استخدم ملف الـ Migration: 
# src/database/migrations/1693555200000-CreateLessonsTablesNotesQuestionsAndIndices.ts
```

### 3️⃣ تشغيل المشروع
```bash
# في 3 نوافذ منفصلة:

# النافذة 1: Frontend
cd frontend && npm run dev
# http://localhost:3000

# النافذة 2: Realtime
cd realtime && npm run start:dev
# http://localhost:3001

# النافذة 3: Backend (Python)
cd backend && python main.py
# http://localhost:8000
```

---

## 📖 استخدام Zustand Stores

### Chat Store
```typescript
import { useChatStore } from '@/stores';

// في Component
const { threads, messages, currentThreadId, createThread, addMessage } = useChatStore();

// إنشاء درس جديد
const threadId = createThread('درس الفاعل', 'النحو');

// إضافة رسالة
addMessage({
  id: 'msg-1',
  role: 'user',
  content: 'ما هو الفاعل؟',
  timestamp: new Date(),
});
```

### Lesson Store
```typescript
import { useLessonStore } from '@/stores';

// الحصول على الدروس
const { lessons, filteredLessons, addLesson, deleteLesson, searchLessons } = useLessonStore();

// إضافة درس
const lessonId = addLesson({
  title: 'درس الفاعل',
  topic: 'الفاعل',
  content: 'شرح مفصل...',
  tags: ['مهم'],
});

// البحث
searchLessons('فاعل');

// التصفية
filterByTopic('النحو');
```

### Notes Store
```typescript
import { useNotesStore } from '@/stores';

// إضافة ملاحظة
const { addNote, updateNote, deleteNote, getNote } = useNotesStore();

const noteId = addNote('lesson-id-123', 'ملاحظة مهمة جداً');

// تحديث
updateNote(noteId, 'ملاحظة محدثة');
```

### UI Store
```typescript
import { useUIStore } from '@/stores';

// إدارة الواجهة
const { theme, setTheme, toggleSidebar, setDifficulty } = useUIStore();

// تغيير المظهر
setTheme('dark');

// تعيين مستوى الصعوبة
setDifficulty('medium');
```

---

## 🔌 API Endpoints الجديدة

### Lessons API
```
POST   /api/lessons                 # إنشاء درس
GET    /api/lessons                 # جميع الدروس
GET    /api/lessons/:id             # درس واحد
GET    /api/lessons/pinned          # الدروس المثبتة
GET    /api/lessons/recent          # أحدث الدروس
GET    /api/lessons/search          # البحث
PATCH  /api/lessons/:id             # تحديث درس
PATCH  /api/lessons/:id/notes       # تحديث الملاحظات
PATCH  /api/lessons/:id/pin         # تثبيت/فك تثبيت
DELETE /api/lessons/:id             # حذف درس
GET    /api/lessons/statistics      # الإحصائيات
```

### Questions API (الخاص بالتوليد - قريباً)
```
POST   /api/questions/generate      # توليد أسئلة
GET    /api/questions               # جميع الأسئلة
GET    /api/questions/by-lesson/:id # أسئلة درس معين
```

---

## 🗄️ المسح الأول للقاعدة

جداول جديدة تم إنشاؤها:

```sql
-- جدول الدروس
CREATE TABLE lessons (
  id UUID PRIMARY KEY,
  teacherId UUID NOT NULL,
  title VARCHAR(255),
  content TEXT,
  topic VARCHAR(100),
  grade VARCHAR(50),
  subject VARCHAR(100),
  notes TEXT,
  isPinned BOOLEAN DEFAULT FALSE,
  tags VARCHAR[],
  createdAt TIMESTAMP,
  updatedAt TIMESTAMP
);

-- جدول الملاحظات
CREATE TABLE lesson_notes (
  id UUID PRIMARY KEY,
  lessonId UUID UNIQUE,
  teacherId UUID,
  content TEXT,
  isPinned BOOLEAN,
  createdAt TIMESTAMP,
  updatedAt TIMESTAMP
);

-- جدول الأسئلة
CREATE TABLE generated_questions (
  id UUID PRIMARY KEY,
  lessonId UUID,
  teacherId UUID,
  questionText TEXT,
  type VARCHAR(50),
  difficulty VARCHAR(50),
  topic VARCHAR(100),
  options JSONB,
  correctAnswer TEXT,
  explanation TEXT,
  isUsed BOOLEAN,
  createdAt TIMESTAMP,
  updatedAt TIMESTAMP
);
```

---

## ⚙️ الإعدادات المطلوبة

### .env.local (Frontend)
```env
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_SOCKET_URL=http://localhost:3001
```

### .env (Realtime)
```env
NODE_ENV=development
PORT=3001
DATABASE_URL=postgresql://user:password@localhost:5432/eduassist
JWT_SECRET=your-secret-key
```

### .env (Backend)
```env
GEMINI_API_KEY=your-gemini-key
DATABASE_URL=postgresql://...
```

---

## 🎯 الخطوات التالية

### المرحلة 1 (القادمة)
- [ ] API لتوليد الأسئلة الذكية
- [ ] API للشروحات المتدرجة
- [ ] تحسين Dashboard

### المرحلة 2
- [ ] Export للـ PDF
- [ ] Sync مع السيرفر
- [ ] Mobile App

### المرحلة 3 (للـ SaaS)
- [ ] Multi-tenant support
- [ ] Role-based access
- [ ] Billing integration

---

## 🐛 المعروف والمشاكل

- ⚠️ معرف المعلم مؤقتاً (يجب ربطه بـ JWT)
- ⚠️ لا يوجد تصريح (auth) في الـ Controllers
- ⚠️ Storage الـ localStorage (حاليًا - يمكن التبديل للسيرفر)

---

## 📚 الموارد الإضافية

- [Zustand Docs](https://github.com/pmndrs/zustand)
- [NestJS Docs](https://docs.nestjs.com)
- [TypeORM Docs](https://typeorm.io)
- [Next.js Docs](https://nextjs.org/docs)

---

**تاريخ التحديث:** أغسطس 2024  
**الإصدار:** 0.2.0  
**المراحل المكتملة:** 1/3 ✅

---

هل تحتاج إلى توضيحات إضافية؟ 🚀
