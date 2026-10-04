import { useState } from 'react';
import { useTheme } from './hooks/useTheme';
import { useTweetGenerator } from './hooks/useTweetGenerator';
import { useAppModals } from './hooks/useAppModals';
import { Sidebar } from './components/Sidebar';
import { PromptEditor } from './components/PromptEditor';
import { TweetCard } from './components/TweetCard';
import { Timeline } from './components/Timeline';
import { HowItWorksCard } from './components/HowItWorksCard';
import { SettingsDrawer } from './components/SettingsDrawer';
import { HistorySidebar } from './components/HistorySidebar';
import { SystemDetailsModal } from './components/SystemDetailsModal';
import { TypewriterHero } from './components/TypewriterHero';
import { StatusToast } from './components/StatusToast';
import { MobileTopbar } from './components/common/MobileTopbar';
import { GuardrailAlert } from './components/common/GuardrailAlert';
import { UserPromptBubble } from './components/common/UserPromptBubble';
import { ClarificationCard } from './components/common/ClarificationCard';
import { AmbientLoading } from './components/AmbientLoading';
import { HistoryEntry } from './types';

export function App() {
  const { theme, toggleTheme } = useTheme();
  const [userQuery, setUserQuery] = useState('');

  const {
    isSettingsOpen,
    openSettings,
    closeSettings,
    isHistoryOpen,
    openHistory,
    closeHistory,
    isFeaturesOpen,
    openFeatures,
    closeFeatures,
    isMobileSidebarOpen,
    openMobileSidebar,
    closeMobileSidebar,
    isSidebarCollapsed,
    toggleSidebarCollapse,
  } = useAppModals();

  const {
    health,
    isLoading,
    currentResponse,
    lastQuery,
    settings,
    updateSettings,
    history,
    clearHistory,
    removeEntry,
    handleGenerate,
    handleClarificationsSubmit,
    handleSkipClarifications,
    loadFromHistory,
    resetToNew,
    toast,
    showToast,
  } = useTweetGenerator();

  const handleSelectInspiration = (promptText: string) => {
    setUserQuery(promptText);
    showToast('Inspiration prompt loaded into editor', 'info');
  };

  const handleHistorySelection = (item: HistoryEntry) => {
    setUserQuery('');
    loadFromHistory(item);
  };

  const handleNewTweet = () => {
    setUserQuery('');
    resetToNew();
    showToast('Ready for a new tweet prompt', 'info');
  };

  const handlePromptSubmit = (query: string) => {
    setUserQuery('');
    handleGenerate(query);
  };

  const hasResult = Boolean(
    currentResponse &&
      (currentResponse.tweet ||
        currentResponse.input_blocked ||
        currentResponse.output_blocked ||
        currentResponse.status === 'NEEDS_CLARIFICATION')
  );

  return (
    <div className="app-layout" style={{ background: 'var(--apple-bg)' }}>
      {/* Toast Notification */}
      <StatusToast toast={toast} />

      {/* Sidebar Navigation */}
      <Sidebar
        theme={theme}
        onToggleTheme={toggleTheme}
        onOpenSettings={openSettings}
        onOpenHistory={openHistory}
        onOpenFeatures={openFeatures}
        onNewTweet={handleNewTweet}
        health={health}
        history={history}
        onSelectHistoryEntry={handleHistorySelection}
        onRemoveHistoryEntry={removeEntry}
        isOpenMobile={isMobileSidebarOpen}
        onCloseMobile={closeMobileSidebar}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={toggleSidebarCollapse}
      />

      {/* Main Viewport */}
      <div className="app-main">
        {/* Mobile Topbar */}
        <MobileTopbar
          theme={theme}
          onToggleTheme={toggleTheme}
          onOpenSidebar={openMobileSidebar}
        />

        {/* Scrollable Content Viewport */}
        <div className="app-scrollable-content">
          <div className="container-fluid mx-auto" style={{ maxWidth: 1040 }}>
            <TypewriterHero hasResult={hasResult} isLoading={isLoading} />

            {hasResult || isLoading ? (
              <div className="row justify-content-center mt-1">
                <div className="col-12 col-lg-10 col-xl-9">
                  {/* User Question / Prompt Bubble */}
                  {lastQuery && (
                    <UserPromptBubble
                      query={lastQuery}
                      onReusePrompt={(q) => {
                        setUserQuery(q);
                        showToast('Loaded prompt into editor', 'info');
                      }}
                      onShowToast={(msg) => showToast(msg, 'info')}
                    />
                  )}

                  {/* Organic Background Ambient Loading State */}
                  {isLoading && <AmbientLoading />}

                  {/* Interactive Clarification Card (Missing Details) */}
                  {!isLoading &&
                    currentResponse &&
                    currentResponse.status === 'NEEDS_CLARIFICATION' &&
                    currentResponse.clarifications_needed &&
                    currentResponse.clarifications_needed.length > 0 && (
                      <ClarificationCard
                        questions={currentResponse.clarifications_needed}
                        reason={currentResponse.clarification_reason}
                        onSubmitClarifications={handleClarificationsSubmit}
                        onSkip={handleSkipClarifications}
                        isLoading={isLoading}
                      />
                    )}

                  {/* Guardrail Blocked Alert */}
                  {!isLoading && currentResponse && <GuardrailAlert response={currentResponse} />}

                  {/* Output Tweet Showcase */}
                  {!isLoading && currentResponse && currentResponse.tweet && (
                    <TweetCard
                      response={currentResponse}
                      onShowToast={(msg) => showToast(msg, 'info')}
                    />
                  )}

                  {/* Editorial Iteration & Quality Audit */}
                  {!isLoading &&
                    currentResponse &&
                    currentResponse.attempt_history &&
                    currentResponse.attempt_history.length > 0 && (
                      <Timeline
                        attempts={currentResponse.attempt_history}
                        reflectionEnabled={currentResponse.reflection_enabled}
                      />
                    )}
                </div>
              </div>
            ) : (
              <div className="row mt-4 pt-2 justify-content-center">
                <div className="col-12 col-lg-11 col-xl-10">
                  <HowItWorksCard
                    onSelectPrompt={handleSelectInspiration}
                    disabled={isLoading}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Chat Prompt Bar */}
        <PromptEditor
          query={userQuery}
          onQueryChange={setUserQuery}
          onGenerate={handlePromptSubmit}
          isLoading={isLoading}
        />
      </div>

      {/* Modals & Drawers */}
      <SystemDetailsModal
        isOpen={isFeaturesOpen}
        onClose={closeFeatures}
        health={health}
      />

      <SettingsDrawer
        isOpen={isSettingsOpen}
        onClose={closeSettings}
        settings={settings}
        onUpdateSettings={updateSettings}
        health={health}
      />

      <HistorySidebar
        isOpen={isHistoryOpen}
        onClose={closeHistory}
        history={history}
        onSelectEntry={handleHistorySelection}
        onClearHistory={clearHistory}
        onRemoveEntry={removeEntry}
      />
    </div>
  );
}

export default App;
