import React from 'react';
import { X } from 'lucide-react';
import { ModalProps } from '../../types';
import { useEscapeKey } from '../../hooks/useEscapeKey';

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  icon,
  maxWidth = 820,
  children,
}) => {
  useEscapeKey(isOpen, onClose);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 1060,
        background: 'rgba(0, 0, 0, 0.45)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.25rem',
      }}
      onClick={onClose}
    >
      <div
        className="apple-card"
        style={{
          width: '100%',
          maxWidth,
          maxHeight: '90vh',
          background: 'var(--apple-surface-1)',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.35)',
          borderRadius: 20,
          overflow: 'hidden',
          border: '1px solid var(--apple-border)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-4 px-4 px-md-5 d-flex align-items-center justify-content-between pb-2">
          <div className="d-flex align-items-center gap-2">
            {icon}
            <h5 className="fw-bold mb-0" style={{ fontSize: '1.2rem', letterSpacing: '-0.02em' }}>
              {title}
            </h5>
          </div>
          <button
            type="button"
            className="btn btn-link p-1 text-secondary"
            style={{ lineHeight: 1 }}
            onClick={onClose}
            aria-label="Close dialog"
          >
            <X size={26} />
          </button>
        </div>

        {/* Scrollable Body */}
        <div className="p-4 px-4 px-md-5 overflow-auto flex-grow-1" style={{ fontSize: '0.92rem' }}>
          {children}
        </div>
      </div>
    </div>
  );
};
