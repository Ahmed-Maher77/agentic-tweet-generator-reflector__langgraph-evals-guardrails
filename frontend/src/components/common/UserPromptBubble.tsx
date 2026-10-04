import React, { useState } from 'react';
import { User, Copy, Check, CornerDownLeft } from 'lucide-react';

interface UserPromptBubbleProps {
  query: string;
  onReusePrompt?: (query: string) => void;
  onShowToast?: (msg: string) => void;
}

export const UserPromptBubble: React.FC<UserPromptBubbleProps> = ({
  query,
  onReusePrompt,
  onShowToast,
}) => {
  const [copied, setCopied] = useState(false);

  if (!query || !query.trim()) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(query);
      setCopied(true);
      onShowToast?.('Prompt copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      onShowToast?.('Failed to copy to clipboard');
    }
  };

  return (
    <div className="user-query-card fade-in-up mb-3">
      <div className="d-flex align-items-start justify-content-between gap-3">
        {/* User Identity & Query Content */}
        <div className="d-flex align-items-start gap-3 flex-grow-1 min-w-0">
          <div className="user-query-avatar flex-shrink-0" aria-hidden="true">
            <User size={15} />
          </div>
          <div className="user-query-content-wrap flex-grow-1 min-w-0">
            <div className="d-flex align-items-center gap-2 mb-1">
              <span className="user-query-author">You</span>
            </div>
            <p className="user-query-text mb-0">
              {query}
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="user-query-actions d-flex align-items-center gap-1 flex-shrink-0">
          {onReusePrompt && (
            <button
              type="button"
              className="apple-icon-btn"
              onClick={() => onReusePrompt(query)}
              title="Edit / Reuse prompt"
              aria-label="Edit or reuse this prompt"
            >
              <CornerDownLeft size={15} />
            </button>
          )}
          <button
            type="button"
            className="apple-icon-btn"
            onClick={handleCopy}
            title={copied ? 'Copied' : 'Copy prompt'}
            aria-label="Copy prompt"
          >
            {copied ? <Check size={15} className="text-success" /> : <Copy size={15} />}
          </button>
        </div>
      </div>
    </div>
  );
};
