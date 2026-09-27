import React from 'react';
import { useTypewriter } from '../hooks/useTypewriter';

interface TypewriterHeroProps {
  hasResult: boolean;
  isLoading: boolean;
}

const TYPEWRITER_PHRASES = [
  'Craft viral tech threads that captivate your audience...',
  'Announce major product releases with self-corrected copy...',
  'Share punchy engineering insights that spark discussions...',
  'Draft high-converting announcements with quality control...',
  'Generate thought leadership posts reviewed on 5 quality rubrics...',
];

export const TypewriterHero: React.FC<TypewriterHeroProps> = ({ hasResult, isLoading }) => {
  const { currentText } = useTypewriter({
    phrases: TYPEWRITER_PHRASES,
    isLoading,
    hasResult,
  });

  return (
    <div className={`text-center ${hasResult ? 'mb-3' : 'my-4 py-2'}`}>
      <h1
        className="fw-bold mb-2"
        style={{
          fontSize: hasResult ? '1.5rem' : '2.1rem',
          letterSpacing: '-0.025em',
          color: 'var(--apple-text-primary)',
          transition: 'font-size 0.2s ease',
        }}
      >
        AI Tweet Studio
      </h1>

      <p
        className="text-secondary mx-auto mb-2"
        style={{
          maxWidth: 580,
          fontSize: hasResult ? '0.85rem' : '0.98rem',
          lineHeight: 1.5,
        }}
      >
        Stateful agentic generation with autonomous reflection review and safety guardrails.
      </p>

      {/* Animated Rotating Typewriter Line (visible when idle) */}
      {!hasResult && !isLoading && (
        <div
          className="d-flex align-items-center justify-content-center mt-2"
          style={{
            minHeight: 28,
            maxWidth: '100%',
          }}
        >
          <span
            style={{
              fontSize: '0.92rem',
              color: 'var(--apple-accent)',
              fontFamily: 'var(--font-family-apple)',
              fontWeight: 500,
              letterSpacing: '-0.01em',
            }}
          >
            {currentText}
            <span
              style={{
                display: 'inline-block',
                width: 2,
                height: '1.05em',
                background: 'var(--apple-accent)',
                marginLeft: 2,
                verticalAlign: 'middle',
                animation: 'apple-blink 1s infinite',
              }}
            />
          </span>
        </div>
      )}
    </div>
  );
};
