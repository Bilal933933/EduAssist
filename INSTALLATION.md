# 📦 الحزم المطلوبة للتثبيت

## Frontend
```bash
cd frontend
npm install zustand immer
```

## Realtime (NestJS)
```bash
cd realtime
npm install typeorm pg class-validator class-transformer
npm install --save-dev @types/express
```

## Backend (Python)
```bash
cd backend
pip install -r requirements.txt
```

---

## 📋 قائمة الملفات الجديدة المضافة:

### Frontend (Zustand Stores)
- ✅ stores/chatStore.ts
- ✅ stores/lessonStore.ts
- ✅ stores/notesStore.ts
- ✅ stores/uiStore.ts
- ✅ stores/questionsStore.ts
- ✅ stores/index.ts
- ✅ components/dashboard/lessons-grid.tsx
- ✅ components/dashboard/lesson-card.tsx
- ✅ components/dashboard/search-bar.tsx
- ✅ components/dashboard/filters.tsx
- ✅ lib/api/lessons.api.ts

### Realtime (NestJS)
- ✅ database/entities/lesson.entity.ts
- ✅ database/entities/note.entity.ts
- ✅ database/entities/question.entity.ts
- ✅ database/repositories/lesson.repository.ts
- ✅ database/repositories/question.repository.ts
- ✅ database/migrations/1693555200000-CreateLessonsTablesNotesQuestionsAndIndices.ts
- ✅ lessons/lessons.service.ts
- ✅ lessons/dto/index.ts
- ✅ lessons/lessons.controller.ts
- ✅ lessons/lessons.module.ts
- ✅ common/filters/global-exception.filter.ts
