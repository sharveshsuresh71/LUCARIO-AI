/**
 * @lucario-ai/shared — platform-agnostic code shared between LUCARIO web and mobile.
 *
 * Design tokens are NOT re-exported here: they are generated build artifacts,
 * consumed via the dedicated subpaths "@lucario-ai/shared/tokens.css" (web/Opal CSS
 * variables), "@lucario-ai/shared/nativewind-theme" (mobile Tailwind theme fragment),
 * and "@lucario-ai/shared/native" (mobile light/dark vars() maps).
 */
export * from "./contracts";
export * from "./types";
export * from "./utils";
