/**
 * Centralized TypeScript definitions for AI Tweet Generator frontend.
 * Encompasses domain models, API DTOs, state shapes, and UI component contracts.
 */

// =====================================================================
// Domain & API Data Transfer Objects (DTOs)
// =====================================================================

export interface ReviewResult {
  decision: 'PASS' | 'REVISE';
  relevance: number;
  clarity: number;
  professionalism: number;
  engagement: number;
  requirement_adherence: number;
  issues: string[];
  feedback: string;
}

export interface AttemptRecord {
  attempt: number;
  tweet: string;
  review?: ReviewResult | null;
  passed: boolean;
}

export interface ClarificationItem {
  id: string;
  question: string;
  placeholder: string;
  key: string;
  optional?: boolean;
}

export type GenerationStatus =
  | 'SUCCESS'
  | 'NEEDS_CLARIFICATION'
  | 'INPUT_BLOCKED'
  | 'OUTPUT_BLOCKED'
  | 'MAX_ATTEMPTS_REACHED';

export interface TweetGenerationRequest {
  query: string;
  skip_clarification?: boolean;
  clarifications?: Record<string, string>;
  max_attempts?: number;
  reflection_enabled?: boolean;
  search_enabled?: boolean;
  relevance_threshold?: number;
  clarity_threshold?: number;
  professionalism_threshold?: number;
  engagement_threshold?: number;
  requirement_threshold?: number;
}

export interface TweetGenerationResponse {
  status: GenerationStatus;
  tweet: string;
  attempts: number;
  reflection_enabled: boolean;
  search_used?: boolean;
  review?: ReviewResult | null;
  attempt_history: AttemptRecord[];
  input_blocked: boolean;
  output_blocked: boolean;
  block_reason?: string | null;
  clarifications_needed?: ClarificationItem[];
  clarification_reason?: string | null;
}

export interface SystemHealth {
  status: string;
  service: string;
  agent: string;
  evaluator: string;
}

export interface HistoryEntry {
  id: string;
  timestamp: string;
  query: string;
  response: TweetGenerationResponse;
}

export interface GenerationSettings {
  maxAttempts: number;
  reflectionEnabled: boolean;
  searchEnabled: boolean;
  relevanceThreshold: number;
  clarityThreshold: number;
  professionalismThreshold: number;
  engagementThreshold: number;
  adherenceThreshold: number;
}

// =====================================================================
// UI State & Presentation Types
// =====================================================================

export type Theme = 'dark' | 'light';

export type ToastType = 'success' | 'warning' | 'info' | 'error';

export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
}

export interface InspirationTopic {
  title: string;
  desc: string;
  prompt: string;
}

export interface RubricDefinition {
  name: string;
  desc: string;
}

// =====================================================================
// Component Contract Types
// =====================================================================

export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  icon?: React.ReactNode;
  position?: 'left' | 'right';
  maxWidth?: number;
  footer?: React.ReactNode;
  children: React.ReactNode;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  icon?: React.ReactNode;
  maxWidth?: number;
  children: React.ReactNode;
}

export interface StatusBadgeProps {
  status?: GenerationStatus | 'PASS' | 'REVISE' | 'SELECTED';
  attempts?: number;
  label?: string;
  size?: 'sm' | 'md';
}

export interface HistoryItemProps {
  item: HistoryEntry;
  onSelect: (item: HistoryEntry) => void;
  onRemove?: (id: string) => void;
  showBadge?: boolean;
  showTweetPreview?: boolean;
}

export interface BrandLogoProps {
  size?: number;
  showText?: boolean;
  onClick?: () => void;
  title?: string;
}

export interface MobileTopbarProps {
  theme: Theme;
  onToggleTheme: () => void;
  onOpenSidebar: () => void;
}

export interface GuardrailAlertProps {
  response: TweetGenerationResponse;
}

export interface MetricPillProps {
  label: string;
  value: number; // 0.0 to 1.0
  threshold?: number;
}

export interface PromptEditorProps {
  query: string;
  onQueryChange: (val: string) => void;
  onGenerate: (query: string) => void;
  isLoading: boolean;
}

export interface TweetCardProps {
  response: TweetGenerationResponse;
  onShowToast: (msg: string) => void;
}

export interface TimelineProps {
  attempts: AttemptRecord[];
  reflectionEnabled: boolean;
}

export interface TimelineReviewDetailsProps {
  review: ReviewResult;
}

export interface HowItWorksCardProps {
  onSelectPrompt: (prompt: string) => void;
  disabled?: boolean;
}

export interface InspirationGridProps {
  onSelectPrompt: (prompt: string) => void;
  disabled?: boolean;
}

export interface SettingsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  settings: GenerationSettings;
  onUpdateSettings: (newSettings: GenerationSettings) => void;
  health: SystemHealth | null;
}

export interface RubricSliderProps {
  label: string;
  value: number;
  onChange: (val: number) => void;
  min?: number;
  max?: number;
  step?: number;
}

export interface HistorySidebarProps {
  isOpen: boolean;
  onClose: () => void;
  history: HistoryEntry[];
  onSelectEntry: (entry: HistoryEntry) => void;
  onClearHistory: () => void;
  onRemoveEntry: (id: string) => void;
}

export interface SystemDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  health: SystemHealth | null;
}

export interface SidebarProps {
  theme: Theme;
  onToggleTheme: () => void;
  onOpenSettings: () => void;
  onOpenHistory: () => void;
  onOpenFeatures: () => void;
  onNewTweet: () => void;
  health: SystemHealth | null;
  history: HistoryEntry[];
  onSelectHistoryEntry: (entry: HistoryEntry) => void;
  onRemoveHistoryEntry: (id: string) => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}
