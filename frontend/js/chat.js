// Modular Chat UI Helper

export function appendMessage(container, role, text) {
  const msgEl = document.createElement("div");
  msgEl.className = `message message-${role}`;

  const metaEl = document.createElement("span");
  metaEl.className = "message-meta";
  metaEl.textContent = role === "user" ? "You" : "Assistant (Local Ollama)";

  const contentEl = document.createElement("div");
  contentEl.className = "message-content";
  contentEl.textContent = text;

  msgEl.appendChild(metaEl);
  msgEl.appendChild(contentEl);
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
  return msgEl;
}

/**
 * Creates an empty assistant message element ready for streaming tokens.
 */
export function createStreamingMessage(container) {
  const msgEl = document.createElement("div");
  msgEl.className = "message message-assistant";

  const metaEl = document.createElement("span");
  metaEl.className = "message-meta";
  metaEl.textContent = "Assistant (Local Ollama)";

  const contentEl = document.createElement("div");
  contentEl.className = "message-content";

  msgEl.appendChild(metaEl);
  msgEl.appendChild(contentEl);
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;

  let currentContent = "";

  return {
    appendToken(token) {
      currentContent += token;
      contentEl.textContent = currentContent;
      container.scrollTop = container.scrollHeight;
    },
    markInterrupted() {
      const tag = document.createElement("div");
      tag.className = "interrupted-tag";
      tag.textContent = "⏹ [Generation stopped by user]";
      msgEl.appendChild(tag);
      container.scrollTop = container.scrollHeight;
    },
    getContent() {
      return currentContent;
    },
    isEmpty() {
      return currentContent.trim().length === 0;
    },
    remove() {
      msgEl.remove();
    }
  };
}

export function updateConnectionBadge(badgeEl, isConnected, version = "") {
  const dot = badgeEl.querySelector(".status-dot");
  const text = badgeEl.querySelector(".status-text");

  if (isConnected) {
    dot.className = "status-dot status-online";
    text.textContent = version ? `Ollama v${version} Connected` : "Ollama Connected";
  } else {
    dot.className = "status-dot status-offline";
    text.textContent = "Ollama Disconnected";
  }
}
