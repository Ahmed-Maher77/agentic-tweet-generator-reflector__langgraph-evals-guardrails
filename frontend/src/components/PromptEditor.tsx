import React from 'react';
import { ArrowUp, RefreshCw } from 'lucide-react';
import { PromptEditorProps } from '../types';
import { usePromptEditor } from '../hooks/usePromptEditor';

export const PromptEditor: React.FC<PromptEditorProps> = ({
  query,
  onQueryChange,
  onGenerate,
  isLoading,
}) => {
  const { textareaRef, handleSubmit, handleKeyDown } = usePromptEditor({
    query,
    isLoading,
    onGenerate,
  });

  return (
    <div className="bottom-chat-wrapper">
      <form onSubmit={handleSubmit} className="bottom-chat-container">
        {/* Auto-expanding Textarea */}
        <textarea
          ref={textareaRef}
          className="bottom-chat-textarea"
          rows={1}
          placeholder="Ask Tweet Studio to draft an announcement, thread opener, or post..."
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />

        {/* Action Button */}
        <button
          type="submit"
          className="apple-btn-circle"
          disabled={!query.trim() || isLoading}
          title={isLoading ? 'Generating in LangGraph...' : 'Generate Tweet (Enter)'}
          aria-label="Generate Tweet"
        >
          {isLoading ? (
            <RefreshCw size={16} className="animate-spin-smooth" />
          ) : (
            <ArrowUp size={18} strokeWidth={2.5} />
          )}
        </button>
      </form>
      <div className="text-center mt-1 text-secondary" style={{ fontSize: '0.72rem' }}>
        Press <kbd style={{ background: 'var(--apple-surface-2)', padding: '1px 5px', borderRadius: 3, color: 'var(--apple-text-primary)' }}>Enter</kbd> to generate · <kbd style={{ background: 'var(--apple-surface-2)', padding: '1px 5px', borderRadius: 3, color: 'var(--apple-text-primary)' }}>Shift + Enter</kbd> for new line
      </div>
    </div>
  );
};
