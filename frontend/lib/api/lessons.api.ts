/**
 * API Service للدروس
 * يتعامل مع جميع استدعاءات API المتعلقة بالدروس
 */

import { SavedLesson } from '@/stores';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

export const lessonsAPI = {
  /**
   * الحصول على جميع الدروس
   */
  async getAllLessons(): Promise<SavedLesson[]> {
    const response = await fetch(`${API_BASE}/api/lessons`, {
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
    });

    if (!response.ok) throw new Error('Failed to fetch lessons');
    return response.json();
  },

  /**
   * الحصول على درس واحد
   */
  async getLesson(id: string): Promise<SavedLesson> {
    const response = await fetch(`${API_BASE}/api/lessons/${id}`, {
      credentials: 'include',
    });

    if (!response.ok) throw new Error('Failed to fetch lesson');
    return response.json();
  },

  /**
   * إنشاء درس جديد
   */
  async createLesson(lesson: Omit<SavedLesson, 'id' | 'createdAt' | 'updatedAt' | 'isPinned'>): Promise<SavedLesson> {
    const response = await fetch(`${API_BASE}/api/lessons`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(lesson),
    });

    if (!response.ok) throw new Error('Failed to create lesson');
    return response.json();
  },

  /**
   * تحديث درس
   */
  async updateLesson(id: string, updates: Partial<SavedLesson>): Promise<SavedLesson> {
    const response = await fetch(`${API_BASE}/api/lessons/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(updates),
    });

    if (!response.ok) throw new Error('Failed to update lesson');
    return response.json();
  },

  /**
   * تحديث الملاحظات
   */
  async updateNotes(id: string, notes: string): Promise<SavedLesson> {
    const response = await fetch(`${API_BASE}/api/lessons/${id}/notes`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ notes }),
    });

    if (!response.ok) throw new Error('Failed to update notes');
    return response.json();
  },

  /**
   * تثبيت/فك تثبيت درس
   */
  async togglePin(id: string): Promise<SavedLesson> {
    const response = await fetch(`${API_BASE}/api/lessons/${id}/pin`, {
      method: 'PATCH',
      credentials: 'include',
    });

    if (!response.ok) throw new Error('Failed to toggle pin');
    return response.json();
  },

  /**
   * حذف درس
   */
  async deleteLesson(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/lessons/${id}`, {
      method: 'DELETE',
      credentials: 'include',
    });

    if (!response.ok) throw new Error('Failed to delete lesson');
  },

  /**
   * البحث في الدروس
   */
  async searchLessons(query: string, topic?: string, grade?: string): Promise<SavedLesson[]> {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (topic) params.append('topic', topic);
    if (grade) params.append('grade', grade);

    const response = await fetch(`${API_BASE}/api/lessons/search?${params}`, {
      credentials: 'include',
    });

    if (!response.ok) throw new Error('Failed to search lessons');
    return response.json();
  },

  /**
   * الحصول على الدروس المثبتة
   */
  async getPinnedLessons(): Promise<SavedLesson[]> {
    const response = await fetch(`${API_BASE}/api/lessons/pinned`, {
      credentials: 'include',
    });

    if (!response.ok) throw new Error('Failed to fetch pinned lessons');
    return response.json();
  },

  /**
   * الحصول على أحدث الدروس
   */
  async getRecentLessons(limit: number = 10): Promise<SavedLesson[]> {
    const response = await fetch(`${API_BASE}/api/lessons/recent?limit=${limit}`, {
      credentials: 'include',
    });

    if (!response.ok) throw new Error('Failed to fetch recent lessons');
    return response.json();
  },
};
