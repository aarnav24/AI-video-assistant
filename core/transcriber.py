import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_chunk(chunk_path: str, language: str = "en") -> str:
    with open(chunk_path, "rb") as f:
        
        if language == "hi":
            return client.audio.translations.create(
                file=f,
                model="whisper-large-v3",
                response_format="text",
                temperature=0,
            ).strip()

        return client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3",
            response_format="text",
            temperature=0,
            language="en",
        ).strip()

def transcribe_all(chunks: list, language: str = "en") -> str : 
    full_transcript = ""
    
    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i+1}")
        full_transcript += transcribe_chunk(chunk, language) + " "
        os.remove(chunk)
    
    print("Transcription completed!")
    
    return full_transcript.strip()