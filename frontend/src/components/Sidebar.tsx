import React from 'react';
import { PlusCircle } from 'lucide-react';
import { SidebarProps } from '../types';
import { SidebarHeader } from './sidebar/SidebarHeader';
import { SidebarNav } from './sidebar/SidebarNav';
import { SidebarRecentList } from './sidebar/SidebarRecentList';
import { SidebarFooter } from './sidebar/SidebarFooter';

export const Sidebar: React.FC<SidebarProps> = ({
  theme,
  onToggleTheme,
  onOpenSettings,
  onOpenHistory,
  onOpenFeatures,
  onNewTweet,
  health,
  history,
  onSelectHistoryEntry,
  onRemoveHistoryEntry,
  isOpenMobile,
  onCloseMobile,
  isCollapsed = false,
  onToggleCollapse,
}) => {
  const handleNavAction = (action: () => void) => {
    action();
    if (isOpenMobile) onCloseMobile();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="d-lg-none position-fixed top-0 start-0 w-100 h-100"
          style={{ background: 'rgba(0,0,0,0.5)', zIndex: 1040 }}
          onClick={onCloseMobile}
        />
      )}

      {/* Main Sidebar Container */}
      <aside
        className={`app-sidebar d-flex flex-column ${isOpenMobile ? 'show-mobile' : ''} ${isCollapsed ? 'collapsed' : ''}`}
      >
        <SidebarHeader
          health={health}
          isCollapsed={isCollapsed}
          onToggleCollapse={onToggleCollapse}
          onCloseMobile={onCloseMobile}
        />

        {/* New Tweet Action Button */}
        <div className="p-3 mb-2">
          <button
            type="button"
            className="apple-btn apple-btn-primary w-100"
            onClick={() => handleNavAction(onNewTweet)}
          >
            <PlusCircle size={16} />
            <span>New Tweet Draft</span>
          </button>
        </div>

        {/* Navigation Section */}
        <SidebarNav
          onOpenSettings={() => handleNavAction(onOpenSettings)}
          onOpenFeatures={() => handleNavAction(onOpenFeatures)}
          onOpenHistory={() => handleNavAction(onOpenHistory)}
          historyCount={history.length}
        />

        {/* Recent Drafts List */}
        <SidebarRecentList
          history={history}
          onSelectEntry={(entry) => handleNavAction(() => onSelectHistoryEntry(entry))}
          onRemoveEntry={onRemoveHistoryEntry}
        />

        {/* Bottom Theme Controls */}
        <SidebarFooter
          theme={theme}
          onToggleTheme={onToggleTheme}
          isCollapsed={isCollapsed}
        />
      </aside>
    </>
  );
};
