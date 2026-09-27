import React, { useRef, useEffect } from 'react';

interface UsePromptEditorParams {
  query: string;
  isLoading: boolean;
  onGenerate: (query: string) => void;
}

export function usePromptEditor({ query, isLoading, onGenerate }: UsePromptEditorParams) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea height to fit content nicely
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      if (!query || scrollHeight <= 32) {
        textareaRef.current.style.height = '24px';
      } else {
        textareaRef.current.style.height = `${Math.min(scrollHeight, 160)}px`;
      }
    }
  }, [query]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onGenerate(query.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (query.trim() && !isLoading) {
        onGenerate(query.trim());
      }
    }
  };

  return {
    textareaRef,
    handleSubmit,
    handleKeyDown,
  };
}
