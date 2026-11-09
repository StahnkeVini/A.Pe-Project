# A.T.L.A.S. — Agent for Technology, Logic, Automation, and Systems

**A.T.L.A.S.** is a hybrid, low-latency, cost-optimized OS Agent designed to control local system processes, inspect screen states via computer vision, and execute voice commands under strict API token constraints.

## 🧠 Core Engineering Highlights

1. **3-Tier Semantic & Deterministic Router (`router.py`)**
   - **Tier 0 (Deterministic Local Execution - 0 Tokens):** Intercepts direct OS, media, and hardware telemetry commands locally in `< 50ms`, bypassing cloud LLMs and reducing API token consumption by up to 70%.
   - **Tier 1 (Lightweight Agentic AFC - `gemini-3.5-flash-lite`):** Handles multi-step tool calling and conversational memory using Google GenAI Automatic Function Calling (AFC).
   - **Tier 2 (Multimodal Computer Vision - `gemini-2.5-flash`):** Captures real-time screen states on demand for code debugging and visual analysis.

2. **Zero-Copy In-Memory Audio Pipeline (`voice_engine.py`)**
   - **Offline STT (`faster-whisper` INT8 on CPU):** Streams raw `float32` PCM microphone buffers directly from RAM into the Whisper tensor engine without disk I/O overhead.
   - **Neural TTS (`edge-tts`):** High-naturalness neural speech synthesis for real-time feedback.

## 📂 System Architecture

```text
A.T.L.A.S./
├── main.py            # Main event loop uniting STT, Router, and TTS
├── router.py          # 3-Tier routing engine with real-time latency/token telemetry
├── pc_tools.py        # OS control functions, hardware diagnostics, and screen capture
├── voice_engine.py    # Push-to-Talk in-memory Whisper STT + Neural TTS
└── requirements.txt   # Project dependencies


🚀 Setup & Execution
1. Clone the repository and create a virtual environment:

PowerShell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt


2.  Create a .env file in the root directory

Code snippet
GEMINI_API_KEY="your_api_key_here"

3.  Run the agent:

PowerShell
python main.py