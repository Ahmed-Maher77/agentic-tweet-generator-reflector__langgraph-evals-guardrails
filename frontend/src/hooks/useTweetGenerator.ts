import { useEffect, useState, useCallback } from 'react';
import confetti from 'canvas-confetti';
import {
  GenerationSettings,
  SystemHealth,
  TweetGenerationResponse,
} from '../api/types';
import { fetchHealth, generateTweet } from '../api/client';
import { useHistory } from './useHistory';
import { ToastMessage } from '../components/StatusToast';

const DEFAULT_SETTINGS: GenerationSettings = {
  maxAttempts: 3,
  reflectionEnabled: true,
  searchEnabled: true,
  relevanceThreshold: 0.80,
  clarityThreshold: 0.80,
  professionalismThreshold: 0.80,
  engagementThreshold: 0.70,
  adherenceThreshold: 0.85,
};

export function useTweetGenerator() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentResponse, setCurrentResponse] = useState<TweetGenerationResponse | null>(null);
  const [lastQuery, setLastQuery] = useState('');
  const [toast, setToast] = useState<ToastMessage | null>(null);

  const [settings, setSettings] = useState<GenerationSettings>(() => {
    try {
      const saved = localStorage.getItem('apple_tweet_settings');
      return saved ? JSON.parse(saved) : DEFAULT_SETTINGS;
    } catch {
      return DEFAULT_SETTINGS;
    }
  });

  const { history, addEntry, clearHistory, removeEntry } = useHistory();

  // Save settings when modified
  const updateSettings = (newSettings: GenerationSettings) => {
    setSettings(newSettings);
    localStorage.setItem('apple_tweet_settings', JSON.stringify(newSettings));
  };

  // Toast dispatcher
  const showToast = useCallback((message: string, type: 'success' | 'warning' | 'info' | 'error' = 'info') => {
    setToast({ id: Date.now().toString(), message, type });
    setTimeout(() => {
      setToast((prev) => (prev?.message === message ? null : prev));
    }, 3000);
  }, []);

  // Check health on mount and periodic interval
  useEffect(() => {
    let isMounted = true;
    const check = async () => {
      try {
        const data = await fetchHealth();
        if (isMounted) setHealth(data);
      } catch {
        if (isMounted) setHealth(null);
      }
    };
    check();
    const interval = setInterval(check, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const triggerCelebration = () => {
    confetti({
      particleCount: 75,
      spread: 60,
      origin: { y: 0.8 },
      colors: ['#0071e3', '#34c759', '#af52de', '#ff9500'],
    });
  };

  const handleGenerate = async (query: string) => {
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    setLastQuery(query);

    try {
      const res = await generateTweet({
        query: query.trim(),
        max_attempts: settings.maxAttempts,
        reflection_enabled: settings.reflectionEnabled,
        search_enabled: settings.searchEnabled,
      });

      setCurrentResponse(res);
      addEntry(query, res);

      if (res.status === 'SUCCESS') {
        showToast(`Tweet approved in ${res.attempts} iteration(s)!`, 'success');
        triggerCelebration();
      } else if (res.status === 'MAX_ATTEMPTS_REACHED') {
        showToast('Max iterations reached. Best draft selected.', 'warning');
      } else if (res.input_blocked) {
        showToast(`Input Guardrail: ${res.block_reason || 'Blocked content'}`, 'error');
      } else if (res.output_blocked) {
        showToast(`Output Guardrail: ${res.block_reason || 'Blocked output'}`, 'error');
      }
    } catch (err: any) {
      const errorMsg = err?.message || 'Failed to communicate with the generation backend.';
      showToast(errorMsg, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const loadFromHistory = (item: { query: string; response: TweetGenerationResponse }) => {
    setLastQuery(item.query);
    setCurrentResponse(item.response);
    showToast('Loaded past generation from history', 'info');
  };

  return {
    health,
    isLoading,
    currentResponse,
    lastQuery,
    settings,
    updateSettings,
    history,
    clearHistory,
    removeEntry,
    handleGenerate,
    loadFromHistory,
    toast,
    showToast,
  };
}
