import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Check, Copy, Share2, Globe, Edit3 } from 'lucide-react';
import { TweetCardProps } from '../types';
import { useTweetCard } from '../hooks/useTweetCard';
import { StatusBadge } from './common/StatusBadge';
import { EngagementButtons } from './tweet/EngagementButtons';

export const TweetCard: React.FC<TweetCardProps> = ({ response, onShowToast }) => {
  const {
    copied,
    editableTweet,
    handleTweetChange,
    handleKeyDown,
    textareaRef,
    isEditing,
    toggleEditing,
    charLimit,
    currentLength,
    handleCopy,
    handleShareToTwitter,
  } = useTweetCard(response, onShowToast);

  return (
    <div className="tweet-showcase">
      {/* Header Info */}
      <div className="d-flex align-items-center justify-content-between mb-3">
        <div className="tweet-author mb-0">
          <div className="avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#1d9bf0">
              <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z" />
            </svg>
          </div>
          <div className="author-meta">
            <div className="name">
              <span>Tweet Studio</span>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="#1d9bf0" className="ms-1">
                <path d="M22.5 12.5c0-1.58-.875-2.95-2.148-3.6.154-.435.238-.905.238-1.4 0-2.21-1.79-4-4-4-.495 0-.965.084-1.4.238C14.55 2.475 13.18 1.6 11.6 1.6c-1.58 0-2.95.875-3.6 2.148-.435-.154-.905-.238-1.4-.238-2.21 0-4 1.79-4 4 4 .495 0 .965-.084 1.4-.238 1.05 1.273 2.42 2.148 4 2.148 1.58 0 2.95-.875 3.6-2.148.435.154.905.238 1.4.238 2.21 0 4-1.79 4-4 0-.495-.084-.965-.238-1.4 1.273-1.05 2.148-2.42 2.148-4zM10.2 16.2l-3.5-3.5 1.4-1.4 2.1 2.1 5.3-5.3 1.4 1.4-6.7 6.7z" />
              </svg>
            </div>
            <div className="handle">@ai_reviewer · verified draft</div>
          </div>
        </div>

        <div className="d-flex align-items-center gap-2">
          {response.search_used && (
            <span className="apple-badge apple-badge-info" title="Grounded with live web search results">
              <Globe size={12} />
              <span>Web Grounded</span>
            </span>
          )}
          <StatusBadge status={response.status} attempts={response.attempts} />
        </div>
      </div>

      {/* Tweet Body / Edit Box */}
      {isEditing ? (
        <div className="tweet-edit-container mb-3">
          <textarea
            ref={textareaRef}
            className="apple-textarea tweet-edit-textarea"
            value={editableTweet}
            onChange={handleTweetChange}
            onKeyDown={handleKeyDown}
            placeholder="Write your tweet..."
            aria-label="Edit tweet content"
          />
          <div className="tweet-edit-hint">
            <span>Press <kbd>Ctrl</kbd> + <kbd>Enter</kbd> to save</span>
          </div>
        </div>
      ) : (
        <div className="tweet-body mb-3">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              a: ({ ...props }) => (
                <a {...props} target="_blank" rel="noopener noreferrer" />
              ),
            }}
          >
            {editableTweet}
          </ReactMarkdown>
        </div>
      )}

      {/* Simulated Engagement Row */}
      <EngagementButtons />

      {/* Footer Actions */}
      <div className="d-flex align-items-center justify-content-between">
        <span
          className="font-monospace"
          style={{
            fontSize: '0.82rem',
            color: currentLength > charLimit ? 'var(--apple-danger)' : 'var(--apple-text-secondary)',
          }}
        >
          {currentLength} / {charLimit} chars
        </span>

        <div className="d-flex align-items-center gap-2">
          <button
            type="button"
            className={`apple-btn ${isEditing ? 'apple-btn-primary' : 'apple-btn-secondary'} apple-btn-sm`}
            onClick={toggleEditing}
            title={isEditing ? 'Save and preview' : 'Edit tweet'}
          >
            {isEditing ? <Check size={13} /> : <Edit3 size={13} />}
            <span>{isEditing ? 'Done' : 'Edit'}</span>
          </button>

          <button
            type="button"
            className="apple-btn apple-btn-secondary apple-btn-sm"
            onClick={handleCopy}
            title="Copy Tweet"
            aria-label="Copy tweet"
          >
            {copied ? <Check size={13} className="text-success" /> : <Copy size={13} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            type="button"
            className="apple-btn apple-btn-primary apple-btn-sm"
            onClick={handleShareToTwitter}
            title="Post to X / Twitter"
            aria-label="Share on X"
          >
            <Share2 size={13} />
            <span>Share on X</span>
          </button>
        </div>
      </div>
    </div>
  );
};
