'use client';

import React from 'react';
import { SavedLesson } from '@/stores';
import LessonCard from './lesson-card';

interface LessonsGridProps {
  lessons: SavedLesson[];
}

export default function LessonsGrid({ lessons }: LessonsGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {lessons.map((lesson) => (
        <LessonCard key={lesson.id} lesson={lesson} />
      ))}
    </div>
  );
}
