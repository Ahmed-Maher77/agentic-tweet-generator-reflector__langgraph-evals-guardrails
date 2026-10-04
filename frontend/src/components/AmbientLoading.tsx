import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';

const LOADING_STAGES = [
  'Synthesizing creative angles & concepts...',
  'Consulting real-time search & context...',
  'Reflection Evaluator reviewing tone & viral punch...',
  'Polishing draft for maximum audience engagement...',
];

export const AmbientLoading: React.FC = () => {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStageIndex((prev) => (prev + 1) % LOADING_STAGES.length);
    }, 2400);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="ambient-loading-canvas my-5 py-4 d-flex align-items-center justify-content-center">
      <div className="d-flex align-items-center justify-content-center gap-3">
        <Loader2 size={20} className="animate-spin-smooth text-primary flex-shrink-0" />
        <span className="fw-semibold text-body" style={{ fontSize: '1.05rem', letterSpacing: '-0.01em' }}>
          {LOADING_STAGES[stageIndex]}
        </span>
      </div>
    </div>
  );
};

