import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { TimelineProps } from '../types';
import { useTimeline } from '../hooks/useTimeline';
import { StatusBadge } from './common/StatusBadge';
import { TimelineReviewDetails } from './timeline/TimelineReviewDetails';

export const Timeline: React.FC<TimelineProps> = ({ attempts, reflectionEnabled }) => {
  const { expandedIndex, toggleExpand } = useTimeline(attempts);

  if (!attempts || attempts.length === 0) return null;

  return (
    <div className="apple-card p-3 mb-4">
      <div className="d-flex align-items-center justify-content-between mb-3 pb-2 border-bottom border-opacity-10">
        <div>
          <h6 className="fw-semibold mb-0" style={{ fontSize: '0.95rem' }}>
            Iteration History ({attempts.length} {attempts.length === 1 ? 'Attempt' : 'Attempts'})
          </h6>
          <span className="text-secondary" style={{ fontSize: '0.8rem' }}>
            {reflectionEnabled ? 'Evaluator review breakdown per attempt' : 'Single-pass baseline'}
          </span>
        </div>
      </div>

      <div>
        {attempts.map((item, index) => {
          const isExpanded = expandedIndex === index;
          const isFinal = index === attempts.length - 1;
          const review = item.review;

          return (
            <div key={index} className="timeline-item">
              <div
                className="d-flex align-items-center justify-content-between"
                style={{ cursor: 'pointer' }}
                onClick={() => toggleExpand(index)}
              >
                <div className="d-flex align-items-center gap-2">
                  <span className="fw-medium" style={{ fontSize: '0.9rem' }}>
                    Attempt {item.attempt}
                  </span>
                  <StatusBadge status={item.passed ? 'PASS' : 'REVISE'} size="sm" />
                  {isFinal && <StatusBadge status="SELECTED" size="sm" />}
                </div>

                <div className="d-flex align-items-center gap-2 text-secondary" style={{ fontSize: '0.8rem' }}>
                  <span>{item.tweet.length} chars</span>
                  {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                </div>
              </div>

              {/* Tweet Content: Plain snippet when collapsed, rendered Markdown when expanded */}
              {!isExpanded ? (
                <div className="text-secondary mt-1" style={{ fontSize: '0.85rem' }}>
                  "{item.tweet.length > 100 ? `${item.tweet.substring(0, 100)}...` : item.tweet}"
                </div>
              ) : (
                <div
                  className="tweet-body mt-2 p-2 rounded"
                  style={{
                    background: 'var(--apple-surface-2)',
                    border: '1px solid var(--apple-border)',
                    fontSize: '0.92rem',
                  }}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      a: ({ ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" />,
                    }}
                  >
                    {item.tweet}
                  </ReactMarkdown>
                </div>
              )}

              {/* Expanded details */}
              {isExpanded && review && <TimelineReviewDetails review={review} />}
            </div>
          );
        })}
      </div>
    </div>
  );
};
