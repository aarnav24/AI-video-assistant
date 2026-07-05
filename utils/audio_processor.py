import sys
try:
    import audioop
except ImportError:
    try:
        import audioop_lts as audioop
        sys.modules['audioop'] = audioop
        sys.modules['pyaudioop'] = audioop
    except ImportError:
        pass

import yt_dlp
from pydub import AudioSegment
import os


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,

        # Better compatibility with YouTube
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        },

        # Use different YouTube clients
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },

        # Retry failed downloads
        "retries": 5,
        "fragment_retries": 5,

        # Useful while debugging
        "quiet": False,
        "no_warnings": False,

        # Convert audio to WAV
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)

            base, _ = os.path.splitext(filename)
            wav_file = base + ".wav"

            return wav_file

    except Exception as e:
        raise Exception(f"YouTube download failed: {str(e)}")

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format and compatible for whisper using pydub"""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) # Mono audio, 16 kHz sample rate (good for Whisper)
    audio.export(output_path, format="wav")
    
    return output_path

def chunk_audio(wav_path: str, chunk_minutes: int = 7) -> list:
    filename = os.path.splitext(wav_path)[0]
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 
    chunks = []
    
    for i, start in enumerate(range(0, len(audio), chunk_ms)): 
        chunk = audio[start: start + chunk_ms]
        chunk_path = f"{filename}_chunk_{i+1}.wav"
        chunk.export(chunk_path, format = "wav")
        
        chunks.append(chunk_path)
        
    return chunks

def process_input(source: str) -> list:
    if source.startswith(("http://", "https://")):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
        print("Converting to 16kHz mono...")
        converted = convert_to_wav(wav_path)  # ← always convert YouTube audio too
        os.remove(wav_path)
        wav_path = converted
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready - {len(chunks)} chunk(s) created.")

    if os.path.exists(wav_path):
        os.remove(wav_path)
    return chunks

"""def is_playlist_url(url: str) -> bool:
    return "list=" in url and "watch?v=" not in url

# In Streamlit
if is_playlist_url(url):
    st.warning("Please provide a single video URL, not a playlist link.")"""