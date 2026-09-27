import React from 'react';
import { AlertTriangle, MessageSquare } from 'lucide-react';
import { TimelineReviewDetailsProps } from '../../types';
import { MetricPill } from '../MetricPill';

export const TimelineReviewDetails: React.FC<TimelineReviewDetailsProps> = ({ review }) => {
  return (
    <div className="mt-3 pt-2">
      {/* Metric Row */}
      <div className="row g-2 mb-3">
        <div className="col-6 col-md">
          <MetricPill label="Relevance" value={review.relevance} threshold={0.80} />
        </div>
        <div className="col-6 col-md">
          <MetricPill label="Clarity" value={review.clarity} threshold={0.80} />
        </div>
        <div className="col-6 col-md">
          <MetricPill label="Professional" value={review.professionalism} threshold={0.80} />
        </div>
        <div className="col-6 col-md">
          <MetricPill label="Engagement" value={review.engagement} threshold={0.70} />
        </div>
        <div className="col-6 col-md">
          <MetricPill label="Adherence" value={review.requirement_adherence} threshold={0.85} />
        </div>
      </div>

      {/* Issues */}
      {review.issues && review.issues.length > 0 && (
        <div
          className="mb-2 p-2 rounded"
          style={{ background: 'var(--apple-warning-subtle)', border: '1px solid rgba(230, 126, 34, 0.2)' }}
        >
          <div className="d-flex align-items-center gap-1 text-warning mb-1" style={{ fontSize: '0.8rem', fontWeight: 600 }}>
            <AlertTriangle size={13} />
            <span>Issues:</span>
          </div>
          <ul className="mb-0 ps-3 text-secondary" style={{ fontSize: '0.8rem' }}>
            {review.issues.map((iss, i) => (
              <li key={i}>{iss}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Feedback */}
      {review.feedback && (
        <div
          className="p-2 rounded"
          style={{ background: 'var(--apple-surface-2)', border: '1px solid var(--apple-border)' }}
        >
          <div className="d-flex align-items-center gap-1 text-primary mb-1" style={{ fontSize: '0.8rem', fontWeight: 600 }}>
            <MessageSquare size={13} />
            <span>Reviewer Feedback:</span>
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--apple-text-primary)' }}>
            {review.feedback}
          </div>
        </div>
      )}
    </div>
  );
};
