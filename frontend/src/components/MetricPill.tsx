import React from 'react';
import { MetricPillProps } from '../types';

export const MetricPill: React.FC<MetricPillProps> = ({ label, value, threshold = 0.8 }) => {
  const percentage = Math.min(Math.max(Math.round(value * 100), 0), 100);
  const isPassing = value >= threshold;
  const isNear = value >= threshold - 0.15;

  const statusColor = isPassing
    ? 'var(--apple-success)'
    : isNear
    ? 'var(--apple-warning)'
    : 'var(--apple-danger)';

  return (
    <div className="editorial-metric-item">
      <div className="d-flex align-items-center justify-content-between mb-1">
        <span className="editorial-metric-name">{label}</span>
        <span className="editorial-metric-score" style={{ color: statusColor }}>
          {percentage}%
        </span>
      </div>
      <div className="editorial-progress-track">
        <div
          className="editorial-progress-fill"
          style={{
            width: `${percentage}%`,
            background: statusColor,
          }}
        />
      </div>
    </div>
  );
};
