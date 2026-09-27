import { useState, useEffect } from 'react';

interface UseTypewriterOptions {
  phrases: string[];
  isLoading: boolean;
  hasResult: boolean;
  typingSpeed?: number;
  deletingSpeed?: number;
  pauseDuration?: number;
}

export function useTypewriter({
  phrases,
  isLoading,
  hasResult,
  typingSpeed = 60,
  deletingSpeed = 30,
  pauseDuration = 2200,
}: UseTypewriterOptions) {
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [currentText, setCurrentText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (isLoading || hasResult || phrases.length === 0) return;

    const targetPhrase = phrases[currentPhraseIndex];
    const speed = isDeleting ? deletingSpeed : typingSpeed;
    let pauseTimer: ReturnType<typeof setTimeout> | undefined;

    const timer = setTimeout(() => {
      if (!isDeleting) {
        if (currentText.length < targetPhrase.length) {
          setCurrentText(targetPhrase.substring(0, currentText.length + 1));
        } else {
          pauseTimer = setTimeout(() => setIsDeleting(true), pauseDuration);
        }
      } else {
        if (currentText.length > 0) {
          setCurrentText(targetPhrase.substring(0, currentText.length - 1));
        } else {
          setIsDeleting(false);
          setCurrentPhraseIndex((prev) => (prev + 1) % phrases.length);
        }
      }
    }, speed);

    return () => {
      clearTimeout(timer);
      if (pauseTimer) clearTimeout(pauseTimer);
    };
  }, [currentText, isDeleting, currentPhraseIndex, isLoading, hasResult, phrases, typingSpeed, deletingSpeed, pauseDuration]);

  return {
    currentText,
  };
}
