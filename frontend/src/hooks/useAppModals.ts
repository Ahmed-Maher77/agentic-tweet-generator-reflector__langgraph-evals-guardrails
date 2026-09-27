import { useState } from 'react';

export function useAppModals() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isFeaturesOpen, setIsFeaturesOpen] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const openSettings = () => setIsSettingsOpen(true);
  const closeSettings = () => setIsSettingsOpen(false);

  const openHistory = () => setIsHistoryOpen(true);
  const closeHistory = () => setIsHistoryOpen(false);

  const openFeatures = () => setIsFeaturesOpen(true);
  const closeFeatures = () => setIsFeaturesOpen(false);

  const openMobileSidebar = () => setIsMobileSidebarOpen(true);
  const closeMobileSidebar = () => setIsMobileSidebarOpen(false);

  const toggleSidebarCollapse = () => setIsSidebarCollapsed((prev) => !prev);

  return {
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
  };
}
