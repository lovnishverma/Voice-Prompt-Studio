---
title: Voice Prompt Studio
emoji: 🎙️
colorFrom: green
colorTo: yellow
sdk: docker
pinned: false
license: mit
short_description: Developed by Lovnish Verma.
---

# 🎙️ Voice → Prompt Studio

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini%20AI-1.5%20Flash-orange)
![Sarvam AI](https://img.shields.io/badge/Sarvam%20AI-Speech_to_Text-green)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

**Voice → Prompt Studio** is an intelligent, high-performance web application designed to transform raw, unstructured voice notes into highly engineered, production-ready AI prompts. 

Built with a Flask backend and a lightning-fast vanilla HTML/JS/CSS frontend, the system leverages **Sarvam AI** for highly accurate Indic and English speech-to-text, and **Google Gemini** for advanced, persona-driven prompt engineering. 

**Live Demo:** [lovnishverma-voice-prompt-studio.hf.space](https://lovnishverma-voice-prompt-studio.hf.space/)

---

<div align="center">
  <img width="48%" alt="App Interface Screenshot 1" src="https://github.com/user-attachments/assets/834fb446-8755-4a2a-af24-74fe296d25fe" />
  <img width="48%" alt="App Interface Screenshot 2" src="https://github.com/user-attachments/assets/3766db77-a1cf-469c-8855-c0cdc1867fc2" />
</div>

---

## 📑 Table of Contents
1. [Key Features](#-key-features)
2. [Tech Stack](#-tech-stack)
3. [System Architecture](#-system-architecture)
4. [Prerequisites](#-prerequisites)
5. [Installation & Setup](#-installation--setup)
6. [API Endpoints](#-api-endpoints)
7. [Troubleshooting](#-troubleshooting)
8. [Future Roadmap](#-future-roadmap)

---

## ✨ Key Features

* **Real-time Audio Processing:** Record audio directly from the browser with a responsive, Web Audio API-driven visualizer.
* **Intelligent Auto-Chunking:** Bypasses standard 30-second ASR API limits by utilizing `pydub` and `FFmpeg` to securely chunk large audio files in ephemeral memory, processing them sequentially, and stitching the transcripts back together.
* **Dynamic Model Routing:** The backend dynamically polls the Gemini API to detect the most powerful, available model assigned to your API key, automatically falling back to stable releases (e.g., `gemini-1.5-flash`) to guarantee uptime.
* **Multi-Tone Prompt Engineering:** Transform a simple 30-word transcript into a comprehensive Software Requirements Specification (SRS), a concise summary, or a creative angle using predefined prompt-engineering pipelines.
* **Cloud History Persistence:** Automatically saves and retrieves your recent prompts using a MongoDB Atlas integration, ensuring you never lose a great idea.
* **Bulletproof Rate Limiting:** Frontend algorithms intercept Google API 429 and Quota Exceeded errors to trigger physical UI cooldown locks, preventing sliding-window API penalties.
* **Multi-Lingual Support:** Native support for English (India) and major regional Indic languages (Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, Gujarati).

---

## 💻 Tech Stack

* **Frontend:** Vanilla HTML5, CSS3 (Syne Font), JavaScript (Web Audio API, MediaRecorder API)
* **Backend:** Python 3.9, Flask
* **Database:** MongoDB Atlas (`pymongo`)
* **AI & Machine Learning:** Google Generative AI API (Gemini), Sarvam AI API (Speech-to-Text)
* **Audio Processing:** `pydub`, FFmpeg
* **Deployment:** Docker, Hugging Face Spaces

---

## 🏗 System Architecture

The application is built on a robust, synchronous micro-architecture designed for local or containerized deployment:

1. **Frontend (Client):** Captures microphone data or handles file uploads. Displays real-time frequency data.
2. **Gateway (Flask):** Intercepts `.webm` or `.mp3` blobs. Employs `tempfile` for secure, ephemeral disk storage to prevent path traversal and memory leaks.
3. **Audio Processor:** Inspects audio length. If `> 29s`, it slices the audio into safe chunks using system-level `FFmpeg` binaries.
4. **ASR Service (Sarvam API):** Transcribes audio chunks synchronously.
5. **LLM Service (Google Gemini):** A highly constrained System Prompt enforces specific outputs based on user-selected tones.
6. **Data Layer (MongoDB):** Asynchronously stores the final generated prompt, original transcript, tone, and timestamp.

---

## 🛠 Prerequisites

Before installing, ensure your system meets the following requirements:

* **Python 3.8+**
* **MongoDB Atlas Account** (Free tier cluster is sufficient)
* **FFmpeg** (Crucial for audio chunking > 30 seconds)

**Installing FFmpeg:**
* **Windows:** Download the pre-compiled binary from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip), extract to `C:\ffmpeg`, and add `C:\ffmpeg\bin` to your System `PATH`. *Restart your terminal.*
* **macOS:** `brew install ffmpeg`
* **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install ffmpeg`

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

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory. The application utilizes an environment-first cascade to protect API keys.
   ```env
   GEMINI_API_KEY="your_gemini_api_key_here"
   SARVAM_API_KEY="your_sarvam_api_key_here"
   MONGO_URI="mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```
   The studio will be available at `http://127.0.0.1:5000`.

---

## 📡 API Endpoints

### Processing
* **`POST /transcribe`**: Accepts `multipart/form-data` containing an `audio` file blob and `language` string. Returns the transcribed text.
* **`POST /refine`**: Accepts JSON (`transcript`, `tone`) to process the raw text through Gemini. Returns the engineered prompt.

### Database
* **`GET /api/history`**: Fetches the 10 most recent generated prompts from MongoDB.
* **`POST /api/history`**: Saves a newly generated prompt object to the database.

---

## ⚠️ Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **Pydub chunking failed / FFmpeg not found** | Missing system binary. | Install FFmpeg and add it to your system `PATH`. Restart your IDE/Terminal. |
| **Audio duration exceeds 30 seconds** | Fallback triggered because `pydub`/`ffmpeg` failed to load. | Ensure `pip install pydub` and FFmpeg installations were successful. |
| **API quota reached / Locked button** | Gemini API rate limit hit. | Wait for the UI cooldown timer. Ensure `app.py` is pointing to `gemini-1.5-flash` for higher rate limits. |
| **History not saving** | MongoDB connection failed. | Check your `MONGO_URI` in the `.env` file and ensure your IP address is whitelisted in MongoDB Atlas Network Access. |

---

## 🗺 Future Roadmap

* **Direct Gemini Audio Ingestion:** Refactor architecture to bypass Sarvam entirely, natively passing audio files directly to the Gemini 1.5 Flash multimodal endpoint (supports up to 9.5 hours of audio without chunking).
* **Custom Directives:** Add an input field allowing users to pass custom, on-the-fly prompt engineering rules alongside predefined tones.
* **Markdown Export:** One-click generation of `.md` files from the refined output.
* **User Authentication:** Add login capabilities to separate prompt histories by user account.

---
*Developed by Lovnish Verma.*
