import React from 'react';
import { HistoryEntry } from '../../types';
import { HistoryItem } from '../common/HistoryItem';

interface SidebarRecentListProps {
  history: HistoryEntry[];
  onSelectEntry: (entry: HistoryEntry) => void;
  onRemoveEntry: (id: string) => void;
  maxItems?: number;
}

export const SidebarRecentList: React.FC<SidebarRecentListProps> = ({
  history,
  onSelectEntry,
  onRemoveEntry,
  maxItems = 8,
}) => {
  return (
    <div className="px-3 mt-4 pt-3 flex-grow-1 overflow-auto sidebar-history-container">
      <div className="d-flex align-items-center justify-content-between px-2 mb-2">
        <span
          className="text-secondary"
          style={{ fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}
        >
          Recent Drafts
        </span>
        {history.length > 0 && (
          <span className="text-secondary" style={{ fontSize: '0.72rem' }}>
            {history.length}
          </span>
        )}
      </div>

      {history.length === 0 ? (
        <div className="px-2 py-3 text-secondary" style={{ fontSize: '0.78rem' }}>
          No previous drafts. Generated tweets will appear here.
        </div>
      ) : (
        <div className="d-flex flex-column gap-1">
          {history.slice(0, maxItems).map((item) => (
            <HistoryItem
              key={item.id}
              item={item}
              onSelect={onSelectEntry}
              onRemove={onRemoveEntry}
              showBadge={false}
              showTweetPreview={false}
            />
          ))}
        </div>
      )}
    </div>
  );
};
