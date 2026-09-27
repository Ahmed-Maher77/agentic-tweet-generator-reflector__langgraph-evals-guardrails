import React from 'react';
import { Sliders, Check } from 'lucide-react';
import { GenerationSettings, SettingsDrawerProps } from '../types';
import { Drawer } from './common/Drawer';
import { RubricSlider } from './settings/RubricSlider';

export const SettingsDrawer: React.FC<SettingsDrawerProps> = ({
  isOpen,
  onClose,
  settings,
  onUpdateSettings,
  health,
}) => {
  const updateField = <K extends keyof GenerationSettings>(field: K, val: GenerationSettings[K]) => {
    onUpdateSettings({ ...settings, [field]: val });
  };

  const footer = (
    <div className="d-flex justify-content-end">
      <button
        type="button"
        className="apple-btn apple-btn-primary apple-btn-sm"
        onClick={onClose}
      >
        <Check size={14} />
        <span>Done</span>
      </button>
    </div>
  );

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title="Inspector Settings"
      icon={<Sliders size={18} className="text-primary" />}
      footer={footer}
    >
      {/* Status info */}
      {health && (
        <div className="pb-3 mb-3 border-bottom border-opacity-10" style={{ fontSize: '0.8rem' }}>
          <div className="text-success fw-medium mb-1">✓ Backend: {health.status}</div>
          <div className="text-secondary">{health.agent}</div>
        </div>
      )}

      {/* Reflection Toggle */}
      <div className="pb-3 mb-3 border-bottom border-opacity-10">
        <div className="d-flex align-items-center justify-content-between">
          <div>
            <div className="fw-medium" style={{ fontSize: '0.9rem' }}>Reflection Loop</div>
            <div className="text-secondary" style={{ fontSize: '0.75rem' }}>Self-correcting evaluation iterations</div>
          </div>
          <label className="apple-switch" title="Toggle reflection loop">
            <input
              type="checkbox"
              checked={settings.reflectionEnabled}
              onChange={(e) => updateField('reflectionEnabled', e.target.checked)}
              aria-label="Reflection Loop"
            />
            <span className="slider" />
          </label>
        </div>
      </div>

      {/* Web Search Grounding Toggle */}
      <div className="pb-3 mb-3 border-bottom border-opacity-10">
        <div className="d-flex align-items-center justify-content-between">
          <div>
            <div className="fw-medium" style={{ fontSize: '0.9rem' }}>Web Search Grounding</div>
            <div className="text-secondary" style={{ fontSize: '0.75rem' }}>Tavily + DuckDuckGo fallback</div>
          </div>
          <label className="apple-switch" title="Toggle web search grounding">
            <input
              type="checkbox"
              checked={settings.searchEnabled}
              onChange={(e) => updateField('searchEnabled', e.target.checked)}
              aria-label="Web Search Grounding"
            />
            <span className="slider" />
          </label>
        </div>
      </div>

      {/* Iteration Limit */}
      <div className="pb-3 mb-3 border-bottom border-opacity-10">
        <div className="d-flex align-items-center justify-content-between mb-2">
          <span className="fw-medium" style={{ fontSize: '0.85rem' }}>Max Attempts</span>
          <span className="apple-badge apple-badge-info">{settings.maxAttempts}</span>
        </div>
        <input
          type="range"
          className="form-range"
          min={1}
          max={5}
          step={1}
          value={settings.maxAttempts}
          onChange={(e) => updateField('maxAttempts', parseInt(e.target.value, 10))}
          aria-label="Max Attempts"
        />
        <div className="d-flex justify-content-between text-secondary" style={{ fontSize: '0.7rem' }}>
          <span>1</span>
          <span>3 (Default)</span>
          <span>5</span>
        </div>
      </div>

      {/* Rubrics */}
      <div className="pb-2">
        <div className="fw-medium mb-3" style={{ fontSize: '0.85rem' }}>
          Rubric Thresholds (PASS requirement)
        </div>

        <RubricSlider
          label="Relevance"
          value={settings.relevanceThreshold}
          onChange={(v) => updateField('relevanceThreshold', v)}
        />
        <RubricSlider
          label="Clarity"
          value={settings.clarityThreshold}
          onChange={(v) => updateField('clarityThreshold', v)}
        />
        <RubricSlider
          label="Professionalism"
          value={settings.professionalismThreshold}
          onChange={(v) => updateField('professionalismThreshold', v)}
        />
        <RubricSlider
          label="Engagement"
          value={settings.engagementThreshold}
          onChange={(v) => updateField('engagementThreshold', v)}
        />
        <RubricSlider
          label="Requirement Adherence"
          value={settings.adherenceThreshold}
          onChange={(v) => updateField('adherenceThreshold', v)}
        />
      </div>
    </Drawer>
  );
};
