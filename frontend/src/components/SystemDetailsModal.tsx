import React from 'react';
import { Bot, ShieldCheck, Repeat, Cpu, CheckCircle2, Layers } from 'lucide-react';
import { SystemDetailsModalProps } from '../types';
import { Modal } from './common/Modal';

const RUBRICS = [
  { name: 'Relevance', desc: 'Topic alignment' },
  { name: 'Clarity', desc: 'Punchy brevity' },
  { name: 'Professional', desc: 'Tone & credibility' },
  { name: 'Engagement', desc: 'Viral appeal' },
  { name: 'Adherence', desc: 'Rule satisfaction' },
];

export const SystemDetailsModal: React.FC<SystemDetailsModalProps> = ({ isOpen, onClose, health }) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="System Features & Architecture"
      icon={<Layers size={22} className="text-primary" />}
      maxWidth={820}
    >
      {/* Status Header */}
      <div className="d-flex align-items-center justify-content-between pb-3 mb-5">
        <div className="d-flex align-items-center gap-2">
          <CheckCircle2 size={18} className="text-success flex-shrink-0" />
          <div>
            <div className="fw-semibold text-body" style={{ fontSize: '0.95rem' }}>
              LangGraph Stateful Engine
            </div>
            <div className="text-secondary" style={{ fontSize: '0.8rem' }}>
              {health ? `${health.service} · Status: ${health.status.toUpperCase()}` : 'Backend offline · Run uvicorn app.api.main:app'}
            </div>
          </div>
        </div>
        <span className={`apple-badge ${health ? 'apple-badge-pass' : 'apple-badge-blocked'}`} style={{ fontSize: '0.74rem' }}>
          {health ? 'Online' : 'Offline'}
        </span>
      </div>

      {/* Feature 1: Single-Agent Pattern */}
      <div className="mb-5">
        <div className="d-flex align-items-center gap-2 mb-2">
          <Bot size={20} className="text-primary flex-shrink-0" />
          <h6 className="fw-bold mb-0" style={{ fontSize: '1.02rem' }}>1. Autonomous Tweet Writer Agent</h6>
        </div>
        <p className="text-secondary mb-0 ps-4" style={{ lineHeight: 1.6 }}>
          Exactly one agent in the graph with specialized system instructions to draft high-converting, punchy X posts tailored to length constraints, engagement patterns, and your prompt.
        </p>
      </div>

      {/* Feature 2: Reflection Reviewer */}
      <div className="mb-5">
        <div className="d-flex align-items-center gap-2 mb-2">
          <Repeat size={20} className="text-warning flex-shrink-0" />
          <h6 className="fw-bold mb-0" style={{ fontSize: '1.02rem' }}>2. Deterministic Reflection Reviewer</h6>
        </div>
        <p className="text-secondary mb-3 ps-4" style={{ lineHeight: 1.6 }}>
          A dedicated evaluation node that objectively grades drafts across 5 quality dimensions:
        </p>
        <div className="row row-cols-2 row-cols-sm-3 row-cols-md-5 g-2 ps-4 mb-2">
          {RUBRICS.map((rubric) => (
            <div key={rubric.name} className="col">
              <div className="p-2 rounded-3 text-center" style={{ background: 'var(--apple-surface-2)', border: '1px solid var(--apple-border)' }}>
                <span className="fw-medium d-block" style={{ fontSize: '0.85rem' }}>{rubric.name}</span>
                <small className="text-secondary" style={{ fontSize: '0.72rem' }}>{rubric.desc}</small>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Feature 3: Safety Guardrails */}
      <div className="mb-5">
        <div className="d-flex align-items-center gap-2 mb-2">
          <ShieldCheck size={20} className="text-success flex-shrink-0" />
          <h6 className="fw-bold mb-0" style={{ fontSize: '1.02rem' }}>3. Two-Tier Safety Guardrails</h6>
        </div>
        <p className="text-secondary mb-0 ps-4" style={{ lineHeight: 1.6 }}>
          - <b>Input Guardrail</b>: Classifies prompt safety and intercepts prompt injections before invoking the LLM writer.<br />
          - <b>Output Guardrail</b>: Validates the final generated text against character constraints (≤280 chars) and safety policies.
        </p>
      </div>

      {/* Feature 4: Stateful LangGraph Loop */}
      <div className="mb-4">
        <div className="d-flex align-items-center gap-2 mb-2">
          <Cpu size={20} style={{ color: 'var(--apple-purple)' }} className="flex-shrink-0" />
          <h6 className="fw-bold mb-0" style={{ fontSize: '1.02rem' }}>4. Multi-Pass Self-Correction</h6>
        </div>
        <p className="text-secondary mb-0 ps-4" style={{ lineHeight: 1.6 }}>
          If a draft fails reviewer rubrics, feedback and concrete issues are fed directly back to the Writer Agent in stateful LangGraph cycles (up to max attempts).
        </p>
      </div>
    </Modal>
  );
};
