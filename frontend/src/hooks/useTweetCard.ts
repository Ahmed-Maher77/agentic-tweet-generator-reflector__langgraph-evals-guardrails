import { useState, useEffect, useRef, ChangeEvent, KeyboardEvent } from 'react';
import { TweetGenerationResponse } from '../types';

export function useTweetCard(
  response: TweetGenerationResponse,
  onShowToast: (msg: string) => void,
  charLimit: number = 280
) {
  const [copied, setCopied] = useState(false);
  const [editableTweet, setEditableTweet] = useState(response.tweet);
  const [isEditing, setIsEditing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setEditableTweet(response.tweet);
    setIsEditing(false);
  }, [response.tweet]);

  // Focus and auto-resize textarea when entering edit mode
  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      const len = textareaRef.current.value.length;
      textareaRef.current.setSelectionRange(len, len);

      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.max(120, textareaRef.current.scrollHeight)}px`;
    }
  }, [isEditing]);

  const currentLength = editableTweet.length;

  const handleTweetChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setEditableTweet(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.max(120, e.target.scrollHeight)}px`;
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      setIsEditing(false);
      onShowToast('Tweet draft updated');
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(editableTweet);
      setCopied(true);
      onShowToast('Copied tweet to clipboard');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      onShowToast('Failed to copy');
    }
  };

  const handleShareToTwitter = () => {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(editableTweet)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const toggleEditing = () => {
    setIsEditing((prev) => !prev);
  };

  return {
    copied,
    editableTweet,
    setEditableTweet,
    handleTweetChange,
    handleKeyDown,
    textareaRef,
    isEditing,
    toggleEditing,
    charLimit,
    currentLength,
    handleCopy,
    handleShareToTwitter,
  };
}

