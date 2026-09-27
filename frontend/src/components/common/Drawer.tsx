import React from 'react';
import { X } from 'lucide-react';
import { DrawerProps } from '../../types';
import { useEscapeKey } from '../../hooks/useEscapeKey';

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  icon,
  position = 'right',
  maxWidth = 380,
  footer,
  children,
}) => {
  useEscapeKey(isOpen, onClose);

  if (!isOpen) return null;

  const isRight = position === 'right';

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 1050,
        background: 'rgba(0, 0, 0, 0.4)',
        display: 'flex',
        justifyContent: isRight ? 'flex-end' : 'flex-start',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%',
          maxWidth,
          height: '100%',
          background: 'var(--apple-surface-1)',
          borderLeft: isRight ? '1px solid var(--apple-border)' : 'none',
          borderRight: !isRight ? '1px solid var(--apple-border)' : 'none',
          display: 'flex',
          flexDirection: 'column',
          overflowY: 'auto',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="p-3 d-flex align-items-center justify-content-between border-bottom border-opacity-10">
          <div className="d-flex align-items-center gap-2">
            {icon}
            <h6 className="fw-semibold mb-0" style={{ fontSize: '0.95rem' }}>{title}</h6>
          </div>
          <button
            type="button"
            className="apple-btn apple-btn-ghost apple-btn-sm"
            onClick={onClose}
            aria-label={`Close ${title}`}
          >
            <X size={16} />
          </button>
        </div>

        {/* Drawer Content */}
        <div className="p-3 flex-grow-1 overflow-auto">
          {children}
        </div>

        {/* Optional Footer */}
        {footer && (
          <div className="p-3 border-top border-opacity-10">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};
