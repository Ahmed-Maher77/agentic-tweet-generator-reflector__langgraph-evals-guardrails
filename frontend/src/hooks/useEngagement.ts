import { useState } from 'react';

export function useEngagement() {
  const [isLiked, setIsLiked] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);

  const toggleLiked = () => setIsLiked((prev) => !prev);
  const toggleBookmarked = () => setIsBookmarked((prev) => !prev);

  return {
    isLiked,
    toggleLiked,
    isBookmarked,
    toggleBookmarked,
  };
}
