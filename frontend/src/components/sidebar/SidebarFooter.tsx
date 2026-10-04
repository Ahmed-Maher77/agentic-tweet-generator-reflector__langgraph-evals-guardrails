import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { Theme } from '../../types';

interface SidebarFooterProps {
  theme: Theme;
  onToggleTheme: () => void;
  isCollapsed?: boolean;
}

export const SidebarFooter: React.FC<SidebarFooterProps> = ({
  theme,
  onToggleTheme,
  isCollapsed = false,
}) => {
  const isDark = theme === 'dark';
  const labelText = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';

  if (isCollapsed) {
    return (
      <div className="p-2 border-top border-opacity-10 d-flex justify-content-center">
        <button
          type="button"
          className="sidebar-nav-item theme-collapsed-btn"
          onClick={onToggleTheme}
          title={labelText}
          aria-label={labelText}
          style={{ width: 42, height: 42 }}
        >
          {isDark ? <Moon size={18} /> : <Sun size={18} />}
        </button>
      </div>
    );
  }

  return (
    <div className="p-3 border-top border-opacity-10">
      <div className="d-flex align-items-center justify-content-between px-2 py-1 theme-toggle-row">
        <div
          className="d-flex align-items-center gap-2 theme-label"
          style={{ fontSize: '0.82rem', color: 'var(--apple-text-primary)' }}
        >
          {isDark ? <Moon size={15} /> : <Sun size={15} />}
          <span>{isDark ? 'Dark Mode' : 'Light Mode'}</span>
        </div>
        <label className="apple-switch" title={labelText}>
          <input
            type="checkbox"
            checked={isDark}
            onChange={onToggleTheme}
            aria-label="Toggle dark/light theme"
          />
          <span className="slider" />
        </label>
      </div>
    </div>
  );
};
