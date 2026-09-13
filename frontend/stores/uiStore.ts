import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * UIStore - إدارة حالة الواجهة
 * يتعامل مع:
 * - المظهر (Theme)
 * - حالة الـ Sidebar
 * - الإعدادات العامة
 * - مستوى الصعوبة والشرح
 */

export type Difficulty = 'easy' | 'medium' | 'hard';
export type ExplanationMode = 'beginner' | 'intermediate' | 'advanced';
export type QuestionType = 'multiple_choice' | 'essay' | 'true_false' | 'fill_blank';
export type Theme = 'light' | 'dark' | 'system';

interface UIStore {
  // الحالة
  theme: Theme;
  sidebarOpen: boolean;
  currentLessonId: string | null;
  selectedDifficulty: Difficulty;
  selectedExplanationMode: ExplanationMode;
  selectedQuestionType: QuestionType;
  showThinkingProcess: boolean;
  autoSaveEnabled: boolean;
  rtlEnabled: boolean;
  notificationEnabled: boolean;
  chatPanelWidth: number; // في بكسل (200-600)

  // الإجراءات
  setTheme: (theme: Theme) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setCurrentLessonId: (id: string | null) => void;
  setDifficulty: (difficulty: Difficulty) => void;
  setExplanationMode: (mode: ExplanationMode) => void;
  setQuestionType: (type: QuestionType) => void;
  setShowThinkingProcess: (show: boolean) => void;
  setAutoSaveEnabled: (enabled: boolean) => void;
  setRTLEnabled: (enabled: boolean) => void;
  setNotificationEnabled: (enabled: boolean) => void;
  setChatPanelWidth: (width: number) => void;
  resetToDefaults: () => void;
}

type UIState = Pick<
  UIStore,
  | "theme"
  | "sidebarOpen"
  | "currentLessonId"
  | "selectedDifficulty"
  | "selectedExplanationMode"
  | "selectedQuestionType"
  | "showThinkingProcess"
  | "autoSaveEnabled"
  | "rtlEnabled"
  | "notificationEnabled"
  | "chatPanelWidth"
>;

const defaultState: UIState = {
  theme: 'dark',
  sidebarOpen: true,
  currentLessonId: null,
  selectedDifficulty: 'medium',
  selectedExplanationMode: 'intermediate',
  selectedQuestionType: 'multiple_choice',
  showThinkingProcess: true,
  autoSaveEnabled: true,
  rtlEnabled: true,
  notificationEnabled: true,
  chatPanelWidth: 400,
};

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      ...defaultState,

      // تعيين المظهر
      setTheme: (theme: Theme) => {
        set({ theme });
      },

      // تبديل الـ Sidebar
      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }));
      },

      // تعيين حالة الـ Sidebar
      setSidebarOpen: (open: boolean) => {
        set({ sidebarOpen: open });
      },

      // تعيين الدرس الحالي
      setCurrentLessonId: (id: string | null) => {
        set({ currentLessonId: id });
      },

      // تعيين مستوى الصعوبة
      setDifficulty: (difficulty: Difficulty) => {
        set({ selectedDifficulty: difficulty });
      },

      // تعيين مستوى الشرح
      setExplanationMode: (mode: ExplanationMode) => {
        set({ selectedExplanationMode: mode });
      },

      // تعيين نمط السؤال
      setQuestionType: (type: QuestionType) => {
        set({ selectedQuestionType: type });
      },

      // تعيين عرض عملية التفكير
      setShowThinkingProcess: (show: boolean) => {
        set({ showThinkingProcess: show });
      },

      // تعيين الحفظ التلقائي
      setAutoSaveEnabled: (enabled: boolean) => {
        set({ autoSaveEnabled: enabled });
      },

      // تعيين دعم RTL
      setRTLEnabled: (enabled: boolean) => {
        set({ rtlEnabled: enabled });
      },

      // تعيين الإشعارات
      setNotificationEnabled: (enabled: boolean) => {
        set({ notificationEnabled: enabled });
      },

      // تعيين عرض لوحة الدردشة
      setChatPanelWidth: (width: number) => {
        // تقيد القيمة بين 200 و 600
        const constrainedWidth = Math.max(200, Math.min(600, width));
        set({ chatPanelWidth: constrainedWidth });
      },

      // إعادة تعيين الإعدادات الافتراضية
      resetToDefaults: () => {
        set(defaultState);
      },
    }),
    {
      name: 'ui-store',
      version: 1,
    }
  )
);
