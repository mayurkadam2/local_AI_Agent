# Local AI Agent (Ollama Interface)

A modular local AI interface connecting a Python FastAPI backend to locally running Ollama models (e.g., `qwen3.5:4b`, `llama3`), with a modular HTML/CSS/JS frontend supporting real-time streaming, animated loading indicator, and user interrupts.

---

## 📁 Project Architecture

```
local_AI_Agent/
├── backend/
│   ├── __init__.py
│   ├── config.py                 # Configuration settings (Ollama URL, ports, timeouts, CORS)
│   ├── ollama_client.py          # Core connection manager & async REST client for Ollama
│   ├── main.py                   # FastAPI app entry point, CORS middleware & static file mounting
│   ├── agent/
│   │   ├── __init__.py
│   │   └── sample_agent.py       # Sample AI Agent template with reasoning & tool support
│   └── routes/
│       ├── __init__.py
│       ├── health.py             # Health check & Ollama connection ping (/api/health)
│       ├── models.py             # List installed local Ollama models (/api/models)
│       ├── chat.py               # Synchronous & streaming chat endpoints (/api/chat)
│       └── agent_routes.py       # Sample agent execution endpoint (/api/agent/run)
├── frontend/                     # Modular frontend
│   ├── index.html                # Entry UI with status badge, model selector & input panel
│   ├── css/
│   │   ├── variables.css         # Design tokens & color system
│   │   ├── layout.css            # Responsive layout & chat structure
│   │   └── components.css        # Buttons, inputs, messages, tilted loader & stop button
│   └── js/
│       ├── config.js             # API base URL & endpoints configuration
│       ├── api.js                # Modular fetch API calls & stream reader
│       ├── chat.js               # Message DOM rendering, stream appender & status helpers
│       └── main.js               # App bootstrap, abort controller & event bindings
├── run_backend.py                # Server launcher script
└── requirements.txt              # Python dependencies
```

---

## ⚡ Features

1. **Local Ollama Integration**: Automatically connects to `http://127.0.0.1:11434` and loads available local models.
2. **Real-time Streaming**: Tokens stream to the chat window in real-time via NDJSON streaming.
3. **Animated Loader**: A thin indicator attached to the top of the input bar featuring a continuous, slightly tilted parallelogram animation (`skewX(-25deg)`) active during generation.
4. **Interruptible Generation (Stop Button)**: While the model generates tokens, the **Send** button transforms into a **Stop** button that cancels network transmission and halts generation immediately via `AbortController`.

---

## 🚀 Quick Start

### 1. Ensure Ollama is Running
```bash
ollama serve
```

### 2. Start the Backend API & Frontend Server
```bash
cd local_AI_Agent
python run_backend.py
```

- **App & UI**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
