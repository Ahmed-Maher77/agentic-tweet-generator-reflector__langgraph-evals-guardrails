import React from 'react';
import { CheckCircle2, AlertCircle, Info } from 'lucide-react';
import { ToastMessage } from '../types';

export type { ToastMessage };

interface StatusToastProps {
  toast: ToastMessage | null;
}

export const StatusToast: React.FC<StatusToastProps> = ({ toast }) => {
  if (!toast) return null;

  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle2 size={16} className="text-success" />;
      case 'warning':
      case 'error':
        return <AlertCircle size={16} className="text-danger" />;
      default:
        return <Info size={16} className="text-primary" />;
    }
  };

  return (
    <div className="dynamic-island">
      {getIcon()}
      <span style={{ fontSize: '0.88rem', fontWeight: 500 }}>{toast.message}</span>
    </div>
  );
};
