#!/usr/bin/env python3
"""
Test script for the Innovate Trix API playlist feature.
Define inputs at the beginning and run to see the generated playlist.
"""

import asyncio
import httpx
from typing import Literal

# ==================== CONFIGURATION ====================
# Define your test inputs here
MOOD: Literal[
    "Reflective", "Calm", "Focused", "Energized", "Unwind",
    "Relax", "Chill", "Recharge", "Romantic"
] = "Romantic"

TIME_OF_DAY: Literal["Morning", "Afternoon", "Evening", "Night"] = "Night"

ENERGY_LEVEL: int = 20  # Must be between 0 and 100

# API endpoint configuration
API_BASE_URL = "http://localhost:8000"  # Change if your server runs on a different port
PLAYLIST_ENDPOINT = f"{API_BASE_URL}/playlist"
# =======================================================


async def test_playlist_generation():
    """Test the playlist generation endpoint with configured inputs."""
    payload = {
        "mood": MOOD,
        "time_of_day": TIME_OF_DAY,
        "energy": ENERGY_LEVEL,
    }

    print("=" * 60)
    print("Testing Playlist Generation")
    print("=" * 60)
    print(f"Mood: {MOOD}")
    print(f"Time of Day: {TIME_OF_DAY}")
    print(f"Energy Level: {ENERGY_LEVEL}/100")
    print("-" * 60)
    print("Requesting playlist from API...")
    print()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(PLAYLIST_ENDPOINT, json=payload)

        if response.status_code == 200:
            playlist = response.json()
            print("✅ SUCCESS! Generated Playlist:")
            print("-" * 60)
            for idx, song in enumerate(playlist, start=1):
                print(f"{idx:2}. {song}")
            print("-" * 60)
            print(f"Total songs: {len(playlist)}")
        else:
            print(f"❌ FAILED with status code: {response.status_code}")
            print(f"Error details: {response.text}")

    except httpx.ConnectError:
        print("❌ FAILED: Could not connect to the API.")
        print(f"Make sure the server is running at {API_BASE_URL}")
        print("Start the server with: uvicorn main:app --reload")
    except httpx.TimeoutException:
        print("❌ FAILED: Request timed out.")
    except Exception as e:
        print(f"❌ FAILED with unexpected error: {e}")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_playlist_generation())
