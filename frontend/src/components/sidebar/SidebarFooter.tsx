import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { Theme } from '../../types';

interface SidebarFooterProps {
  theme: Theme;
  onToggleTheme: () => void;
}

export const SidebarFooter: React.FC<SidebarFooterProps> = ({ theme, onToggleTheme }) => {
  return (
    <div className="p-3 border-top border-opacity-10">
      <div className="d-flex align-items-center justify-content-between px-2 py-1 theme-toggle-row">
        <div
          className="d-flex align-items-center gap-2 theme-label"
          style={{ fontSize: '0.82rem', color: 'var(--apple-text-primary)' }}
        >
          {theme === 'dark' ? <Moon size={15} /> : <Sun size={15} />}
          <span>{theme === 'dark' ? 'Dark Mode' : 'Light Mode'}</span>
        </div>
        <label className="apple-switch" title="Toggle theme">
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
