import { useEffect, useState } from 'react';
import { HistoryEntry, TweetGenerationResponse } from '../api/types';

const HISTORY_KEY = 'apple_tweet_history';
const MAX_HISTORY = 30;

export function useHistory() {
  const [history, setHistory] = useState<HistoryEntry[]>(() => {
    try {
      const saved = localStorage.getItem(HISTORY_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    } catch (e) {
      console.error('Failed to save generation history to localStorage', e);
    }
  }, [history]);

  const addEntry = (query: string, response: TweetGenerationResponse) => {
    const newEntry: HistoryEntry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
      timestamp: new Date().toISOString(),
      query,
      response,
    };
    setHistory((prev) => [newEntry, ...prev.slice(0, MAX_HISTORY - 1)]);
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem(HISTORY_KEY);
  };

  const removeEntry = (id: string) => {
    setHistory((prev) => prev.filter((item) => item.id !== id));
  };

  return { history, addEntry, clearHistory, removeEntry };
}
