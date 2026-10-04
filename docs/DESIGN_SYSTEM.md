# AI Tweet Generator — Design System Specification

Welcome to the **Design System** specification for the AI Tweet Generator Assistant. This document captures the visual philosophy, design tokens, typography hierarchies, layout mechanics, component library, logic separation hooks, and accessibility guidelines powering the modern **Apple HIG + Developer Minimalist** user interface.

---

## 📑 Table of Contents
1. [Design Philosophy & Aesthetic](#1-design-philosophy--aesthetic)
2. [Design Tokens & Color Palette](#2-design-tokens--color-palette)
3. [Typography Hierarchy](#3-typography-hierarchy)
4. [Layout & Grid Architecture](#4-layout--grid-architecture)
5. [Component Library & Specifications](#5-component-library--specifications)
6. [Logic Separation & Custom Hooks Architecture](#6-logic-separation--custom-hooks-architecture)
7. [Interactive Feedback & Motion](#7-interactive-feedback--motion)
8. [Accessibility & Ergonomics](#8-accessibility--ergonomics)

---

## 1. Design Philosophy & Aesthetic

The AI Tweet Generator UI is built on modern principles inspired by **Apple Human Interface Guidelines (HIG)** and premium developer tools (Linear, Vercel, Apple Developer):

- **Content-First Simplicity**: Clean, unboxed information flow where content blends directly into the page rather than being trapped in nested cards.
- **Atmospheric Depth**: Subtle ambient side illumination (`--apple-bg-side-glow`) combined with a crisp `32px × 32px` technical grid pattern (`--apple-grid-color`).
- **Harmonious Dual Themes**: Seamless light and dark mode implementations using custom CSS custom properties without abrupt contrast jumps.
- **Physicality & Tactile Motion**: Responsive hover physics, smooth ease-in-out transitions (`0.15s`), and interactive celebratory confetti.

---

## 2. Design Tokens & Color Palette

All colors and surfaces are organized as semantic CSS custom properties defined in `frontend/src/scss/_apple-theme.scss` and `frontend/src/scss/_variables.scss`.

### 2.1 Dual-Theme Neutral Palette

| Token | Light Mode Value | Dark Mode Value | Usage |
| :--- | :--- | :--- | :--- |
| `--apple-bg` | `#f8f9fa` (Slate-50) | `#121214` (Zinc-950) | Primary page background |
| `--apple-surface-1` | `#ffffff` (Clean White) | `#18181b` (Zinc-900) | Primary surface (Sidebar, Prompt Bar, Cards, Modals) |
| `--apple-surface-2` | `#f1f3f5` (Gray-100) | `#222226` (Zinc-800) | Secondary surface (Hover states, Metric Tiles, Badges) |
| `--apple-surface-3` | `#e9ecef` (Gray-200) | `#2d2d32` (Zinc-700) | Tertiary surface (Pill counts, progress track, borders) |
| `--apple-border` | `#dee2e6` (Gray-300) | `#2e2e33` (Zinc-750) | Dividers, card strokes, input outlines |
| `--apple-text-primary` | `#212529` (Gray-900) | `#f4f4f5` (Zinc-100) | Main headings, body text, primary labels |
| `--apple-text-secondary`| `#6c757d` (Gray-600) | `#a1a1aa` (Zinc-400) | Subtitles, helper descriptions, timestamps |
| `--apple-text-tertiary` | `#adb5bd` (Gray-500) | `#71717a` (Zinc-500) | Placeholders, inactive icons, subtle hints |
| `--apple-grid-color` | `rgba(0, 0, 0, 0.045)` | `rgba(255, 255, 255, 0.04)` | Main canvas 32px grid pattern |
| `--apple-bg-side-glow` | `rgba(255, 255, 255, 0.85)` | `rgba(255, 255, 255, 0.035)` | Subtle lateral ambient illumination |

### 2.2 Semantic Accent Tokens

| Semantic Role | Token | Light Mode | Dark Mode | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Accent** | `--apple-accent` | `#0066cc` | `#2997ff` | Focus rings, active buttons, Stage 1 indicators |
| **Accent Hover** | `--apple-accent-hover` | `#0052a3` | `#54aeff` | Interactive button hover states |
| **Accent Subtle** | `--apple-accent-subtle`| `#e6f0fa` | `#162438` | Badge backdrops, active sidebar items |
| **Success** | `--apple-success` | `#28a745` | `#30d158` | Verified outputs, PASS verdicts, online status |
| **Warning** | `--apple-warning` | `#e67e22` | `#ff9f0a` | REVISE verdicts, Stage 2 reflection loops |
| **Danger** | `--apple-danger` | `#dc3545` | `#ff453a` | Guardrail blocked alerts, delete actions |
| **Purple/AI** | `--apple-purple` | `#6f42c1` | `#bf5af2` | AI system specs, self-correction highlights |

---

## 3. Typography Hierarchy

The typographic system utilizes modern geometric sans-serif typefaces tailored for crisp rendering on high-DPI displays.

### 3.1 Font Stacks
- **Main Font Stack (`$font-family-apple`)**:
  ```css
  font-family: 'Udemy Sans', 'Noto Sans JP', 'Vazirmatn', -apple-system, 
               BlinkMacSystemFont, Roboto, 'Segoe UI', Helvetica, Arial, 
               sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
  ```
- **Monospace Code Stack (`$font-family-code`)**:
  ```css
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  ```

### 3.2 Type Scale

| Level | Size | Weight | Line Height | Tracking | Application |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hero Title** | `1.75rem` (28px) – `2.1rem` (34px) | 800 (Extrabold) | 1.2 | `-0.03em` | Main application heading |
| **Typewriter Subtitle**| `0.98rem` (15.5px) | 500 (Medium) | 1.4 | `-0.01em` | Animated terminal hero taglines |
| **Section Header** | `1.15rem` (18.5px) | 700 (Bold) | 1.3 | `-0.02em` | Drawer titles, modal headings |
| **Card / Step Title** | `0.98rem` (15.5px) | 600 (Semibold) | 1.3 | `-0.01em` | Stepper stage names, inspiration titles |
| **Body Primary** | `0.92rem` (14.7px) | 400 (Regular) | 1.55 | `0` | Tweet output body, modal text |
| **Secondary Description**| `0.82rem` (13px) | 400 (Regular) | 1.45 | `0` | Stepper explanations, metadata labels |
| **Micro Caption / Pill** | `0.72rem` (11.5px) | 600 (Semibold) | 1.2 | `+0.01em` | Status badges, metric labels, counts |

---

## 4. Layout & Grid Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│ .app-layout                                                            │
│ ┌────────────────┐ ┌─────────────────────────────────────────────────┐ │
│ │  .app-sidebar  │ │  .app-main (Ambient Grid + Side Glow)           │ │
│ │  (260px / 68px)│ │  ┌───────────────────────────────────────────┐  │ │
│ │                │ │  │ .app-scrollable-content                   │  │ │
│ │  - SidebarHead │ │  │                                           │  │ │
│ │  - New Tweet   │ │  │   TypewriterHero (Centered Headline)      │  │ │
│ │  - SidebarNav  │ │  │   PipelineStepper (Connected Line)        │  │ │
│ │  - RecentDrafts│ │  │   InspirationGrid (Prompt Tiles)          │  │ │
│ │  - SidebarFoot │ │  │   TweetCard & Iteration Timeline          │  │ │
│ │                │ │  └───────────────────────────────────────────┘  │ │
│ │                │ │  ┌───────────────────────────────────────────┐  │ │
│ │                │ │  │ .bottom-chat-wrapper (Sticky Floating Dock│  │ │
│ │                │ │  │  [  Enter your topic or hook...    ( ↑ ) ]│  │ │
│ │                │ │  └───────────────────────────────────────────┘  │ │
│ └────────────────┘ └─────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Component Library & Specifications

### 5.1 Reusable UI Primitives (`frontend/src/components/common/`)
- **`BrandLogo`**: Standardized Twitter bird SVG icon with an amber AI sparkle badge and responsive brand text.
- **`StatusBadge`**: Multi-state badge supporting `SUCCESS`, `PASS`, `REVISE`, `MAX_ATTEMPTS_REACHED`, `INPUT_BLOCKED`, `OUTPUT_BLOCKED`, and `SELECTED`.
- **`Drawer`**: Sliding panel primitive supporting right/left orientation, custom headers/footers, and background backdrop blur.
- **`Modal`**: Centered dialog primitive with backdrop blur, customizable max-width, and header actions.
- **`HistoryItem`**: Standardized history entry card with relative timestamps, truncated queries, preview snippets, and delete buttons.
- **`GuardrailAlert`**: Interception banner for input/output security guardrail blocks.
- **`MobileTopbar`**: Clean responsive topbar for viewports `< 992px`.

### 5.2 Focused Presentational Components
- **`PromptEditor`**: Floating bottom input pill (`.bottom-chat-container`, `max-width: 820px`) with auto-expanding textarea, instant query clearing upon dispatch, and circular send button (`.apple-btn-circle`).
- **`AmbientLoading`**: Borderless, background-integrated loading canvas with luminous ambient glow orbs, rotating progress status descriptors, and subtle gradient shimmer track.
- **`TweetCard`**: Authentic social post card with markdown support, author metadata, character counter, edit mode, copy-to-clipboard, share to X, and `EngagementButtons`.
- **`Timeline`**: Streamlined vertical connected timeline with indicator dot milestones (pass/revise) and line connectors linking iterative draft attempts.
- **`TimelineReviewDetails`**: Minimalist quality scorecard featuring an open 5-criteria metrics strip (`Relevance`, `Clarity`, `Tone`, `Engagement`, `Adherence`) and unboxed editorial quote memo notes.
- **`SettingsDrawer`**: Inspector settings drawer composing `RubricSlider` controls and reflection / web search toggles.
- **`SystemDetailsModal`**: Architecture overview modal detailing the single-agent writer, reflection reviewer, guardrails, and stateful loop.

---

## 6. Logic Separation & Custom Hooks Architecture

All components follow the **Presenter-Container** pattern, delegating side effects, timers, and state transitions to dedicated custom hooks:

| Custom Hook | Module | Logic Encapsulated |
| :--- | :--- | :--- |
| `useTweetGenerator` | `hooks/useTweetGenerator.ts` | Primary state coordinator managing API invocations, response history, system health monitoring, and settings persistence. |
| `usePromptEditor` | `hooks/usePromptEditor.ts` | Auto-resizing textarea calculation, `Enter` submission, and `Shift+Enter` multi-line handling. |
| `useTweetCard` | `hooks/useTweetCard.ts` | Edit mode toggles, clipboard copy with feedback timer, character counting, and share intent formatting. |
| `useTypewriter` | `hooks/useTypewriter.ts` | Phrase rotation, character typing/deleting intervals, pause durations, and unmount timer cleanup. |
| `useEngagement` | `hooks/useEngagement.ts` | Simulated like count and bookmark toggle states. |
| `useAppModals` | `hooks/useAppModals.ts` | Inspector settings, history archive, system features modal, and responsive mobile sidebar open/close states. |
| `useHistory` | `hooks/useHistory.ts` | LocalStorage persistence, item retrieval, and history management. |
| `useTheme` | `hooks/useTheme.ts` | System preference detection, dark/light theme toggling, and data attribute synchronization. |
| `useEscapeKey` | `hooks/useEscapeKey.ts` | Global keyboard <kbd>Escape</kbd> event listener management with automatic listener cleanup. |

All TypeScript types and interfaces are centralized in [`frontend/src/types/index.ts`](file:///e:/OneDrive/Courses/AI%20Agentic/Practice/AI%20Tweet%20Generator%20Assistant/frontend/src/types/index.ts).

---

## 7. Interactive Feedback & Motion

### 7.1 Transitions & Curves
- **Standard UI Speed**: `$apple-transition-speed: 0.15s ease`.
- **Drawers & Sidebar**: `cubic-bezier(0.4, 0, 0.2, 1)` with `0.25s` duration for fluid open/close motion.
- **Spinning Loading Animation**: `@keyframes spinSmooth` with `0.8s linear infinite`.

### 7.2 Confetti Celebration
- Triggered on generation pass (`canvas-confetti`) using brand palette:
  `['#0066cc', '#34c759', '#af52de', '#ff9500']`.

---

## 8. Accessibility & Ergonomics

- **Keyboard Navigation**: All interactive buttons, switches, and input controls support standard `:focus-visible` outlines.
- **Global Escape Handling**: All modals and drawers dismiss on pressing the <kbd>Escape</kbd> key.
- **Semantic ARIA**: Buttons and dialogs include descriptive `aria-label` tags for screen readers.
- **High-Contrast Ratios**: Body text meets WCAG AA contrast standards across both light (`#212529` on `#ffffff`) and dark (`#f4f4f5` on `#18181b`) themes.
