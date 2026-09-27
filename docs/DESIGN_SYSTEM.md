# AI Tweet Generator — Design System Specification

Welcome to the **Design System** specification for the AI Tweet Generator Assistant. This document captures the visual philosophy, design tokens, typography hierarchies, layout mechanics, component library, and motion guidelines powering the modern **Apple HIG + Developer Minimalist** user interface.

---

## 📑 Table of Contents
1. [Design Philosophy & Aesthetic](#1-design-philosophy--aesthetic)
2. [Design Tokens & Color Palette](#2-design-tokens--color-palette)
3. [Typography Hierarchy](#3-typography-hierarchy)
4. [Layout & Grid Architecture](#4-layout--grid-architecture)
5. [Component Library & Specifications](#5-component-library--specifications)
6. [Interactive Feedback & Motion](#6-interactive-feedback--motion)
7. [Accessibility & Ergonomics](#7-accessibility--ergonomics)

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
│ │  - Brand Logo  │ │  │                                           │  │ │
│ │  - New Tweet   │ │  │   TypewriterHero (Centered Headline)      │  │ │
│ │  - Navigation  │ │  │   Agent Pipeline Stepper (Connected Line) │  │ │
│ │  - History     │ │  │   Inspiration Prompt Tiles                │  │ │
│ │  - Theme Switch│ │  │   Tweet Showcase & Iteration Timeline    │  │ │
│ │                │ │  └───────────────────────────────────────────┘  │ │
│ │                │ │  ┌───────────────────────────────────────────┐  │ │
│ │                │ │  │ .bottom-chat-wrapper (Sticky Floating Dock│  │ │
│ │                │ │  │  [  Enter your topic or hook...    ( ↑ ) ]│  │ │
│ │                │ │  └───────────────────────────────────────────┘  │ │
│ └────────────────┘ └─────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Master Viewport
- **`app-layout`**: Full viewport flex wrapper (`height: 100vh; width: 100vw; overflow: hidden;`).
- **`app-sidebar`**: 
  - **Expanded**: Width `260px`, full navigation labels, history list, and theme toggler.
  - **Compressed**: Width `68px`, vertically centered icons, stacked logo and toggle button.
  - **Mobile**: Fixed drawer (`z-index: 1060`) with smooth sliding transformation.
- **`app-main`**: Viewport container with multi-layer background (Grid + Ambient Glow).
- **`app-scrollable-content`**: Scrollable inner view with bottom padding (`padding-bottom: 7rem`) preventing overlap with the floating prompt dock.

---

## 5. Component Library & Specifications

### 5.1 Chatbot Bottom Dock (`PromptEditor`)
- **Structure**: Sticky bottom container with a soft vertical gradient mask.
- **Input Pill (`.bottom-chat-container`)**:
  - `max-width: 820px`, `border-radius: 26px`, `min-height: 52px`.
  - Border: `1.5px solid var(--apple-border)`.
  - Focus Ring: `border-color: var(--apple-accent); box-shadow: 0 0 0 3px var(--apple-accent-subtle);`.
- **Send Button (`.apple-btn-circle`)**:
  - `36px × 36px` fully circular button with high-contrast arrow icon.
  - Hover physics: `transform: scale(1.04)`.

### 5.2 Agent Pipeline Stepper (`HowItWorksCard`)
- **Track Line (`.stepper-line`)**: Continuous connecting gradient line spanning stages (`opacity: 0.55`).
- **Step Node (`.stepper-node`)**:
  - `48px × 48px` circular surface elevated with `box-shadow: 0 4px 12px rgba(0,0,0,0.05)`.
  - Hover physics: `transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.09);`.
- **Numbered Badge (`.stepper-badge-num`)**:
  - `19px × 19px` circular pill positioned at top-right of the node with bold stage number.
- **3 Stages**:
  1. **Prompt Input**: Icon `PenLine`, Blue Accent (`--apple-accent`).
  2. **Reflection Loop**: Icon `Repeat`, Orange Accent (`--apple-warning`).
  3. **Verified Output**: Icon `ShieldCheck`, Green Accent (`--apple-success`).

### 5.3 Tweet Showcase (`TweetCard`)
- Authentic social post card featuring:
  - User avatar with Twitter brand icon + AI sparkle.
  - Author name, handle (`@TweetStudioAI`), verified check badge.
  - Monospace character counter (`0 / 280`).
  - Copy to Clipboard button with toast feedback.
  - Quick action toolbar: Regeneration, Settings shortcut, Character limit checks.

### 5.4 Iteration Timeline & Metric Score Radars (`Timeline` & `MetricPill`)
- Visual display of the LangGraph self-correction loop.
- **Verdict Badges**: `.apple-badge-pass` (Green) and `.apple-badge-revise` (Orange).
- **Metric Tiles (`.metric-tile`)**:
  - 5 Rubric Scores: Relevance, Clarity, Professionalism, Engagement, Adherence.
  - Individual score values with color-coded mini progress bars.
- **Actionable Feedback Section**: Detailed evaluator suggestions displayed in clean quote callouts.

### 5.5 Settings & History Drawers (`SettingsDrawer` & `HistorySidebar`)
- Slide-over side sheet with backdrop blur.
- **Apple Switch Toggle (`.apple-switch`)**: Native iOS style slider switch with smooth sliding thumb (`transform: translateX(20px)`).
- **Threshold Sliders**: Custom HTML range inputs with real-time percentage indicators.

### 5.6 System Features & Specs Modal (`SystemDetailsModal`)
- Dialog width: `max-width: 820px`, `border-radius: 20px`.
- Backdrop: `rgba(0, 0, 0, 0.45)` with `backdrop-filter: blur(4px)`.
- 4 Architecture Breakdown Sections (Single-Agent Pattern, Reflection Reviewer, Two-Tier Guardrails, Stateful Loop).
- Real-time Backend Engine Health Status badge (`Online` / `Offline`).

### 5.7 Dynamic Island Toast (`StatusToast`)
- Centered top pill notification (`.dynamic-island`, `z-index: 2000`).
- Floating elevation with `box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15)`.

---

## 6. Interactive Feedback & Motion

### 6.1 Transitions & Curves
- **Standard UI Speed**: `$apple-transition-speed: 0.15s ease`.
- **Drawers & Sidebar**: `cubic-bezier(0.4, 0, 0.2, 1)` with `0.25s` duration for fluid open/close motion.
- **Spinning Loading Animation**: `@keyframes spinSmooth` with `0.8s linear infinite`.

### 6.2 Confetti Celebration
- Triggered on generation pass (`canvas-confetti`) using brand palette:
  `['#0066cc', '#34c759', '#af52de', '#ff9500']`.

---

## 7. Accessibility & Ergonomics

- **Keyboard Navigation**: All interactive buttons, switches, and input controls support standard `:focus-visible` outlines.
- **Semantic ARIA**: Buttons and dialogs include descriptive `aria-label` tags for screen readers.
- **High-Contrast Ratios**: Body text meets WCAG AA contrast standards across both light (`#212529` on `#ffffff`) and dark (`#f4f4f5` on `#18181b`) themes.
