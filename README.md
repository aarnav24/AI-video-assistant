# 🎬 AI Meeting & Video Intelligence Assistant

An end-to-end AI-powered tool that transcribes audio from YouTube videos or local files, summarizes the content, extracts action items and key decisions, and lets you chat with the transcript using a RAG pipeline.

---

## 🚀 Features

- **Audio Ingestion** — Supports YouTube URLs and local audio/video files (MP3, MP4, WAV, M4A, and more)
- **Transcription** — Fast, accurate transcription via Groq's Whisper large-v3 API
- **Hindi / Hinglish Support** — Automatically translates Hindi and Hinglish audio to English
- **AI Summarization** — Generates concise bullet-point summaries using Mistral AI via LangChain LCEL
- **Smart Extraction** — Automatically extracts action items, key decisions, and open questions
- **RAG Chat** — Chat with your transcript using ChromaDB vector store + FastEmbed embeddings
- **Export** — Download transcript as TXT
- **Clean UI** — Dark-themed Streamlit interface with live pipeline status

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Transcription | Groq Whisper large-v3 |
| LLM | Mistral AI (`open-mistral-nemo`) via LangChain LCEL |
| Embeddings | FastEmbed (`BAAI/bge-small-en-v1.5`) |
| Vector Store | ChromaDB |
| Audio Processing | yt-dlp, pydub, FFmpeg |
| Language | Python 3.10+ |

---

## 📁 Project Structure

```
video_assistant/
├── app.py                  # Streamlit UI
├── main.py                 # CLI entry point
├── pyproject.toml          # Project metadata & dependencies
├── uv.lock                 # Locked dependency versions
├── requirements.txt
├── .env                    # API keys (not committed)
├── core/
│   ├── transcriber.py      # Groq Whisper transcription
│   ├── summarize.py        # LangChain summarization pipeline
│   ├── extractor.py        # Action items, decisions, questions
│   ├── vector_store.py     # ChromaDB vector store builder
│   └── rag_engine.py       # RAG chain for Q&A
└── utils/
    └── audio_processor.py  # Audio download, conversion, chunking
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/video_assistant.git
cd video_assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** FFmpeg must be installed separately.
> - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
> - Linux/Mac: `sudo apt install ffmpeg` or `brew install ffmpeg`

### 3. Set up environment variables
Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key
MISTRAL_API_KEY=your_mistral_api_key
```

Get your free API keys:
- Groq: [console.groq.com](https://console.groq.com)
- Mistral: [console.mistral.ai](https://console.mistral.ai)

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🔄 Pipeline

```
YouTube URL / Local File
        ↓
  Audio Download & Conversion (yt-dlp + pydub)
        ↓
  Chunking (5-min chunks)
        ↓
  Transcription (Groq Whisper large-v3)
        ↓
  Translation if Hindi/Hinglish (Whisper translate task)
        ↓
  Summarization (Mistral + LangChain LCEL map-reduce)
        ↓
  Extraction — Action Items · Decisions · Questions
        ↓
  Vector Store (ChromaDB + FastEmbed)
        ↓
  RAG Chat (Mistral + ChromaDB retriever)
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key for Whisper transcription |
| `MISTRAL_API_KEY` | Mistral API key for summarization and RAG |

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).