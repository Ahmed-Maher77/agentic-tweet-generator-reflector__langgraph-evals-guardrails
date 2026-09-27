import React from 'react';
import { Heart, Repeat2, MessageCircle, Bookmark } from 'lucide-react';
import { useEngagement } from '../../hooks/useEngagement';

export const EngagementButtons: React.FC = () => {
  const { isLiked, toggleLiked, isBookmarked, toggleBookmarked } = useEngagement();

  return (
    <div
      className="d-flex align-items-center justify-content-between py-2 border-top border-bottom border-opacity-10 text-secondary mb-3"
      style={{ fontSize: '0.8rem' }}
    >
      <button
        type="button"
        className="btn btn-link text-decoration-none p-0 text-secondary d-flex align-items-center gap-1"
        style={{ fontSize: '0.8rem' }}
        aria-label="Reply"
      >
        <MessageCircle size={15} />
        <span>Reply</span>
      </button>

      <button
        type="button"
        className="btn btn-link text-decoration-none p-0 text-secondary d-flex align-items-center gap-1"
        style={{ fontSize: '0.8rem' }}
        aria-label="Repost"
      >
        <Repeat2 size={16} />
        <span>Repost</span>
      </button>

      <button
        type="button"
        className={`btn btn-link text-decoration-none p-0 d-flex align-items-center gap-1 ${isLiked ? 'text-danger' : 'text-secondary'}`}
        onClick={toggleLiked}
        style={{ fontSize: '0.8rem' }}
        aria-label={isLiked ? 'Unlike' : 'Like'}
      >
        <Heart size={15} fill={isLiked ? '#ef4444' : 'none'} />
        <span>{isLiked ? '1' : 'Like'}</span>
      </button>

      <button
        type="button"
        className={`btn btn-link text-decoration-none p-0 d-flex align-items-center gap-1 ${isBookmarked ? 'text-primary' : 'text-secondary'}`}
        onClick={toggleBookmarked}
        style={{ fontSize: '0.8rem' }}
        aria-label={isBookmarked ? 'Remove Bookmark' : 'Bookmark'}
      >
        <Bookmark size={15} fill={isBookmarked ? 'var(--apple-accent)' : 'none'} />
        <span>Bookmark</span>
      </button>
    </div>
  );
};
