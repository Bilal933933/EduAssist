import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * LessonStore - إدارة الدروس المحفوظة
 * يتعامل مع:
 * - حفظ واسترجاع الدروس
 * - البحث والتصفية
 * - التثبيت والحذف
 */

export interface SavedLesson {
  id: string;
  title: string;
  topic: string; // "الفاعل", "النعت", إلخ
  content: string;
  grade?: string; // "أول ثانوي", "ثالث ثانوي"
  subject?: string; // "نحو", "صرف"
  createdAt: Date;
  updatedAt: Date;
  isPinned: boolean;
  tags: string[]; // ["مهم", "للاختبار"]
  sourceMessageId?: string;
  notes?: string;
  isSynced?: boolean; // هل تم حفظها على السيرفر
}

interface LessonStore {
  // الحالة
  lessons: SavedLesson[];
  filteredLessons: SavedLesson[];
  searchQuery: string;
  selectedTopic: string | null;
  selectedGrade: string | null;
  isLoading: boolean;
  error: string | null;

  // الإجراءات
  addLesson: (lesson: Omit<SavedLesson, 'id' | 'createdAt' | 'updatedAt' | 'isPinned'>) => string;
  updateLesson: (id: string, updates: Partial<SavedLesson>) => void;
  deleteLesson: (id: string) => void;
  pinLesson: (id: string, pinned: boolean) => void;
  searchLessons: (query: string) => void;
  filterByTopic: (topic: string | null) => void;
  filterByGrade: (grade: string | null) => void;
  applyFilters: () => void;
  getLessonById: (id: string) => SavedLesson | undefined;
  getLessonsByTopic: (topic: string) => SavedLesson[];
  getPinnedLessons: () => SavedLesson[];
  getRecentLessons: (count: number) => SavedLesson[];
  clearLessons: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  syncWithServer: (lessons: SavedLesson[]) => void;
  exportLessons: (ids: string[], format: 'json' | 'pdf') => string;
}

export const useLessonStore = create<LessonStore>()(
  persist(
    (set, get) => ({
      // الحالة الابتدائية
      lessons: [],
      filteredLessons: [],
      searchQuery: '',
      selectedTopic: null,
      selectedGrade: null,
      isLoading: false,
      error: null,

      // إضافة درس جديد
      addLesson: (lesson) => {
        const id = `lesson_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const newLesson: SavedLesson = {
          ...lesson,
          id,
          createdAt: new Date(),
          updatedAt: new Date(),
          isPinned: false,
          isSynced: false,
        };

        set((state) => ({
          lessons: [newLesson, ...state.lessons],
        }));

        get().applyFilters();
        return id;
      },

      // تحديث درس
      updateLesson: (id: string, updates: Partial<SavedLesson>) => {
        set((state) => ({
          lessons: state.lessons.map((lesson) =>
            lesson.id === id
              ? { ...lesson, ...updates, updatedAt: new Date() }
              : lesson
          ),
        }));

        get().applyFilters();
      },

      // حذف درس
      deleteLesson: (id: string) => {
        set((state) => ({
          lessons: state.lessons.filter((lesson) => lesson.id !== id),
        }));

        get().applyFilters();
      },

      // تثبيت/فك تثبيت درس
      pinLesson: (id: string, pinned: boolean) => {
        set((state) => ({
          lessons: state.lessons.map((lesson) =>
            lesson.id === id ? { ...lesson, isPinned: pinned } : lesson
          ),
        }));

        get().applyFilters();
      },

      // البحث
      searchLessons: (query: string) => {
        set({ searchQuery: query });
        get().applyFilters();
      },

      // تصفية حسب الموضوع
      filterByTopic: (topic: string | null) => {
        set({ selectedTopic: topic });
        get().applyFilters();
      },

      // تصفية حسب الصف
      filterByGrade: (grade: string | null) => {
        set({ selectedGrade: grade });
        get().applyFilters();
      },

      // تطبيق جميع الفلاتر
      applyFilters: () => {
        const state = get();
        let filtered = [...state.lessons];

        // البحث
        if (state.searchQuery.trim()) {
          const query = state.searchQuery.toLowerCase();
          filtered = filtered.filter(
            (lesson) =>
              lesson.title.toLowerCase().includes(query) ||
              lesson.content.toLowerCase().includes(query) ||
              lesson.topic.toLowerCase().includes(query) ||
              lesson.tags.some((tag) => tag.toLowerCase().includes(query))
          );
        }

        // تصفية حسب الموضوع
        if (state.selectedTopic) {
          filtered = filtered.filter((lesson) => lesson.topic === state.selectedTopic);
        }

        // تصفية حسب الصف
        if (state.selectedGrade) {
          filtered = filtered.filter((lesson) => lesson.grade === state.selectedGrade);
        }

        // ترتيب: المثبتة أولاً، ثم الأحدث
        filtered.sort((a, b) => {
          if (a.isPinned !== b.isPinned) {
            return a.isPinned ? -1 : 1;
          }
          return b.updatedAt.getTime() - a.updatedAt.getTime();
        });

        set({ filteredLessons: filtered });
      },

      // الحصول على درس بـ ID
      getLessonById: (id: string) => {
        return get().lessons.find((lesson) => lesson.id === id);
      },

      // الحصول على الدروس حسب الموضوع
      getLessonsByTopic: (topic: string) => {
        return get().lessons.filter((lesson) => lesson.topic === topic);
      },

      // الحصول على الدروس المثبتة
      getPinnedLessons: () => {
        return get().lessons.filter((lesson) => lesson.isPinned);
      },

      // الحصول على أحدث الدروس
      getRecentLessons: (count: number) => {
        return get()
          .lessons.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
          .slice(0, count);
      },

      // مسح جميع الدروس
      clearLessons: () => {
        set({ lessons: [], filteredLessons: [] });
      },

      // تعيين حالة التحميل
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      // تعيين الخطأ
      setError: (error: string | null) => {
        set({ error });
      },

      // مزامنة مع السيرفر
      syncWithServer: (lessons: SavedLesson[]) => {
        set((state) => ({
          lessons: lessons.map((serverLesson) => ({
            ...serverLesson,
            isSynced: true,
          })),
        }));

        get().applyFilters();
      },

      // تصدير الدروس
      exportLessons: (ids: string[], format: 'json' | 'pdf') => {
        const lessonsToExport = get().lessons.filter((lesson) =>
          ids.includes(lesson.id)
        );

        if (format === 'json') {
          return JSON.stringify(lessonsToExport, null, 2);
        }

        // PDF سيتم التعامل معه عبر مكتبة خارجية
        return '';
      },
    }),
    {
      name: 'lesson-store',
      version: 1,
    }
  )
);
