import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { GuardrailAlertProps } from '../../types';

export const GuardrailAlert: React.FC<GuardrailAlertProps> = ({ response }) => {
  if (!response.input_blocked && !response.output_blocked) return null;

  const isInput = response.input_blocked;
  const title = isInput
    ? 'Input Blocked by Safety Guardrail'
    : 'Output Blocked by Safety Guardrail';
  const description =
    response.block_reason || 'This query was intercepted by the guardrail policy.';

  return (
    <div
      className="apple-card p-3 mb-4"
      style={{
        background: 'var(--apple-danger-subtle)',
        borderColor: 'var(--apple-danger)',
      }}
    >
      <div className="d-flex align-items-start gap-2">
        <ShieldAlert size={18} className="text-danger mt-1 flex-shrink-0" />
        <div>
          <div className="fw-semibold text-danger" style={{ fontSize: '0.9rem' }}>
            {title}
          </div>
          <div className="text-secondary" style={{ fontSize: '0.85rem' }}>
            {description}
          </div>
        </div>
      </div>
    </div>
  );
};
