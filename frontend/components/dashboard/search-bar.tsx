'use client';

import React, { useState } from 'react';
import { Search } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string) => void;
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    onSearch(value);
  };

  return (
    <div className="relative">
      <Search className="absolute right-3 top-3 w-4 h-4 text-muted-foreground" />
      <input
        type="text"
        placeholder="ابحث عن درس..."
        value={query}
        onChange={handleChange}
        className="w-full pr-10 pl-4 py-2 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground"
      />
    </div>
  );
}
