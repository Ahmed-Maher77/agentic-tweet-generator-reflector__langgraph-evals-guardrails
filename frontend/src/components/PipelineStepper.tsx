import React from 'react';
import { Workflow, PenLine, Repeat, ShieldCheck } from 'lucide-react';

export const PipelineStepper: React.FC = () => {
  return (
    <div className="w-100">
      {/* Header with Workflow Icon centered */}
      <div className="d-flex align-items-center justify-content-center gap-2 mb-4 mt-2 text-center">
        <Workflow size={20} className="text-primary" />
        <h6
          className="fw-bold mb-0"
          style={{
            fontSize: '1.05rem',
            color: 'var(--apple-text-primary)',
            letterSpacing: '-0.01em',
          }}
        >
          Agent Pipeline
        </h6>
        <span className="text-secondary ms-1" style={{ fontSize: '0.8rem' }}>
          · &nbsp; 3-Stage Autonomous Execution
        </span>
      </div>

      {/* 3 Step Connected Stepper Flow as a Line of Steps */}
      <div className="stepper-track-container mb-5">
        <div className="stepper-line" />
        <div className="row g-4 position-relative">
          {/* Step 1 */}
          <div className="col-12 col-md-4">
            <div className="stepper-step-item">
              <div className="stepper-node-wrapper">
                <div className="stepper-node node-1">
                  <PenLine size={20} />
                </div>
                <div className="stepper-badge-num badge-1">1</div>
              </div>
              <div className="step-title">Prompt Input</div>
              <p className="step-desc">
                Enter your topic, headline, announcement, or thread hook into the prompt bar.
              </p>
            </div>
          </div>

          {/* Step 2 */}
          <div className="col-12 col-md-4">
            <div className="stepper-step-item">
              <div className="stepper-node-wrapper">
                <div className="stepper-node node-2">
                  <Repeat size={20} />
                </div>
                <div className="stepper-badge-num badge-2">2</div>
              </div>
              <div className="step-title">Reflection Loop</div>
              <p className="step-desc">
                LangGraph Writer drafts copy and Deterministic Reviewer iterates across 5 rubrics.
              </p>
            </div>
          </div>

          {/* Step 3 */}
          <div className="col-12 col-md-4">
            <div className="stepper-step-item">
              <div className="stepper-node-wrapper">
                <div className="stepper-node node-3">
                  <ShieldCheck size={20} />
                </div>
                <div className="stepper-badge-num badge-3">3</div>
              </div>
              <div className="step-title">Verified Output</div>
              <p className="step-desc">
                Safety guardrails verify strict character constraints and deliver high-converting copy.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
