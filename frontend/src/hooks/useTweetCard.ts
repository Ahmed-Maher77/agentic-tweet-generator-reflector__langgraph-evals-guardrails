import { useState, useEffect } from 'react';
import { TweetGenerationResponse } from '../types';

export function useTweetCard(
  response: TweetGenerationResponse,
  onShowToast: (msg: string) => void,
  charLimit: number = 280
) {
  const [copied, setCopied] = useState(false);
  const [editableTweet, setEditableTweet] = useState(response.tweet);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    setEditableTweet(response.tweet);
    setIsEditing(false);
  }, [response.tweet]);

  const currentLength = editableTweet.length;

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
    isEditing,
    toggleEditing,
    charLimit,
    currentLength,
    handleCopy,
    handleShareToTwitter,
  };
}
