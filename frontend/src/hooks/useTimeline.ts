import { useState } from 'react';
import { AttemptRecord } from '../types';

export function useTimeline(attempts: AttemptRecord[]) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(
    attempts.length > 0 ? attempts.length - 1 : null
  );

  const toggleExpand = (idx: number) => {
    setExpandedIndex((prev) => (prev === idx ? null : idx));
  };

  return {
    expandedIndex,
    toggleExpand,
  };
}
