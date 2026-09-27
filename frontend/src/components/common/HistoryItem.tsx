import React from 'react';
import { Trash2 } from 'lucide-react';
import { HistoryItemProps } from '../../types';
import { formatRelativeTime } from '../../utils/formatters';
import { StatusBadge } from './StatusBadge';

export const HistoryItem: React.FC<HistoryItemProps> = ({
  item,
  onSelect,
  onRemove,
  showBadge = false,
  showTweetPreview = false,
}) => {
  const tweetSnippet = item.response.tweet
    ? item.response.tweet.length > 70
      ? `${item.response.tweet.substring(0, 70)}...`
      : item.response.tweet
    : 'Blocked';

  return (
    <div
      className="sidebar-history-item"
      onClick={() => onSelect(item)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          onSelect(item);
        }
      }}
    >
      <div className="d-flex align-items-center justify-content-between mb-1">
        <span className="text-secondary" style={{ fontSize: '0.7rem' }}>
          {formatRelativeTime(item.timestamp)}
        </span>

        <div className="d-flex align-items-center gap-1">
          {showBadge && (
            <StatusBadge status={item.response.status} size="sm" />
          )}

          {onRemove && (
            <button
              type="button"
              className="delete-btn"
              onClick={(e) => {
                e.stopPropagation();
                onRemove(item.id);
              }}
              title="Delete item"
              aria-label="Delete history item"
            >
              <Trash2 size={11} />
            </button>
          )}
        </div>
      </div>

      <div className="text-truncate title" style={{ fontSize: '0.82rem' }}>
        {item.query}
      </div>

      {showTweetPreview && (
        <div className="text-secondary mt-1 text-truncate" style={{ fontSize: '0.75rem' }}>
          "{tweetSnippet}"
        </div>
      )}
    </div>
  );
};
