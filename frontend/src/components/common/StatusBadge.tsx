import React from 'react';
import { CheckCircle, AlertTriangle, ShieldAlert, AlertCircle } from 'lucide-react';
import { StatusBadgeProps } from '../../types';

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  attempts,
  label,
  size = 'md',
}) => {
  const iconSize = size === 'sm' ? 10 : 12;

  switch (status) {
    case 'SUCCESS':
    case 'PASS':
      return (
        <span className="apple-badge apple-badge-pass">
          <CheckCircle size={iconSize} />
          <span>
            {label || (attempts ? `Passed Review (${attempts} ${attempts === 1 ? 'attempt' : 'attempts'})` : 'Approved')}
          </span>
        </span>
      );

    case 'MAX_ATTEMPTS_REACHED':
      return (
        <span className="apple-badge apple-badge-revise">
          <AlertTriangle size={iconSize} />
          <span>{label || (attempts ? `Max Iterations (${attempts})` : 'Max Iterations')}</span>
        </span>
      );

    case 'REVISE':
      return (
        <span className="apple-badge apple-badge-revise">
          <AlertCircle size={iconSize} />
          <span>{label || 'Revision'}</span>
        </span>
      );

    case 'INPUT_BLOCKED':
    case 'OUTPUT_BLOCKED':
      return (
        <span className="apple-badge apple-badge-blocked">
          <ShieldAlert size={iconSize} />
          <span>{label || 'Guardrail Intercepted'}</span>
        </span>
      );

    case 'SELECTED':
      return (
        <span className="apple-badge apple-badge-purple">
          <span>{label || 'Selected'}</span>
        </span>
      );

    default:
      return null;
  }
};
