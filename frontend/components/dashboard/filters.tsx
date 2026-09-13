'use client';

import React from 'react';
import { Button } from '@/components/ui/button';

interface FiltersProps {
  onTopicChange: (topic: string | null) => void;
  onGradeChange: (grade: string | null) => void;
  selectedTopic: string | null;
  selectedGrade: string | null;
}

const TOPICS = ['الفاعل', 'النعت', 'الإضافة', 'الصفة', 'الفعل', 'الحال'];
const GRADES = ['أول ثانوي', 'ثاني ثانوي', 'ثالث ثانوي'];

export default function Filters({
  onTopicChange,
  onGradeChange,
  selectedTopic,
  selectedGrade,
}: FiltersProps) {
  return (
    <div className="space-y-4">
      {/* Topics */}
      <div>
        <p className="text-sm font-medium text-foreground mb-2">المواضيع</p>
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant={selectedTopic === null ? 'default' : 'outline'}
            onClick={() => onTopicChange(null)}
          >
            الكل
          </Button>
          {TOPICS.map((topic) => (
            <Button
              key={topic}
              size="sm"
              variant={selectedTopic === topic ? 'default' : 'outline'}
              onClick={() => onTopicChange(topic)}
            >
              {topic}
            </Button>
          ))}
        </div>
      </div>

      {/* Grades */}
      <div>
        <p className="text-sm font-medium text-foreground mb-2">الصفوف</p>
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant={selectedGrade === null ? 'default' : 'outline'}
            onClick={() => onGradeChange(null)}
          >
            الكل
          </Button>
          {GRADES.map((grade) => (
            <Button
              key={grade}
              size="sm"
              variant={selectedGrade === grade ? 'default' : 'outline'}
              onClick={() => onGradeChange(grade)}
            >
              {grade}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
