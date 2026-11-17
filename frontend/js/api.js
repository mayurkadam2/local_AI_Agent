// Modular API Layer for Backend Communication
import { CONFIG } from './config.js';

export async function checkConnection() {
  const url = `${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.HEALTH}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }
  return await response.json();
}

export async function fetchInstalledModels() {
  const url = `${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.MODELS}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }
  return await response.json();
}

/**
 * Stream chat tokens from backend with support for cancellation via AbortSignal.
 */
export async function streamChatMessage(messages, model, signal, onToken) {
  const url = `${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.CHAT_STREAM}`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, model }),
    signal
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Chat request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        const parsed = JSON.parse(trimmed);
        if (parsed.error) {
          throw new Error(parsed.error);
        }
        const token = parsed.message?.content || "";
        if (token) {
          onToken(token);
        }
      } catch (e) {
        if (e.name === "AbortError") throw e;
        // Non-JSON line or partial chunk, continue
      }
    }
  }

  if (buffer.trim()) {
    try {
      const parsed = JSON.parse(buffer.trim());
      const token = parsed.message?.content || "";
      if (token) onToken(token);
    } catch (_) {}
  }
}
