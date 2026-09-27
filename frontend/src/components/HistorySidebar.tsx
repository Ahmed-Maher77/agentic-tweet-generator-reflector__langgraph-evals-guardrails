import React from 'react';
import { Clock, Trash2 } from 'lucide-react';
import { HistorySidebarProps } from '../types';
import { Drawer } from './common/Drawer';
import { HistoryItem } from './common/HistoryItem';

export const HistorySidebar: React.FC<HistorySidebarProps> = ({
  isOpen,
  onClose,
  history,
  onSelectEntry,
  onClearHistory,
  onRemoveEntry,
}) => {
  const footer = history.length > 0 ? (
    <button
      type="button"
      className="apple-btn apple-btn-secondary apple-btn-sm w-100 text-danger"
      onClick={onClearHistory}
    >
      <Trash2 size={13} />
      <span>Clear All History</span>
    </button>
  ) : null;

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title="History Archive"
      icon={<Clock size={18} className="text-primary" />}
      position="left"
      maxWidth={360}
      footer={footer}
    >
      {history.length === 0 ? (
        <div className="text-center py-5 text-secondary" style={{ fontSize: '0.85rem' }}>
          No history yet.
        </div>
      ) : (
        <div className="d-flex flex-column gap-2">
          {history.map((item) => (
            <HistoryItem
              key={item.id}
              item={item}
              onSelect={(selected) => {
                onSelectEntry(selected);
                onClose();
              }}
              onRemove={onRemoveEntry}
              showBadge={true}
              showTweetPreview={true}
            />
          ))}
        </div>
      )}
    </Drawer>
  );
};
