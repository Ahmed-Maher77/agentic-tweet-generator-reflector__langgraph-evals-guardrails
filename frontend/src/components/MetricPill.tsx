import React from 'react';
import { MetricPillProps } from '../types';

export const MetricPill: React.FC<MetricPillProps> = ({ label, value, threshold = 0.8 }) => {
  const percentage = Math.min(Math.max(Math.round(value * 100), 0), 100);
  const isPassing = value >= threshold;

  const getColorClass = () => {
    if (isPassing) return 'var(--apple-success)';
    if (value >= threshold - 0.15) return 'var(--apple-warning)';
    return 'var(--apple-danger)';
  };

  const getSubtleColor = () => {
    if (isPassing) return 'var(--apple-success-subtle)';
    if (value >= threshold - 0.15) return 'var(--apple-warning-subtle)';
    return 'var(--apple-danger-subtle)';
  };

  return (
    <div
      className="metric-tile"
      style={{
        borderLeft: `3px solid ${getColorClass()}`,
      }}
    >
      <div className="d-flex align-items-center justify-content-between">
        <span className="metric-label">{label}</span>
        <span
          style={{
            fontSize: '0.7rem',
            padding: '1px 6px',
            borderRadius: '999px',
            background: getSubtleColor(),
            color: getColorClass(),
            fontWeight: 600,
          }}
        >
          {isPassing ? 'PASS' : 'WARN'}
        </span>
      </div>

      <div className="d-flex align-items-baseline gap-1 my-1">
        <span className="metric-value" style={{ color: getColorClass() }}>
          {value.toFixed(2)}
        </span>
        <span style={{ fontSize: '0.75rem', color: 'var(--apple-text-secondary)' }}>
          / 1.00
        </span>
      </div>

      <div className="metric-progress">
        <div
          className="progress-bar"
          style={{
            width: `${percentage}%`,
            backgroundColor: getColorClass(),
          }}
        />
      </div>
    </div>
  );
};
