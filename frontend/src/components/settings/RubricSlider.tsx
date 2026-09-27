import React from 'react';
import { RubricSliderProps } from '../../types';

export const RubricSlider: React.FC<RubricSliderProps> = ({
  label,
  value,
  onChange,
  min = 0.0,
  max = 1.0,
  step = 0.05,
}) => {
  return (
    <div className="mb-3">
      <div className="d-flex justify-content-between text-secondary mb-1" style={{ fontSize: '0.75rem' }}>
        <span>{label}</span>
        <span className="fw-bold">{value.toFixed(2)}</span>
      </div>
      <input
        type="range"
        className="form-range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        aria-label={`${label} threshold`}
      />
    </div>
  );
};
