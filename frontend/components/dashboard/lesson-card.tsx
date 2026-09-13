'use client';

import React from 'react';
import { SavedLesson, useLessonStore } from '@/stores';
import { Button } from '@/components/ui/button';
import { Pin, Trash2, Edit2 } from 'lucide-react';

interface LessonCardProps {
  lesson: SavedLesson;
}

export default function LessonCard({ lesson }: LessonCardProps) {
  const pinLesson = useLessonStore((state) => state.pinLesson);
  const deleteLesson = useLessonStore((state) => state.deleteLesson);

  return (
    <div className="bg-card rounded-lg border border-border p-4 hover:shadow-md transition">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-bold text-foreground line-clamp-2">
          {lesson.title}
        </h3>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => pinLesson(lesson.id, !lesson.isPinned)}
        >
          <Pin className={`w-4 h-4 ${lesson.isPinned ? 'fill-current' : ''}`} />
        </Button>
      </div>

      <span className="inline-block bg-primary/10 text-primary text-xs px-2 py-1 rounded mb-2">
        {lesson.topic}
      </span>

      <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
        {lesson.content}
      </p>

      <div className="flex gap-2">
        <Button size="sm" variant="outline" className="flex-1">
          <Edit2 className="w-4 h-4 mr-1" />
          عرض
        </Button>
        <Button
          size="sm"
          variant="destructive"
          onClick={() => deleteLesson(lesson.id)}
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
