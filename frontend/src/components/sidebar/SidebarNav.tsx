import React from 'react';
import { Layers, Sliders, Info, History } from 'lucide-react';

interface SidebarNavProps {
  onOpenSettings: () => void;
  onOpenFeatures: () => void;
  onOpenHistory: () => void;
  historyCount: number;
}

export const SidebarNav: React.FC<SidebarNavProps> = ({
  onOpenSettings,
  onOpenFeatures,
  onOpenHistory,
  historyCount,
}) => {
  return (
    <div className="px-3 mb-2">
      <div
        className="sidebar-section-title text-secondary px-2 mb-1"
        style={{ fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}
      >
        Workspace
      </div>
      <nav className="d-flex flex-column gap-1">
        <button
          type="button"
          className="sidebar-nav-item active"
          title="Prompt Studio"
        >
          <Layers size={16} className="flex-shrink-0" />
          <span>Prompt Studio</span>
        </button>

        <button
          type="button"
          className="sidebar-nav-item"
          title="Inspector Settings"
          onClick={onOpenSettings}
        >
          <Sliders size={16} className="flex-shrink-0" />
          <span>Inspector Settings</span>
        </button>

        <button
          type="button"
          className="sidebar-nav-item"
          title="System Features & Specs"
          onClick={onOpenFeatures}
        >
          <Info size={16} className="flex-shrink-0" />
          <span>System Specs</span>
        </button>

        <button
          type="button"
          className="sidebar-nav-item"
          title="Full History Archive"
          onClick={onOpenHistory}
        >
          <History size={16} className="flex-shrink-0" />
          <span>Full History Archive</span>
          {historyCount > 0 && (
            <span className="badge-count ms-auto">{historyCount}</span>
          )}
        </button>
      </nav>
    </div>
  );
};
