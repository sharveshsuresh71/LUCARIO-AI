/**
 * LUCARIO Chat Widget - Entry Point
 * Exports the main web component
 */

import { OnyxChatWidget } from "./widget";

// Define the custom element
if (
  typeof customElements !== "undefined" &&
  !customElements.get("lucario-chat-widget")
) {
  customElements.define("lucario-chat-widget", OnyxChatWidget);
}

// Export for use in other modules
export { OnyxChatWidget };
export * from "./types/api-types";
export * from "./types/widget-types";
