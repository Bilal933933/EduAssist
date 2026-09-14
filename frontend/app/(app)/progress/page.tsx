"use client";

import { Spinner } from "@/components/ui/spinner";
import { useProgressData } from "@/hooks/use-progress-data";
import { StatCards } from "@/components/progress/stat-cards";
import { TopicsChart } from "@/components/progress/topics-chart";
import { LessonsList } from "@/components/progress/lessons-list";
import { MistakesList } from "@/components/progress/mistakes-list";
import { ProfileSummary } from "@/components/progress/profile-summary";

// وظيفة واحدة: تجميع أقسام صفحة التقدم — الاشتقاق في useProgressData والعرض في components/progress.
export default function ProgressPage() {
  const data = useProgressData();

  return (
    <div className="container py-6 space-y-6">
      <div>
        <h1 className="text-xl font-extrabold">سجلي كمدرس</h1>
        <p className="text-sm text-muted-foreground mt-1">
          ملخص حقيقي من محادثاتك ومصادرك المفهرسة — يتحدث تلقائياً مع كل استخدام
        </p>
      </div>

      {data.loading ? (
        <div className="flex justify-center py-10">
          <Spinner className="size-6" />
        </div>
      ) : (
        <>
          <StatCards
            threadCount={data.threadCount}
            messageTotal={data.messageTotal}
            interactionCount={data.interactionCount}
            totalChunks={data.totalChunks}
            topicCount={data.topics.length}
            grades={data.grades}
          />

          <div className="grid md:grid-cols-2 gap-4 items-start">
            <TopicsChart topics={data.topics} maxCount={data.maxCount} />
            <div className="space-y-4">
              <LessonsList lessons={data.lessons} />
              <MistakesList mistakes={data.mistakes} />
            </div>
          </div>

          <ProfileSummary summary={data.summary} classContext={data.classContext} />
        </>
      )}
    </div>
  );
}
