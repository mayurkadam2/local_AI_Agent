// Modular Frontend Configuration
export const CONFIG = {
  API_BASE_URL: window.location.origin.includes(":8000") 
    ? "" 
    : "http://127.0.0.1:8000",
  ENDPOINTS: {
    HEALTH: "/api/health",
    MODELS: "/api/models",
    CHAT: "/api/chat",
    CHAT_STREAM: "/api/chat/stream",
  }
};
