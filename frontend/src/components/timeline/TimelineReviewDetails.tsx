import React from 'react';
import { PenTool, HelpCircle } from 'lucide-react';
import { TimelineReviewDetailsProps } from '../../types';
import { MetricPill } from '../MetricPill';

export const TimelineReviewDetails: React.FC<TimelineReviewDetailsProps> = ({ review }) => {
  const meaningfulIssues = (review.issues || []).filter((issue) => {
    const text = issue.trim().toLowerCase();
    return (
      text.length > 0 &&
      !text.includes('no significant issue') &&
      !text.includes('no issue') &&
      !text.includes('none') &&
      !text.includes('all criteria met') &&
      !text.includes('no revision')
    );
  });

  return (
    <div className="timeline-review-section mt-4">
      {/* Reduced 5-Metric Strip */}
      <div className="editorial-metrics-strip mb-4">
        <MetricPill label="Relevance" value={review.relevance} threshold={0.80} />
        <MetricPill label="Clarity" value={review.clarity} threshold={0.80} />
        <MetricPill label="Tone" value={review.professionalism} threshold={0.80} />
        <MetricPill label="Engagement" value={review.engagement} threshold={0.70} />
        <MetricPill label="Adherence" value={review.requirement_adherence} threshold={0.85} />
      </div>

      <div className="d-flex flex-column gap-2">
        {/* Editor Feedback Memo (Clean minimal quote) */}
        {review.feedback && (
          <div className="editorial-memo-quote">
            <div className="d-flex align-items-center gap-2 mb-1 text-primary">
              <PenTool size={12} />
              <span className="editorial-memo-title">Evaluation Note</span>
            </div>
            <p className="editorial-memo-body mb-0">
              {review.feedback}
            </p>
          </div>
        )}

        {/* Actionable Revisions (Only when real issues exist) */}
        {meaningfulIssues.length > 0 && (
          <div className="editorial-critique-quote">
            <div className="d-flex align-items-center gap-2 mb-1 text-warning">
              <HelpCircle size={13} className="flex-shrink-0" />
              <span className="editorial-critique-title">Revisions Requested</span>
            </div>
            <ul className="editorial-critique-list mb-0">
              {meaningfulIssues.map((issue, idx) => (
                <li key={idx} className="editorial-critique-item">
                  <span className="bullet-dot" />
                  <span>{issue}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
