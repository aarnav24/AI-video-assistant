import streamlit as st
import time
import os
from dotenv import load_dotenv
from utils.audio_processor import process_input, convert_to_wav, chunk_audio
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.vector_store import build_vector_store
from core.rag_engine import load_rag_chain, ask_question

load_dotenv()

st.set_page_config(
    page_title="AI Meeting & Video Intelligence Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface-2: #1a1a25;
    --border: #2a2a3a;
    --accent: #7c3aed;
    --accent-glow: #9f67ff;
    --accent-2: #06b6d4;
    --text: #e8e8f0;
    --text-muted: #7070a0;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(124, 58, 237, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-glow) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.card:hover { border-color: var(--accent); }
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}
.card-content {
    font-size: 0.875rem;
    line-height: 1.7;
    color: var(--text);
}

.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.badge-purple { background: rgba(124,58,237,0.2); color: var(--accent-glow); border: 1px solid rgba(124,58,237,0.3); }
.badge-cyan   { background: rgba(6,182,212,0.15);  color: var(--accent-2);    border: 1px solid rgba(6,182,212,0.3); }
.badge-green  { background: rgba(16,185,129,0.15); color: var(--success);     border: 1px solid rgba(16,185,129,0.3); }

.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), #5b21b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
}

.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface-2);
    border-radius: 8px;
    margin: 0.4rem 0;
    border: 1px solid var(--border);
    font-size: 0.8rem;
    transition: border-color 0.3s;
}
.status-bar.active { border-color: var(--accent); }
.status-bar.done   { border-color: var(--success); }

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-active  { background: var(--accent-glow); box-shadow: 0 0 8px var(--accent-glow); animation: pulse 1.5s infinite; }
.dot-done    { background: var(--success); }
.dot-pending { background: var(--border); }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

.spin-gear { display: inline-block; animation: spin 2s linear infinite; }
@keyframes spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

.pipeline-banner {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.85rem 1.25rem;
    background: rgba(124,58,237,0.1);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 10px;
    font-size: 0.85rem;
    color: var(--accent-glow);
    font-family: 'JetBrains Mono', monospace;
}

.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
}
.chat-msg {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}
.chat-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.chat-bubble {
    display: inline-block;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 90%;
}
.user-label  { color: var(--accent-glow); }
.bot-label   { color: var(--accent-2); }
.user-bubble { background: rgba(124,58,237,0.15); border: 1px solid rgba(124,58,237,0.25); align-self: flex-end; }
.bot-bubble  { background: rgba(6,182,212,0.1);   border: 1px solid rgba(6,182,212,0.2);  align-self: flex-start; }

hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 300px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

.stProgress > div > div > div { background: var(--accent) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── Session State ───────────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "pipeline_done": False,
    "pipeline_started": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

STEPS = [
    ("audio",       "🔊", "Audio Processing"),
    ("transcript",  "📝", "Transcription"),
    ("title",       "🏷️",  "Title Generation"),
    ("summary",     "📋", "Summarisation"),
    ("extract",     "🔍", "Extraction"),
    ("vectorstore", "🗄️",  "Building Vector Store"),
    ("rag",         "🧠", "Running RAG Engine"),
]

# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.6rem">🎬 AI<br>Video</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Meeting Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<span class="badge badge-purple">Input</span>', unsafe_allow_html=True)

    input_type = st.radio("Source", ["YouTube URL", "Upload File"], horizontal=True)
    language   = st.selectbox("Language", ["english", "hinglish"], index=0)

    source          = None
    uploaded_file   = None

    if input_type == "YouTube URL":
        url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        if url.strip():
            source = url.strip()
    else:
        uploaded_file = st.file_uploader(
            "Upload Audio/Video",
            type=["mp3", "mp4", "wav", "m4a", "ogg", "flac", "webm", "mkv"],
            help="Max file size: 500MB"
        )
        st.caption("Supports MP3, MP4, WAV, M4A, OGG, FLAC, WEBM, MKV")

    run_btn = st.button("⚡  Analyse", use_container_width=True)

    if st.session_state.pipeline_started:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">Pipeline Status</span>', unsafe_allow_html=True)

    step_placeholders = {key: st.empty() for key, _, _ in STEPS}

    def render_step(key, icon, label, state):
        if state == "active":
            dot_cls, bar_cls = "dot-active", "active"
        elif state == "done":
            dot_cls, bar_cls = "dot-done", "done"
        else:
            dot_cls, bar_cls = "dot-pending", ""
        step_placeholders[key].markdown(f"""
        <div class="status-bar {bar_cls}">
            <div class="status-dot {dot_cls}"></div>
            <span>{icon} {label}</span>
        </div>""", unsafe_allow_html=True)

    def mark(key, state):
        st.session_state[f"step_{key}"] = state
        for k, icon, label in STEPS:
            render_step(k, icon, label, st.session_state.get(f"step_{k}", "pending"))

    if st.session_state.pipeline_started:
        for key, icon, label in STEPS:
            render_step(key, icon, label, st.session_state.get(f"step_{key}", "pending"))

# ─── Main Area ───────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Meeting & Video Intelligence Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Transcribe · Summarise · Chat with your meetings</div>', unsafe_allow_html=True)
st.markdown("---")

# ── Run Pipeline ─────────────────────────────────────────────────────────────────
if run_btn:
    # ── Validate input ──
    if input_type == "YouTube URL" and not source:
        st.error("Please enter a YouTube URL.")
        st.stop()
    elif input_type == "Upload File" and uploaded_file is None:
        st.error("Please upload an audio or video file.")
        st.stop()

    st.session_state.result           = None
    st.session_state.chat_history     = []
    st.session_state.pipeline_done    = False
    st.session_state.pipeline_started = True

    for key, _, _ in STEPS:
        st.session_state[f"step_{key}"] = "pending"

    progress_placeholder = st.empty()
    progress_placeholder.markdown("""
    <div class="pipeline-banner">
        <span class="spin-gear">⚙️</span>
        <span>Pipeline running… check sidebar for live status</span>
    </div>""", unsafe_allow_html=True)

    try:
        mark("audio", "active")

        if input_type == "Upload File":
            # Save uploaded file to downloads/ then process
            os.makedirs("downloads", exist_ok=True)
            file_path = os.path.join("downloads", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            chunks = chunk_audio(convert_to_wav(file_path))
        else:
            # YouTube URL — show friendly error if blocked
            try:
                chunks = process_input(source)
            except Exception as e:
                if "403" in str(e) or "Forbidden" in str(e):
                    progress_placeholder.error(
                        "❌ YouTube download is unavailable on the hosted version due to server restrictions. "
                        "Please upload an audio/video file directly."
                    )
                    st.stop()
                raise e

        mark("audio", "done")

        mark("transcript", "active")
        source_type = "youtube" if input_type == "YouTube URL" else "meeting"
        transcript  = transcribe_all(chunks, "en" if language == "english" else "hi")
        mark("transcript", "done")

        mark("title", "active")
        title = generate_title(transcript, source_type=source_type)
        mark("title", "done")

        mark("summary", "active")
        summary_text = summarize(transcript, source_type=source_type)
        mark("summary", "done")

        mark("extract", "active")
        action_items = extract_action_items(summary_text)
        decisions    = extract_key_decisions(summary_text)
        questions    = extract_questions(summary_text)
        mark("extract", "done")

        mark("vectorstore", "active")
        build_vector_store(transcript)
        mark("vectorstore", "done")

        mark("rag", "active")
        rag_chain = load_rag_chain()
        mark("rag", "done")

        st.session_state.result = {
            "title":          title,
            "transcript":     transcript,
            "summary":        summary_text,
            "action_items":   action_items,
            "key_decisions":  decisions,
            "open_questions": questions,
            "rag_chain":      rag_chain,
        }
        st.session_state.pipeline_done = True
        progress_placeholder.success("✅ Analysis complete!")
        time.sleep(0.8)
        progress_placeholder.empty()
        st.rerun()

    except Exception as e:
        for key, _, _ in STEPS:
            if st.session_state.get(f"step_{key}") == "active":
                st.session_state[f"step_{key}"] = "pending"
                mark(key, "pending")
        progress_placeholder.error(f"❌ Error: {e}")

# ── Results ───────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    st.markdown(f"""
    <div class="card">
        <div class="card-title">📌 Session Title</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:var(--text)">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="medium")
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📋 Summary</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)
            st.download_button("⬇️ Download TXT", data=r["transcript"], file_name="transcript.txt", mime="text/plain")

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">✅ Action Items</div>
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🔑 Key Decisions</div>
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">❓ Open Questions</div>
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.2rem;font-weight:700;margin-bottom:1rem">💬 Chat with your Meeting</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">🤖 Assistant</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-muted);font-size:0.85rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:5rem 2rem;text-align:center">
        <div style="font-size:4rem;margin-bottom:1rem">🎬</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:0.5rem">
            Ready to Analyse
        </div>
        <div style="color:var(--text-muted);font-size:0.85rem;max-width:380px;line-height:1.7">
            Upload an audio/video file or paste a YouTube URL in the sidebar, choose your language, and hit <strong>Analyse</strong> to get started.
        </div>
        <div style="margin-top:2rem;display:flex;gap:1rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-purple">Transcription</span>
            <span class="badge badge-cyan">Summarisation</span>
            <span class="badge badge-green">RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)
