import json
import os
import re
from typing import Literal
from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx 
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Innovate Trix API")

# Allow CORS for development; adjust `allow_origins` in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use NVIDIA NIM API for inference
NIM_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NIM_MODEL = "meta/llama-3.1-8b-instruct" # or "mistralai/mixtral-8x7b-instruct-v0.1", "meta/llama-3.1-70b-instruct"
MoodOption = Literal[
    "Reflective",
    "Calm",
    "Focused",
    "Energized",
    "Unwind",
    "Relax",
    "Chill",
    "Recharge",
    "Romantic",
]

TimeOfDayOption = Literal["Morning", "Afternoon", "Evening", "Night"]

class PlaylistRequest(BaseModel):
    mood: MoodOption
    time_of_day: TimeOfDayOption
    energy: int = Field(ge=0, le=100)

def _extract_song_names(text: str) -> list[str]:
    parsed = None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", text)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                parsed = None

    if isinstance(parsed, list):
        songs = [str(item).strip() for item in parsed if str(item).strip()]
        return songs

    songs: list[str] = []
    for raw_line in text.splitlines():
        cleaned = re.sub(r'^\s*(?:[-*]|\d+[.)])\s*', "", raw_line).strip(" \t\"'")
        if cleaned:
            songs.append(cleaned)
    return songs

async def _generate_playlist_with_nim(payload: PlaylistRequest) -> list[str]:
    nim_api_key = os.getenv("NIM_API_KEY")
    if not nim_api_key:
        raise HTTPException(
            status_code=500,
            detail="NIM_API_KEY is not set. Add your NVIDIA NIM API key in your environment.",
        )

    # Construct a prompt for chat completion format
    prompt = (
        f"You are a helpful assistant that creates music playlists. "
        f"Generate a playlist of exactly 20 real song names based on:\n"
        f"- Mood: {payload.mood}\n"
        f"- Time of day: {payload.time_of_day}\n"
        f"- Energy level: {payload.energy}/100\n\n"
        f"Rules:\n"
        f"1. Return a JSON array ONLY. No other text.\n"
        f"2. Exactly 20 items.\n"
        f"3. Song names only (no artist names, no numbering).\n"
        f"4. Avoid duplicates.\n"
        f"5. Format: [\"Song 1\", \"Song 2\", ...]\n"
    )

    request_body = {
        "model": NIM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.8,
        "max_tokens": 600,
        "top_p": 0.9,
        "stream": False,
    }

    headers = {
        "Authorization": f"Bearer {nim_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            response = await client.post(
                NIM_API_URL,
                headers=headers,
                json=request_body,
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"AI provider request failed: {exc}") from exc

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"AI provider error ({response.status_code}): {response.text}",
            )

        data = response.json()

        # Extract content from chat completion response
        if isinstance(data, dict) and "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0].get("message", {}).get("content", "")
        else:
            content = str(data)

        songs = _extract_song_names(content)
        unique_songs = list(dict.fromkeys(song for song in songs if song))

        if len(unique_songs) < 20:
            raise HTTPException(
                status_code=502,
                detail=f"AI provider returned fewer than 20 valid songs ({len(unique_songs)}). Please retry.",
            )

        return unique_songs[:20]

@app.get("/")
def root():
    return {"message": "Innovate Trix API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/playlist", response_model=list[str])
async def create_playlist(payload: PlaylistRequest) -> list[str]:
    return await _generate_playlist_with_nim(payload)

