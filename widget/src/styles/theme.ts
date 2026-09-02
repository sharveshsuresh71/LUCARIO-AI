import { css } from "lit";
import { colors } from "./colors";

/**
 * LUCARIO Design System - Theme
 * Typography, spacing, and layout tokens from Figma
 */
export const theme = css`
  ${colors}

  :host {
    /* Typography - Hanken Grotesk */
    --lucario-font-family:
      "Hanken Grotesk", -apple-system, BlinkMacSystemFont, "Segoe UI",
      sans-serif;
    --lucario-font-family-mono: "DM Mono", "Monaco", "Menlo", monospace;

    /* Font Sizes */
    --lucario-font-size-small: 10px;
    --lucario-font-size-secondary: 12px;
    --lucario-font-size-sm: 13px;
    --lucario-font-size-main: 14px;
    --lucario-font-size-label: 16px;

    /* Line Heights */
    --lucario-line-height-small: 12px;
    --lucario-line-height-secondary: 16px;
    --lucario-line-height-main: 20px;
    --lucario-line-height-label: 24px;
    --lucario-line-height-section: 28px;
    --lucario-line-height-headline: 36px;

    /* Font Weights */
    --lucario-weight-regular: 400;
    --lucario-weight-medium: 500;
    --lucario-weight-semibold: 600;

    /* Content Heights */
    --lucario-height-content-secondary: 12px;
    --lucario-height-content-main: 16px;
    --lucario-height-content-label: 18px;
    --lucario-height-content-section: 24px;

    /* Border Radius - from Figma */
    --lucario-radius-04: 4px;
    --lucario-radius-08: 8px;
    --lucario-radius-12: 12px;
    --lucario-radius-16: 16px;
    --lucario-radius-round: 1000px;

    /* Spacing - Block */
    --lucario-space-block-1x: 4px;
    --lucario-space-block-2x: 8px;
    --lucario-space-block-3x: 12px;
    --lucario-space-block-4x: 16px;
    --lucario-space-block-6x: 24px;

    /* Spacing - Inline */
    --lucario-space-inline-0: 0px;
    --lucario-space-inline-0_5x: 2px;
    --lucario-space-inline-1x: 4px;

    /* Legacy spacing aliases (for compatibility) */
    --lucario-space-2xs: var(--lucario-space-block-1x);
    --lucario-space-xs: var(--lucario-space-block-2x);
    --lucario-space-sm: var(--lucario-space-block-3x);
    --lucario-space-md: var(--lucario-space-block-4x);
    --lucario-space-lg: var(--lucario-space-block-6x);

    /* Padding */
    --lucario-padding-icon-0: 0px;
    --lucario-padding-icon-0_5x: 2px;
    --lucario-padding-text-0_5x: 2px;
    --lucario-padding-text-1x: 4px;

    /* Icon Weights (stroke-width) */
    --lucario-icon-weight-secondary: 1px;
    --lucario-icon-weight-main: 1.5px;
    --lucario-icon-weight-section: 2px;

    /* Z-index */
    --lucario-z-launcher: 9999;
    --lucario-z-widget: 10000;

    /* Transitions */
    --lucario-transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --lucario-transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  * {
    box-sizing: border-box;
  }
`;
