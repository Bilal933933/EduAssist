"use client";

import { useMemory, useStats, useThreads } from "@/lib/queries";
import { cleanGradeLabel, mergeTopics } from "@/lib/memory";

// وظيفة واحدة: اشتقاق بيانات صفحة التقدم من الاستعلامات — بلا أي عرض.
export function useProgressData() {
  const { data: stats } = useStats();
  const { data: threads = [], isLoading: threadsLoading } = useThreads(true);
  const { data: memory, isLoading: memoryLoading } = useMemory(true);

  const profile = memory?.profile;
  const topics = mergeTopics(profile?.frequent_topics);

  return {
    loading: threadsLoading || memoryLoading,
    totalChunks: stats?.total_chunks ?? 0,
    threadCount: threads.length,
    messageTotal: threads.reduce((sum, t) => sum + (t.message_count || 0), 0),
    interactionCount: profile?.interaction_count ?? 0,
    topics,
    maxCount: topics.reduce((max, t) => Math.max(max, t.count), 1),
    lessons: profile?.recent_lessons ?? [],
    mistakes: profile?.common_mistakes ?? [],
    grades: (profile?.preferred_grades ?? [])
      .map(cleanGradeLabel)
      .filter((g): g is string => !!g),
    summary: profile?.summary ?? null,
    classContext: profile?.class_context ?? null,
  };
}

export type ProgressData = ReturnType<typeof useProgressData>;
