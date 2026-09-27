import React from 'react';
import { Sparkles } from 'lucide-react';
import { BrandLogoProps } from '../../types';

export const BrandLogo: React.FC<BrandLogoProps> = ({
  size = 20,
  showText = true,
  onClick,
  title = 'Tweet Studio',
}) => {
  return (
    <div
      className="d-inline-flex align-items-center gap-2"
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
      title={title}
    >
      <div
        style={{
          position: 'relative',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <svg width={size} height={size} viewBox="0 0 24 24" fill="#1d9bf0">
          <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z" />
        </svg>
        <Sparkles
          size={Math.round(size * 0.52)}
          style={{
            position: 'absolute',
            top: -3,
            right: -3,
            color: '#f59e0b',
            fill: '#f59e0b',
          }}
        />
      </div>
      {showText && (
        <span className="fw-bold" style={{ fontSize: '0.98rem', letterSpacing: '-0.01em' }}>
          Tweet Studio
        </span>
      )}
    </div>
  );
};
