import React from 'react';
import { ArrowUpRight } from 'lucide-react';
import { InspirationTopic, InspirationGridProps } from '../types';

export const INSPIRATION_TOPICS: InspirationTopic[] = [
  {
    title: '🚀 Product Launch Announcement',
    desc: 'LangGraph self-correcting reflection loops & quality control',
    prompt: 'Announce our new AI Tweet Generator with LangGraph self-correcting reflection loops. Emphasize multi-pass quality control and safety guardrails.',
  },
  {
    title: '🧵 Tech Thread Hook',
    desc: 'Why single-pass LLM prompts fail for high-stakes marketing copy',
    prompt: 'Write an irresistible thread opener about why single-pass LLM prompts fail for high-stakes marketing copy.',
  },
  {
    title: '💡 AI Agent Architecture',
    desc: 'Single-agent reflection vs bloated multi-agent setups',
    prompt: 'Why single-agent reflection loops outperform bloated multi-agent setups for deterministic copy generation.',
  },
  {
    title: '📈 Growth Metric Milestone',
    desc: 'Reaching 10k users with viral loops and zero ad spend',
    prompt: 'Excited to share we reached 10,000 active users this month with zero paid ads. Here are the 3 viral loops we used.',
  },
];

export const InspirationGrid: React.FC<InspirationGridProps> = ({ onSelectPrompt, disabled }) => {
  return (
    <div className="w-100">
      <div className="d-flex align-items-center justify-content-between mb-3">
        <span
          className="fw-bold"
          style={{
            fontSize: '1rem',
            color: 'var(--apple-text-primary)',
            letterSpacing: '-0.01em',
          }}
        >
          Need inspiration?
        </span>
        <span className="text-secondary" style={{ fontSize: '0.78rem' }}>
          Click any idea to load into prompt bar
        </span>
      </div>

      <div className="row g-3">
        {INSPIRATION_TOPICS.map((item, idx) => (
          <div key={idx} className="col-12 col-sm-6">
            <button
              type="button"
              className="p-3 text-start rounded-3 w-100 h-100 border-0 d-flex flex-column justify-content-between"
              style={{
                background: 'var(--apple-surface-1)',
                color: 'var(--apple-text-primary)',
                fontSize: '0.86rem',
                cursor: 'pointer',
                transition: 'border-color 0.15s ease, transform 0.1s ease, box-shadow 0.15s ease',
                border: '1px solid var(--apple-border)',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)',
              }}
              onClick={() => onSelectPrompt(item.prompt)}
              disabled={disabled}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--apple-accent)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.07)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--apple-border)';
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.03)';
              }}
            >
              <div className="d-flex align-items-center justify-content-between w-100 mb-2">
                <span className="fw-semibold text-truncate">{item.title}</span>
                <ArrowUpRight size={15} className="text-secondary flex-shrink-0 ms-1" />
              </div>
              <div className="text-secondary" style={{ fontSize: '0.78rem', lineHeight: 1.45 }}>
                {item.desc}
              </div>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
