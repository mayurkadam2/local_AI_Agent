// Modular Frontend Application Entry Point
import { checkConnection, fetchInstalledModels, streamChatMessage } from './api.js';
import { appendMessage, createStreamingMessage, updateConnectionBadge } from './chat.js';

document.addEventListener("DOMContentLoaded", async () => {
  const statusBadge = document.getElementById("status-badge");
  const modelSelect = document.getElementById("model-select");
  const messagesContainer = document.getElementById("messages-container");
  const messageInput = document.getElementById("message-input");
  const sendBtn = document.getElementById("send-btn");
  const stopBtn = document.getElementById("stop-btn");
  const progressBar = document.getElementById("progress-bar");

  const conversationHistory = [];
  let currentAbortController = null;

  // 1. Initial Connection & Health Check
  try {
    const health = await checkConnection();
    const isConnected = health.ollama?.connected ?? false;
    const version = health.ollama?.version ?? "";
    updateConnectionBadge(statusBadge, isConnected, version);

    if (isConnected) {
      appendMessage(messagesContainer, "assistant", "Connected to local Ollama API successfully! Type a message to chat.");
    } else {
      appendMessage(messagesContainer, "assistant", "⚠️ Ollama is not running on 127.0.0.1:11434. Run 'ollama serve' in your terminal.");
    }
  } catch (err) {
    updateConnectionBadge(statusBadge, false);
    appendMessage(messagesContainer, "assistant", `Failed to connect to backend: ${err.message}`);
  }

  // 2. Fetch Available Models
  try {
    const modelsData = await fetchInstalledModels();
    modelSelect.innerHTML = "";
    if (modelsData.models && modelsData.models.length > 0) {
      modelsData.models.forEach(m => {
        const opt = document.createElement("option");
        opt.value = m.name;
        opt.textContent = `${m.name} (${m.size_human})`;
        modelSelect.appendChild(opt);
      });
    } else {
      const opt = document.createElement("option");
      opt.textContent = "No models found (e.g. run 'ollama pull qwen3.5:4b')";
      modelSelect.appendChild(opt);
    }
  } catch (err) {
    console.error("Error loading models:", err);
  }

  // UI State toggles
  function setGeneratingState(isGenerating) {
    if (isGenerating) {
      sendBtn.classList.add("hidden");
      stopBtn.classList.remove("hidden");
      progressBar.classList.remove("hidden");
      messageInput.disabled = true;
    } else {
      stopBtn.classList.add("hidden");
      sendBtn.classList.remove("hidden");
      progressBar.classList.add("hidden");
      messageInput.disabled = false;
      messageInput.focus();
      currentAbortController = null;
    }
  }

  // 3. Handle Message Submission & Streaming
  async function handleSend() {
    const text = messageInput.value.trim();
    if (!text) return;

    messageInput.value = "";
    appendMessage(messagesContainer, "user", text);
    conversationHistory.push({ role: "user", content: text });

    // Show tilted parallelogram progress bar and replace Send with Stop button
    setGeneratingState(true);

    const streamMessage = createStreamingMessage(messagesContainer);
    currentAbortController = new AbortController();

    try {
      const selectedModel = modelSelect.value;
      await streamChatMessage(
        conversationHistory,
        selectedModel,
        currentAbortController.signal,
        (token) => {
          streamMessage.appendToken(token);
        }
      );

      const reply = streamMessage.getContent();
      if (reply) {
        conversationHistory.push({ role: "assistant", content: reply });
      }
    } catch (err) {
      if (err.name === "AbortError") {
        // Generation was interrupted by user clicking Stop
        streamMessage.markInterrupted();
        const partialReply = streamMessage.getContent();
        if (partialReply) {
          conversationHistory.push({ role: "assistant", content: partialReply });
        }
      } else {
        if (streamMessage.isEmpty()) {
          streamMessage.remove();
        }
        appendMessage(messagesContainer, "assistant", `Error: ${err.message}`);
      }
    } finally {
      setGeneratingState(false);
    }
  }

  // 4. Handle Stop / Interrupt Button
  stopBtn.addEventListener("click", () => {
    if (currentAbortController) {
      currentAbortController.abort();
    }
  });

  sendBtn.addEventListener("click", handleSend);
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });
});
