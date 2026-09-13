import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * QuestionsStore - إدارة الأسئلة المولدة
 * يتعامل مع:
 * - حفظ الأسئلة المولدة
 * - تتبع الإجابات
 * - الإحصائيات
 */

export interface QuestionOption {
  id: string; // 'A', 'B', 'C', 'D'
  text: string;
  isCorrect?: boolean;
}

export interface Question {
  id: string;
  lessonId: string;
  questionText: string;
  type: 'multiple_choice' | 'essay' | 'true_false' | 'fill_blank';
  difficulty: 'easy' | 'medium' | 'hard';
  topic: string;
  options?: QuestionOption[]; // لـ multiple_choice و true_false
  correctAnswer: string; // قيمة الإجابة الصحيحة
  explanation: string; // شرح الإجابة
  createdAt: Date;
  isUsed: boolean; // هل استُخدمت في اختبار
  userAnswer?: string; // إجابة المستخدم
  isAnsweredCorrectly?: boolean; // هل الإجابة صحيحة
  timestamp?: Date; // وقت الإجابة
}

export interface Quiz {
  id: string;
  name: string;
  lessonId: string;
  questions: Question[];
  createdAt: Date;
  completedAt?: Date;
  score?: number; // النسبة المئوية
  totalQuestions: number;
  correctAnswers: number;
}

interface QuestionsStore {
  // الحالة
  questions: Question[];
  quizzes: Quiz[];
  currentQuiz: Quiz | null;
  isLoading: boolean;
  error: string | null;

  // الإجراءات
  addQuestion: (question: Omit<Question, 'id' | 'createdAt'>) => string;
  updateQuestion: (id: string, updates: Partial<Question>) => void;
  deleteQuestion: (id: string) => void;
  getQuestionById: (id: string) => Question | undefined;
  getQuestionsByLesson: (lessonId: string) => Question[];
  getQuestionsByDifficulty: (difficulty: 'easy' | 'medium' | 'hard') => Question[];
  createQuiz: (name: string, lessonId: string, questions: Question[]) => string;
  deleteQuiz: (quizId: string) => void;
  setCurrentQuiz: (quizId: string) => void;
  answerQuestion: (quizId: string, questionId: string, answer: string) => void;
  submitQuiz: (quizId: string) => { score: number; correctAnswers: number };
  getQuizzes: () => Quiz[];
  getQuizByLesson: (lessonId: string) => Quiz[];
  getStatistics: () => {
    totalQuestions: number;
    totalQuizzes: number;
    averageScore: number;
    correctAnswers: number;
    wrongAnswers: number;
  };
  clearQuestions: () => void;
  exportQuestions: (ids: string[], format: 'json' | 'pdf') => string;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useQuestionsStore = create<QuestionsStore>()(
  persist(
    (set, get) => ({
      // الحالة الابتدائية
      questions: [],
      quizzes: [],
      currentQuiz: null,
      isLoading: false,
      error: null,

      // إضافة سؤال جديد
      addQuestion: (question) => {
        const id = `question_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const newQuestion: Question = {
          ...question,
          id,
          createdAt: new Date(),
          isUsed: false,
        };

        set((state) => ({
          questions: [...state.questions, newQuestion],
        }));

        return id;
      },

      // تحديث سؤال
      updateQuestion: (id: string, updates: Partial<Question>) => {
        set((state) => ({
          questions: state.questions.map((question) =>
            question.id === id ? { ...question, ...updates } : question
          ),
        }));
      },

      // حذف سؤال
      deleteQuestion: (id: string) => {
        set((state) => ({
          questions: state.questions.filter((question) => question.id !== id),
        }));
      },

      // الحصول على سؤال بـ ID
      getQuestionById: (id: string) => {
        return get().questions.find((question) => question.id === id);
      },

      // الحصول على الأسئلة حسب الدرس
      getQuestionsByLesson: (lessonId: string) => {
        return get().questions.filter((question) => question.lessonId === lessonId);
      },

      // الحصول على الأسئلة حسب مستوى الصعوبة
      getQuestionsByDifficulty: (difficulty) => {
        return get().questions.filter((question) => question.difficulty === difficulty);
      },

      // إنشاء اختبار
      createQuiz: (name: string, lessonId: string, questions: Question[]) => {
        const quizId = `quiz_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const newQuiz: Quiz = {
          id: quizId,
          name,
          lessonId,
          questions,
          createdAt: new Date(),
          totalQuestions: questions.length,
          correctAnswers: 0,
        };

        set((state) => ({
          quizzes: [...state.quizzes, newQuiz],
        }));

        return quizId;
      },

      // حذف اختبار
      deleteQuiz: (quizId: string) => {
        set((state) => ({
          quizzes: state.quizzes.filter((quiz) => quiz.id !== quizId),
          currentQuiz: state.currentQuiz?.id === quizId ? null : state.currentQuiz,
        }));
      },

      // تعيين الاختبار الحالي
      setCurrentQuiz: (quizId: string) => {
        const quiz = get().quizzes.find((q) => q.id === quizId);
        if (quiz) {
          set({ currentQuiz: quiz });
        }
      },

      // الإجابة على سؤال
      answerQuestion: (quizId: string, questionId: string, answer: string) => {
        set((state) => {
          const updatedQuizzes = state.quizzes.map((quiz) => {
            if (quiz.id === quizId) {
              const updatedQuestions = quiz.questions.map((question) => {
                if (question.id === questionId) {
                  const isCorrect = question.correctAnswer === answer;
                  return {
                    ...question,
                    userAnswer: answer,
                    isAnsweredCorrectly: isCorrect,
                    timestamp: new Date(),
                  };
                }
                return question;
              });

              return {
                ...quiz,
                questions: updatedQuestions,
              };
            }
            return quiz;
          });

          return {
            quizzes: updatedQuizzes,
            currentQuiz:
              state.currentQuiz?.id === quizId
                ? updatedQuizzes.find((q) => q.id === quizId) || null
                : state.currentQuiz,
          };
        });
      },

      // إرسال الاختبار (حساب النتيجة)
      submitQuiz: (quizId: string) => {
        const quiz = get().quizzes.find((q) => q.id === quizId);
        if (!quiz) return { score: 0, correctAnswers: 0 };

        const correctAnswers = quiz.questions.filter(
          (q) => q.isAnsweredCorrectly === true
        ).length;
        const score = Math.round((correctAnswers / quiz.totalQuestions) * 100);

        set((state) => ({
          quizzes: state.quizzes.map((q) =>
            q.id === quizId
              ? {
                  ...q,
                  score,
                  correctAnswers,
                  completedAt: new Date(),
                }
              : q
          ),
        }));

        return { score, correctAnswers };
      },

      // الحصول على جميع الاختبارات
      getQuizzes: () => {
        return get().quizzes.sort(
          (a, b) => b.createdAt.getTime() - a.createdAt.getTime()
        );
      },

      // الحصول على الاختبارات حسب الدرس
      getQuizByLesson: (lessonId: string) => {
        return get().quizzes.filter((quiz) => quiz.lessonId === lessonId);
      },

      // الحصول على الإحصائيات
      getStatistics: () => {
        const state = get();
        const answeredQuestions = state.questions.filter(
          (q) => q.userAnswer !== undefined
        );
        const correctAnswers = answeredQuestions.filter(
          (q) => q.isAnsweredCorrectly === true
        ).length;
        const wrongAnswers = answeredQuestions.length - correctAnswers;
        const completedQuizzes = state.quizzes.filter((q) => q.completedAt);
        const averageScore =
          completedQuizzes.length > 0
            ? Math.round(
                completedQuizzes.reduce((sum, q) => sum + (q.score || 0), 0) /
                  completedQuizzes.length
              )
            : 0;

        return {
          totalQuestions: state.questions.length,
          totalQuizzes: completedQuizzes.length,
          averageScore,
          correctAnswers,
          wrongAnswers,
        };
      },

      // مسح جميع الأسئلة
      clearQuestions: () => {
        set({
          questions: [],
          quizzes: [],
          currentQuiz: null,
        });
      },

      // تصدير الأسئلة
      exportQuestions: (ids: string[], format: 'json' | 'pdf') => {
        const questionsToExport = get().questions.filter((q) =>
          ids.includes(q.id)
        );

        if (format === 'json') {
          return JSON.stringify(questionsToExport, null, 2);
        }

        // PDF سيتم التعامل معه عبر مكتبة خارجية
        return '';
      },

      // تعيين حالة التحميل
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      // تعيين الخطأ
      setError: (error: string | null) => {
        set({ error });
      },
    }),
    {
      name: 'questions-store',
      version: 1,
    }
  )
);
