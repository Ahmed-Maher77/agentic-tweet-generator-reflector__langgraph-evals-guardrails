import React from 'react';
import { PanelLeftClose, PanelLeft, X } from 'lucide-react';
import { SystemHealth } from '../../types';
import { BrandLogo } from '../common/BrandLogo';

interface SidebarHeaderProps {
  health: SystemHealth | null;
  isCollapsed: boolean;
  onToggleCollapse?: () => void;
  onCloseMobile: () => void;
}

export const SidebarHeader: React.FC<SidebarHeaderProps> = ({
  health,
  isCollapsed,
  onToggleCollapse,
  onCloseMobile,
}) => {
  return (
    <div className="sidebar-header p-3 border-bottom border-opacity-10 d-flex align-items-center justify-content-between">
      <div className="d-flex align-items-center gap-2 overflow-hidden">
        <BrandLogo
          size={22}
          showText={!isCollapsed}
          onClick={isCollapsed ? onToggleCollapse : undefined}
          title="Tweet Studio AI"
        />

        {!isCollapsed && (
          <div className="sidebar-brand-text">
            <div className="d-flex align-items-center gap-1" style={{ fontSize: '0.72rem' }}>
              <span
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  background: health ? 'var(--apple-success)' : 'var(--apple-warning)',
                  display: 'inline-block',
                }}
              />
              <span className="text-secondary">{health ? 'Connected' : 'Connecting...'}</span>
            </div>
          </div>
        )}
      </div>

      <div className="d-flex align-items-center justify-content-center">
        {onToggleCollapse && (
          <button
            type="button"
            className="d-none d-lg-flex btn btn-link p-1 text-secondary"
            onClick={onToggleCollapse}
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            aria-label={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? <PanelLeft size={17} /> : <PanelLeftClose size={17} />}
          </button>
        )}

        <button
          type="button"
          className="d-lg-none btn btn-link p-0 text-secondary"
          onClick={onCloseMobile}
          aria-label="Close sidebar"
        >
          <X size={20} />
        </button>
      </div>
    </div>
  );
};
