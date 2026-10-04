import React, { useEffect, useMemo, useState } from 'react';
import { ClarificationItem } from '../../types';

interface ClarificationCardProps {
  questions: ClarificationItem[];
  reason?: string | null;
  onSubmitClarifications: (answers: Record<string, string>) => void;
  onSkip: () => void;
  isLoading?: boolean;
}

interface QuestionField {
  item: ClarificationItem;
  fieldKey: string;
}

export const ClarificationCard: React.FC<ClarificationCardProps> = ({
  questions,
  reason,
  onSubmitClarifications,
  onSkip,
  isLoading = false,
}) => {
  // Compute guaranteed unique, stable keys for each question input
  const fields = useMemo<QuestionField[]>(() => {
    const seen = new Set<string>();
    return questions.map((item, idx) => {
      let raw = (item.key || item.id || `detail_${idx + 1}`).trim().toLowerCase().replace(/\s+/g, '_');
      if (!raw) {
        raw = `detail_${idx + 1}`;
      }
      let uniqueKey = raw;
      let counter = 1;
      while (seen.has(uniqueKey)) {
        uniqueKey = `${raw}_${counter}`;
        counter += 1;
      }
      seen.add(uniqueKey);
      return { item, fieldKey: uniqueKey };
    });
  }, [questions]);

  const [answers, setAnswers] = useState<Record<string, string>>(() => {
    const init: Record<string, string> = {};
    fields.forEach(({ fieldKey }) => {
      init[fieldKey] = '';
    });
    return init;
  });

  // Reinitialize answers whenever questions change
  useEffect(() => {
    const init: Record<string, string> = {};
    fields.forEach(({ fieldKey }) => {
      init[fieldKey] = '';
    });
    setAnswers(init);
  }, [fields]);

  const handleInputChange = (fieldKey: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [fieldKey]: value }));
  };

  const hasAnyAnswer = Object.values(answers).some((val) => val.trim().length > 0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;
    onSubmitClarifications(answers);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      if (!isLoading && hasAnyAnswer) {
        onSubmitClarifications(answers);
      }
    }
  };

  return (
    <div className="clarification-panel fade-in-up" onKeyDown={handleKeyDown}>
      {/* Header */}
      <div className="clarification-header">
        <div className="clarification-header-text">
          <div className="clarification-title-row">
            <span className="clarification-title">Context needed</span>
            <span className="clarification-count">
              {questions.length} detail{questions.length > 1 ? 's' : ''}
            </span>
          </div>
          <p className="clarification-description">
            {reason || 'Provide specific context to avoid assumptions.'}
          </p>
        </div>
      </div>

      {/* Questions Form */}
      <form onSubmit={handleSubmit} className="clarification-form">
        <div className="clarification-fields">
          {fields.map(({ item, fieldKey }, idx) => (
            <div key={item.id || fieldKey || idx} className="clarification-field">
              <label className="clarification-field-label">
                <span className="clarification-question-text">{item.question}</span>
                {item.optional && (
                  <span className="clarification-optional-tag">optional</span>
                )}
              </label>
              <input
                type="text"
                className="clarification-text-input"
                placeholder={item.placeholder || 'Type here...'}
                value={answers[fieldKey] ?? ''}
                onChange={(e) => handleInputChange(fieldKey, e.target.value)}
                disabled={isLoading}
                autoComplete="off"
                spellCheck={false}
              />
            </div>
          ))}
        </div>

        {/* Action Controls */}
        <div className="clarification-actions">
          <button
            type="button"
            className="apple-btn apple-btn-ghost apple-btn-sm"
            onClick={onSkip}
            disabled={isLoading}
          >
            Skip and generate anyway
          </button>

          <button
            type="submit"
            className="apple-btn apple-btn-primary apple-btn-sm"
            disabled={isLoading || !hasAnyAnswer}
          >
            <span>Generate Tweet</span>
            <kbd className="clarification-shortcut-kbd">⌘↵</kbd>
          </button>
        </div>
      </form>
    </div>
  );
};

