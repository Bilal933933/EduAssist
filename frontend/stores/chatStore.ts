import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * ChatStore - إدارة حالة الدردشات والرسائل
 * يتعامل مع:
 * - رسائل الدردشة الحالية
 * - معرّف thread الحالي
 * - حفظ الدردشات في localStorage
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  lessonId?: string;
  sources?: Array<{
    title: string;
    page?: number;
    confidence?: number;
  }>;
  thinking?: string; // ReAct Thinking
  isSaved?: boolean;
}

export interface ChatThread {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
  topicArea?: string; // "الفاعل", "النعت", إلخ
}

interface ChatStore {
  // الحالة
  threads: ChatThread[];
  currentThreadId: string | null;
  messages: ChatMessage[]; // الرسائل في الـ thread الحالي
  isLoading: boolean;
  error: string | null;

  // الإجراءات
  createThread: (title: string, topicArea?: string) => string;
  setCurrentThread: (threadId: string) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (messageId: string, updates: Partial<ChatMessage>) => void;
  deleteMessage: (messageId: string) => void;
  clearMessages: () => void;
  deleteThread: (threadId: string) => void;
  renameThread: (threadId: string, newTitle: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  getCurrentThread: () => ChatThread | undefined;
  getThreads: () => ChatThread[];
  exportThread: (threadId: string, format: 'json' | 'txt' | 'pdf') => string;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      // الحالة الابتدائية
      threads: [],
      currentThreadId: null,
      messages: [],
      isLoading: false,
      error: null,

      // إنشاء thread جديد
      createThread: (title: string, topicArea?: string) => {
        const threadId = `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const newThread: ChatThread = {
          id: threadId,
          title,
          messages: [],
          createdAt: new Date(),
          updatedAt: new Date(),
          topicArea,
        };

        set((state) => ({
          threads: [...state.threads, newThread],
          currentThreadId: threadId,
          messages: [],
        }));

        return threadId;
      },

      // تعيين thread الحالي
      setCurrentThread: (threadId: string) => {
        const thread = get().threads.find((t) => t.id === threadId);
        if (thread) {
          set({
            currentThreadId: threadId,
            messages: thread.messages,
          });
        }
      },

      // إضافة رسالة
      addMessage: (message: ChatMessage) => {
        const messageWithDate = {
          ...message,
          timestamp: new Date(),
        };

        set((state) => {
          const updatedMessages = [...state.messages, messageWithDate];
          const updatedThreads = state.threads.map((thread) => {
            if (thread.id === state.currentThreadId) {
              return {
                ...thread,
                messages: updatedMessages,
                updatedAt: new Date(),
              };
            }
            return thread;
          });

          return {
            messages: updatedMessages,
            threads: updatedThreads,
          };
        });
      },

      // تحديث رسالة
      updateMessage: (messageId: string, updates: Partial<ChatMessage>) => {
        set((state) => {
          const updatedMessages = state.messages.map((msg) =>
            msg.id === messageId ? { ...msg, ...updates } : msg
          );

          const updatedThreads = state.threads.map((thread) => {
            if (thread.id === state.currentThreadId) {
              return {
                ...thread,
                messages: updatedMessages,
                updatedAt: new Date(),
              };
            }
            return thread;
          });

          return {
            messages: updatedMessages,
            threads: updatedThreads,
          };
        });
      },

      // حذف رسالة
      deleteMessage: (messageId: string) => {
        set((state) => {
          const updatedMessages = state.messages.filter((msg) => msg.id !== messageId);
          const updatedThreads = state.threads.map((thread) => {
            if (thread.id === state.currentThreadId) {
              return {
                ...thread,
                messages: updatedMessages,
              };
            }
            return thread;
          });

          return {
            messages: updatedMessages,
            threads: updatedThreads,
          };
        });
      },

      // مسح جميع الرسائل
      clearMessages: () => {
        set((state) => {
          const updatedThreads = state.threads.map((thread) => {
            if (thread.id === state.currentThreadId) {
              return {
                ...thread,
                messages: [],
              };
            }
            return thread;
          });

          return {
            messages: [],
            threads: updatedThreads,
          };
        });
      },

      // حذف thread
      deleteThread: (threadId: string) => {
        set((state) => {
          const updatedThreads = state.threads.filter((t) => t.id !== threadId);
          const isCurrentThread = state.currentThreadId === threadId;

          return {
            threads: updatedThreads,
            currentThreadId: isCurrentThread ? (updatedThreads[0]?.id ?? null) : state.currentThreadId,
            messages: isCurrentThread ? (updatedThreads[0]?.messages ?? []) : state.messages,
          };
        });
      },

      // إعادة تسمية thread
      renameThread: (threadId: string, newTitle: string) => {
        set((state) => ({
          threads: state.threads.map((thread) =>
            thread.id === threadId ? { ...thread, title: newTitle } : thread
          ),
        }));
      },

      // تعيين حالة التحميل
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      // تعيين الخطأ
      setError: (error: string | null) => {
        set({ error });
      },

      // الحصول على الـ thread الحالي
      getCurrentThread: () => {
        return get().threads.find((t) => t.id === get().currentThreadId);
      },

      // الحصول على جميع الـ threads
      getThreads: () => {
        return get().threads.sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());
      },

      // تصدير thread
      exportThread: (threadId: string, format: 'json' | 'txt' | 'pdf') => {
        const thread = get().threads.find((t) => t.id === threadId);
        if (!thread) return '';

        if (format === 'json') {
          return JSON.stringify(thread, null, 2);
        }

        if (format === 'txt') {
          let text = `الموضوع: ${thread.title}\n`;
          text += `تاريخ الإنشاء: ${thread.createdAt.toLocaleString('ar-SA')}\n`;
          text += `${'='.repeat(50)}\n\n`;

          thread.messages.forEach((msg) => {
            text += `${msg.role === 'user' ? 'أنت' : 'المساعد'}: ${msg.content}\n\n`;
          });

          return text;
        }

        // PDF سيتم التعامل معه عبر مكتبة خارجية
        return '';
      },
    }),
    {
      name: 'chat-store',
      version: 1,
    }
  )
);
