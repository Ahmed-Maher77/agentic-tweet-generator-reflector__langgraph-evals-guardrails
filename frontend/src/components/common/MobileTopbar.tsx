import React from 'react';
import { Menu } from 'lucide-react';
import { MobileTopbarProps } from '../../types';
import { BrandLogo } from './BrandLogo';

export const MobileTopbar: React.FC<MobileTopbarProps> = ({
  theme,
  onToggleTheme,
  onOpenSidebar,
}) => {
  return (
    <div className="mobile-topbar d-lg-none">
      <div className="d-flex align-items-center gap-2">
        <button
          type="button"
          className="btn btn-link p-0 text-body"
          onClick={onOpenSidebar}
          aria-label="Open navigation sidebar"
        >
          <Menu size={22} />
        </button>
        <BrandLogo size={19} />
      </div>

      <div className="d-flex align-items-center gap-2">
        <label className="apple-switch" title="Toggle dark/light theme">
          <input
            type="checkbox"
            checked={theme === 'dark'}
            onChange={onToggleTheme}
            aria-label="Toggle dark/light theme"
          />
          <span className="slider" />
        </label>
      </div>
    </div>
  );
};
