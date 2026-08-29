---
name: GyanSetu Knowledge System
colors:
  surface: '#faf9f6'
  surface-dim: '#dbdad7'
  surface-bright: '#faf9f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f1'
  surface-container: '#efeeeb'
  surface-container-high: '#e9e8e5'
  surface-container-highest: '#e3e2e0'
  on-surface: '#1a1c1a'
  on-surface-variant: '#41493e'
  inverse-surface: '#2f312f'
  inverse-on-surface: '#f2f1ee'
  outline: '#717a6d'
  outline-variant: '#c0c9bb'
  surface-tint: '#2a6b2c'
  primary: '#00450d'
  on-primary: '#ffffff'
  primary-container: '#1b5e20'
  on-primary-container: '#90d689'
  inverse-primary: '#91d78a'
  secondary: '#835500'
  on-secondary: '#ffffff'
  secondary-container: '#feae2c'
  on-secondary-container: '#6b4500'
  tertiary: '#6b1d3d'
  on-tertiary: '#ffffff'
  tertiary-container: '#883454'
  on-tertiary-container: '#ffaec6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#acf4a4'
  primary-fixed-dim: '#91d78a'
  on-primary-fixed: '#002203'
  on-primary-fixed-variant: '#0c5216'
  secondary-fixed: '#ffddb4'
  secondary-fixed-dim: '#ffb955'
  on-secondary-fixed: '#291800'
  on-secondary-fixed-variant: '#633f00'
  tertiary-fixed: '#ffd9e2'
  tertiary-fixed-dim: '#ffb1c8'
  on-tertiary-fixed: '#3e001d'
  on-tertiary-fixed-variant: '#7a2949'
  background: '#faf9f6'
  on-background: '#1a1c1a'
  surface-variant: '#e3e2e0'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  title-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-numeric:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  sidebar-width: 240px
  max-content-width: 1440px
  container-padding: 24px
  gutter: 20px
  stack-gap: 16px
---

## Brand & Style

The design system is engineered for **GyanSetu**, an offline-first AI knowledge platform. The brand personality is authoritative, resilient, and highly functional. It prioritizes clarity and information density without sacrificing the user's cognitive load.

The visual style is **Corporate Modern with Tactile Clarity**. It utilizes a structured layout, a grounded color palette, and subtle depth to create an environment that feels like a reliable tool for high-stakes knowledge management. The interface avoids ephemeral trends, focusing instead on longevity, accessibility, and high-contrast legibility.

**Key Principles:**
- **Information Integrity:** Layouts must expand to fit content; text truncation is strictly prohibited to ensure full data visibility.
- **Functional Aesthetics:** Visual elements like gradients or icons must serve a functional purpose or denote hierarchy, never acting as mere decoration.
- **Resilience:** The UI must feel robust, reflecting the platform's offline-first capability through solid blocks of color and clear state indicators.

## Colors

The palette is anchored by **Deep Green**, evoking growth and stability, and **Off-white**, providing a soft, paper-like canvas that reduces eye strain during long research sessions.

- **Primary (#1B5E20):** Reserved for active navigation states, branding elements, and meaningful headers.
- **Accent (#F5A623):** Used exclusively for primary Call-to-Action (CTA) buttons to create a high-contrast focal point against the green and white core.
- **Background (#FAF9F6):** Applied to the global page background to distinguish the "stage" from the "content."
- **Surface (#FFFFFF):** Used for cards, modals, and the sidebar to create a clean, elevated feel.
- **Status Colors:** Success and Error states use solid, high-saturation fills (Green/Red) for badges to ensure immediate recognition of system health.

## Typography

The design system utilizes **Inter** exclusively for its exceptional legibility and systematic neutral tone. 

- **Data Representation:** Numeric data (e.g., storage capacity, sync percentages) must always use `label-numeric` (16px+) to ensure importance.
- **Content Hierarchy:** Body text never drops below 14px.
- **Zero Truncation Policy:** Containers must use flex-wrap or dynamic height settings. If a title is long, the container grows vertically.
- **Readability:** High contrast is maintained by using deep grey (#1A1A1A) for primary text and medium grey (#5F6368) for secondary labels.

## Layout & Spacing

The layout is built on a **Rigid Fixed-Fluid Hybrid** model to maintain a professional, dashboard-centric feel.

- **Sidebar:** A fixed 240px width sidebar persists across all screens. It houses the primary navigation and critical system health stats (Offline Status, Storage).
- **Main Canvas:** A centered content area with a maximum width of 1440px. 
- **Padding:** A minimum of 24px padding is required for all primary containers to ensure "breathability" in data-heavy environments.
- **Grid:** A 12-column grid is used for desktop layouts, with 20px gutters. 
- **Responsiveness:** On smaller screens, the sidebar collapses into a drawer, but numeric data and headers remain consistent in scale.

## Elevation & Depth

This design system uses **Tonal Layering** combined with **Soft Ambient Shadows** to define hierarchy.

- **Level 0 (Background):** #FAF9F6. The base layer for the entire application.
- **Level 1 (Cards/Sidebar):** #FFFFFF. Elevated with a subtle, highly-diffused shadow (0px 4px 12px rgba(0,0,0,0.05)). This provides a clear distinction between the canvas and interactive content.
- **Level 2 (Modals/Popovers):** #FFFFFF. These use a more pronounced shadow (0px 8px 24px rgba(0,0,0,0.1)) to focus user attention.
- **Outlines:** Subtle 1px borders (#E0E0E0) are used on input fields and secondary cards to provide structure without adding visual noise.

## Shapes

The shape language is defined by a consistent **12px radius** for all primary containers, providing a modern but structured appearance.

- **Cards & Sections:** 12px (`rounded-lg` equivalent).
- **Buttons & Inputs:** 8px to maintain a slightly sharper, more "tool-like" feel for interactive elements.
- **Badges:** Fully rounded (pill-shaped) to distinguish them from interactive buttons.
- **Selection States:** Active sidebar items use a 0px left-border accent but an overall rounded background treatment.

## Components

### Buttons & CTAs
- **Primary CTA:** Solid Amber (#F5A623) with white text. Reserved for the most important action on a page.
- **Secondary Action:** Ghost or Outlined styles using the Deep Green (#1B5E20).
- **Navigation Items:** Clear hover states using a light tint of Green (#E8F5E9) and a solid Green indicator for active states.

### Cards
- White background, 12px rounded corners, 24px internal padding. 
- Card headers should include a Lucide-style line icon to provide visual context for the data presented.

### Badges (Status Indicators)
- **Success:** Solid #2E7D32 background with white text.
- **Failed:** Solid #C62828 background with white text.
- **Syncing/Pending:** Solid #F5A623 background with white text.

### Input Fields
- 1px border (#E0E0E0), 8px radius. Active state uses a 2px Deep Green border. 
- Labels always sit above the input; never use placeholder text as the primary label.

### Icons
- Use **Lucide** or similar minimalist line icons (2px stroke width).
- Icons are always paired with text to ensure clarity. 
- Never use "icon-only" buttons unless the icon is universally understood (e.g., a "Close" X).

### Dashboard Widgets
- **Storage/Data Gauges:** Use clean, linear progress bars in Deep Green. Numeric values must be displayed prominently at 16px+.