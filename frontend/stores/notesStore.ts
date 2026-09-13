import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * NotesStore - إدارة الملاحظات الشخصية على الدروس
 * يتعامل مع:
 * - إنشاء وتعديل الملاحظات
 * - حفظ سريع (Auto-save)
 * - البحث في الملاحظات
 */

export interface Note {
  id: string;
  lessonId: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
  isSynced?: boolean;
  isPinned?: boolean;
}

interface NotesStore {
  // الحالة
  notes: Map<string, Note>; // مفتاح: lessonId, قيمة: Note
  allNotes: Note[]; // قائمة بسيطة من كل الملاحظات
  isDirty: Map<string, boolean>; // تتبع الملاحظات غير المحفوظة
  lastSavedTime: Map<string, Date>; // آخر وقت حفظ لكل ملاحظة

  // الإجراءات
  addNote: (lessonId: string, content: string) => string;
  updateNote: (noteId: string, content: string) => void;
  deleteNote: (noteId: string, lessonId: string) => void;
  getNote: (lessonId: string) => Note | undefined;
  getNotesByLessonId: (lessonId: string) => Note | undefined;
  getAllNotes: () => Note[];
  searchNotes: (query: string) => Note[];
  pinNote: (noteId: string, pinned: boolean) => void;
  getPinnedNotes: () => Note[];
  markAsSynced: (noteId: string) => void;
  markAsDirty: (noteId: string) => void;
  clearNotes: () => void;
  exportNotes: (format: 'json' | 'txt') => string;
  getUnsyncedNotes: () => Note[];
}

export const useNotesStore = create<NotesStore>()(
  persist(
    (set, get) => ({
      // الحالة الابتدائية
      notes: new Map(),
      allNotes: [],
      isDirty: new Map(),
      lastSavedTime: new Map(),

      // إضافة ملاحظة جديدة
      addNote: (lessonId: string, content: string) => {
        const noteId = `note_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const newNote: Note = {
          id: noteId,
          lessonId,
          content,
          createdAt: new Date(),
          updatedAt: new Date(),
          isSynced: false,
          isPinned: false,
        };

        set((state) => {
          const newNotes = new Map(state.notes);
          newNotes.set(lessonId, newNote);

          const newIsDirty = new Map(state.isDirty);
          newIsDirty.set(noteId, true);

          return {
            notes: newNotes,
            allNotes: [...state.allNotes, newNote],
            isDirty: newIsDirty,
          };
        });

        return noteId;
      },

      // تحديث ملاحظة
      updateNote: (noteId: string, content: string) => {
        set((state) => {
          const newNotes = new Map(state.notes);
          let updatedNote: Note | undefined;

          // البحث عن الملاحظة وتحديثها
          for (const [lessonId, note] of newNotes.entries()) {
            if (note.id === noteId) {
              updatedNote = { ...note, content, updatedAt: new Date() };
              newNotes.set(lessonId, updatedNote);
              break;
            }
          }

          // تحديث قائمة الملاحظات
          const newAllNotes = state.allNotes.map((note) =>
            note.id === noteId
              ? { ...note, content, updatedAt: new Date() }
              : note
          );

          // تسجيل كـ dirty
          const newIsDirty = new Map(state.isDirty);
          newIsDirty.set(noteId, true);

          return {
            notes: newNotes,
            allNotes: newAllNotes,
            isDirty: newIsDirty,
          };
        });
      },

      // حذف ملاحظة
      deleteNote: (noteId: string, lessonId: string) => {
        set((state) => {
          const newNotes = new Map(state.notes);
          newNotes.delete(lessonId);

          const newAllNotes = state.allNotes.filter((note) => note.id !== noteId);

          const newIsDirty = new Map(state.isDirty);
          newIsDirty.delete(noteId);

          const newLastSavedTime = new Map(state.lastSavedTime);
          newLastSavedTime.delete(noteId);

          return {
            notes: newNotes,
            allNotes: newAllNotes,
            isDirty: newIsDirty,
            lastSavedTime: newLastSavedTime,
          };
        });
      },

      // الحصول على ملاحظة درس معين
      getNote: (lessonId: string) => {
        return get().notes.get(lessonId);
      },

      // نفس الدالة السابقة (للتوضيح)
      getNotesByLessonId: (lessonId: string) => {
        return get().notes.get(lessonId);
      },

      // الحصول على جميع الملاحظات
      getAllNotes: () => {
        return get().allNotes.sort(
          (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()
        );
      },

      // البحث في الملاحظات
      searchNotes: (query: string) => {
        const lowerQuery = query.toLowerCase();
        return get().allNotes.filter(
          (note) =>
            note.content.toLowerCase().includes(lowerQuery) ||
            note.id.toLowerCase().includes(lowerQuery)
        );
      },

      // تثبيت/فك تثبيت ملاحظة
      pinNote: (noteId: string, pinned: boolean) => {
        set((state) => {
          const newAllNotes = state.allNotes.map((note) =>
            note.id === noteId ? { ...note, isPinned: pinned } : note
          );

          const newNotes = new Map(state.notes);
          for (const [lessonId, note] of newNotes.entries()) {
            if (note.id === noteId) {
              newNotes.set(lessonId, { ...note, isPinned: pinned });
              break;
            }
          }

          return {
            allNotes: newAllNotes,
            notes: newNotes,
          };
        });
      },

      // الحصول على الملاحظات المثبتة
      getPinnedNotes: () => {
        return get().allNotes.filter((note) => note.isPinned);
      },

      // تسجيل الملاحظة كـ مُحفوظة
      markAsSynced: (noteId: string) => {
        set((state) => {
          const newAllNotes = state.allNotes.map((note) =>
            note.id === noteId
              ? {
                  ...note,
                  isSynced: true,
                  updatedAt: new Date(),
                }
              : note
          );

          const newIsDirty = new Map(state.isDirty);
          newIsDirty.set(noteId, false);

          const newLastSavedTime = new Map(state.lastSavedTime);
          newLastSavedTime.set(noteId, new Date());

          return {
            allNotes: newAllNotes,
            isDirty: newIsDirty,
            lastSavedTime: newLastSavedTime,
          };
        });
      },

      // تسجيل الملاحظة كـ غير محفوظة
      markAsDirty: (noteId: string) => {
        set((state) => {
          const newIsDirty = new Map(state.isDirty);
          newIsDirty.set(noteId, true);

          return { isDirty: newIsDirty };
        });
      },

      // مسح جميع الملاحظات
      clearNotes: () => {
        set({
          notes: new Map(),
          allNotes: [],
          isDirty: new Map(),
          lastSavedTime: new Map(),
        });
      },

      // تصدير الملاحظات
      exportNotes: (format: 'json' | 'txt') => {
        const notes = get().allNotes;

        if (format === 'json') {
          return JSON.stringify(notes, null, 2);
        }

        if (format === 'txt') {
          let text = 'الملاحظات الشخصية\n';
          text += `تصدير بتاريخ: ${new Date().toLocaleString('ar-SA')}\n`;
          text += `${'='.repeat(50)}\n\n`;

          notes.forEach((note) => {
            text += `الدرس: ${note.lessonId}\n`;
            text += `الملاحظة:\n${note.content}\n`;
            text += `التاريخ: ${note.updatedAt.toLocaleString('ar-SA')}\n`;
            text += `${'-'.repeat(50)}\n\n`;
          });

          return text;
        }

        return '';
      },

      // الحصول على الملاحظات غير المحفوظة
      getUnsyncedNotes: () => {
        return get().allNotes.filter((note) => !note.isSynced);
      },
    }),
    {
      name: 'notes-store',
      version: 1,
      merge: (persistedState: any, currentState) => {
        // تحويل الخريطة المحفوظة إلى Map
        if (persistedState.notes && !(persistedState.notes instanceof Map)) {
          persistedState.notes = new Map(persistedState.notes);
        }
        if (persistedState.isDirty && !(persistedState.isDirty instanceof Map)) {
          persistedState.isDirty = new Map(persistedState.isDirty);
        }
        if (persistedState.lastSavedTime && !(persistedState.lastSavedTime instanceof Map)) {
          persistedState.lastSavedTime = new Map(persistedState.lastSavedTime);
        }
        return { ...currentState, ...persistedState };
      },
    }
  )
);
