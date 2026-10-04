import React from 'react';
import { Layers, Check, RotateCw } from 'lucide-react';
import { TimelineProps } from '../types';
import { StatusBadge } from './common/StatusBadge';
import { TimelineReviewDetails } from './timeline/TimelineReviewDetails';

export const Timeline: React.FC<TimelineProps> = ({ attempts }) => {
  if (!attempts || attempts.length === 0) return null;

  return (
    <div className="vertical-timeline-wrapper mb-4">
      {/* Timeline Header */}
      <div className="d-flex align-items-center justify-content-between mb-3 pb-2 border-bottom border-opacity-10">
        <div className="d-flex align-items-center gap-2">
          <Layers size={15} className="text-primary" />
          <h6 className="fw-semibold mb-0" style={{ fontSize: '0.9rem' }}>
            Iteration Timeline
          </h6>
        </div>
        <span className="text-secondary" style={{ fontSize: '0.76rem' }}>
          {attempts.length} {attempts.length === 1 ? 'Attempt' : 'Attempts'}
        </span>
      </div>

      {/* Vertical Connected Timeline Track */}
      <div className="vertical-timeline-track">
        {attempts.map((item, index) => {
          const isLast = index === attempts.length - 1;
          const isPassed = item.passed;

          return (
            <div key={index} className={`timeline-step-row ${isLast ? 'is-last' : ''}`}>
              {/* Left Axis: Dot & Connector Line */}
              <div className="timeline-step-axis">
                <div className={`timeline-step-dot ${isPassed ? 'passed' : 'revise'}`}>
                  {isPassed ? <Check size={10} strokeWidth={3} /> : <RotateCw size={9} />}
                </div>
                {!isLast && <div className="timeline-step-line" />}
              </div>

              {/* Right Content */}
              <div className="timeline-step-content pb-3">
                <div className="d-flex align-items-center justify-content-between mb-1.5">
                  <div className="d-flex align-items-center gap-2">
                    <span className="fw-semibold" style={{ fontSize: '0.85rem' }}>
                      Attempt {item.attempt} {isLast && attempts.length > 1 ? '(Final)' : ''}
                    </span>
                    <StatusBadge status={isPassed ? 'PASS' : 'REVISE'} size="sm" />
                  </div>
                  <span className="text-secondary" style={{ fontSize: '0.74rem' }}>
                    {item.tweet.length} chars
                  </span>
                </div>

                {/* If previous attempt draft was revised, show draft text snippet */}
                {!isLast && (
                  <div className="timeline-draft-snippet mb-2">
                    "{item.tweet}"
                  </div>
                )}

                {/* Quality Scorecard and Feedback */}
                {item.review && <TimelineReviewDetails review={item.review} />}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
