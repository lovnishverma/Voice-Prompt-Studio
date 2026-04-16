# 🎙️ Voice → Prompt Studio

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini%20AI-1.5%20Flash-orange)
![Sarvam AI](https://img.shields.io/badge/Sarvam%20AI-Speech_to_Text-green)

Voice → Prompt Studio is an intelligent, high-performance web application designed to transform raw, unstructured voice notes into highly engineered, production-ready AI prompts. 

Built with a Flask backend and a lightweight, vanilla HTML/JS/CSS frontend, the system leverages **Sarvam AI** for highly accurate Indic and English speech-to-text, and **Google Gemini** for advanced, persona-driven prompt engineering.

---

<img width="746" height="955" alt="image" src="https://github.com/user-attachments/assets/1647384b-8cf7-4441-a94b-df3c51e4a9c5" />

---

## 📑 Table of Contents

1. [Key Features](#-key-features)
2. [System Architecture](#-system-architecture)
3. [Prerequisites](#-prerequisites)
4. [Installation & Setup](#-installation--setup)
5. [Environment Variables](#-environment-variables)
6. [Usage Guide](#-usage-guide)
7. [API Endpoints](#-api-endpoints)
8. [Troubleshooting](#-troubleshooting)
9. [Future Roadmap](#-future-roadmap)

---

## ✨ Key Features

* **Real-time Audio Processing:** Record audio directly from the browser with a responsive, Web Audio API-driven visualizer.
* **Intelligent Auto-Chunking:** Bypasses standard 30-second API limits by utilizing `pydub` and `FFmpeg` to securely chunk large audio files in ephemeral memory, processing them sequentially, and stitching the transcripts back together.
* **Dynamic Model Routing:** The backend dynamically polls the Gemini API to detect the most powerful, available model assigned to your API key, automatically falling back to stable releases (e.g., `gemini-1.5-flash`) to guarantee uptime and maximize daily quotas (up to 1,500 requests/day).
* **Multi-Tone Prompt Engineering:** Transform a simple 30-word transcript into a comprehensive Software Requirements Specification (SRS), a concise summary, or a creative angle using predefined prompt-engineering pipelines.
* **Bulletproof Rate Limiting:** Frontend algorithms intercept Google API 429 and Quota Exceeded errors to trigger physical UI cooldown locks, preventing sliding-window API penalties.
* **Multi-Lingual Support:** Native support for English (India) and major regional Indic languages (Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, Gujarati).

---

## 🏗 System Architecture

The application is built on a robust, synchronous micro-architecture designed for local or containerized deployment:

1. **Frontend (Client):** Captures microphone data via `MediaRecorder API` or handles file uploads. Displays real-time frequency data via `AudioContext`.
2. **Gateway (Flask):** Intercepts `.webm` or `.mp3` blobs. Employs `tempfile` for secure, ephemeral disk storage to prevent path traversal and memory leaks.
3. **Audio Processor (`pydub`):** Inspects audio length. If `> 29s`, it slices the audio into safe chunks using system-level `FFmpeg` binaries.
4. **ASR Service (Sarvam API):** Transcribes audio chunks synchronously.
5. **LLM Service (Google Gemini):** A highly constrained System Prompt enforces specific outputs (e.g., Markdown schemas) based on user-selected tones.

---

## 🛠 Prerequisites

Before installing, ensure your system meets the following requirements:

* **Python 3.8+**
* **FFmpeg** (Crucial for audio chunking > 30 seconds)

### Installing FFmpeg

**Windows:**
1. Download the pre-compiled binary from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip).
2. Extract and rename the folder to `ffmpeg`. Move it to `C:\ffmpeg`.
3. Add `C:\ffmpeg\bin` to your System `PATH` Environment Variables.
4. *Restart your terminal or IDE.*

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update && sudo apt install ffmpeg
```

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/voice-prompt-studio.git](https://github.com/yourusername/voice-prompt-studio.git)
   cd voice-prompt-studio
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install flask requests python-dotenv pydub
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   The studio will be available at `http://127.0.0.1:5000`.

---

## 🔐 Environment Variables

Create a `.env` file in the root directory of your project. The application utilizes an environment-first cascade, meaning you no longer need to expose API keys in the frontend UI.

```env
# .env
SARVAM_API_KEY=sk_your_sarvam_api_key_here
GEMINI_API_KEY=AIzaSy_your_gemini_api_key_here
```

---

## 💡 Usage Guide

1. **Record or Upload:** Click the microphone icon to record your idea, or upload a pre-existing audio file (e.g., a meeting recording).
2. **Review Transcript:** The raw text will appear in the editable transcript box. Fix any specific names or severe hallucinated typos before proceeding.
3. **Select Tone:**
   * `clear`: Cleans up grammar and filler words.
   * `detailed`: Expands a basic idea into a comprehensive, multi-section prompt (Best for Software/Project ideation).
   * `concise`: Distills down to essential keywords.
   * `technical`: Adapts the prompt for developers, specifying tech stacks and algorithms.
   * `step-by-step`: Formats the prompt as an implementation guide.
4. **Refine:** Click **Refine with Gemini**. The generated, highly structured prompt will appear below, ready to be copied.

---

## 📡 API Endpoints

### `POST /transcribe`
Accepts `multipart/form-data` containing an audio file.
* **Payload:** `audio` (File Blob), `language` (String, e.g., 'en-IN')
* **Returns:** `{"success": True, "transcript": "..."}`

### `POST /refine`
Accepts a JSON payload to process the raw text through Gemini.
* **Payload:** `{"transcript": "Raw text...", "tone": "technical"}`
* **Returns:** `{"success": True, "prompt": "..."}`

---

## ⚠️ Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **Pydub chunking failed / FFmpeg not found** | Missing system binary. | Install FFmpeg and add it to your system `PATH`. Ensure you restart your IDE/Terminal afterward. |
| **Audio duration exceeds 30 seconds** | Fallback triggered because `pydub`/`ffmpeg` failed to load. | See above. Ensure `pip install pydub` was successful. |
| **API quota reached / Locked button** | Gemini API rate limit hit. | Wait for the UI cooldown timer. If you receive a "Daily Limit" error, ensure `app.py` is pointing to `gemini-1.5-flash`, not a preview model. |
| **No models found** | Invalid Gemini API Key or missing permissions. | Verify your `GEMINI_API_KEY` in the `.env` file. |

---

## 🗺 Future Roadmap

* **Direct Gemini Audio Ingestion:** Refactor architecture to bypass Sarvam entirely, natively passing audio files directly to the Gemini 1.5 Flash multimodal endpoint (supports up to 9.5 hours of audio without chunking).
* **Local Persistence:** Implement a lightweight SQLite database to persist prompt history across server restarts.
* **Custom Directives:** Add an input field allowing users to pass custom, on-the-fly prompt engineering rules alongside predefined tones.
* **Markdown Export:** One-click generation of `.md` files from the refined output.

---
*Developed by Lovnish Verma.*
