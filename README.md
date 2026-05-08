# innovate-trix-back

Simple FastAPI backend.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
uvicorn main:app --reload
```

## Environment

This app uses the free Hugging Face Inference API for playlist generation.

```powershell
$env:HF_API_KEY = "your_huggingface_token"
```

## Playlist API

**POST** `/playlist`

Request body:

```json
{
  "mood": "Calm",
  "time_of_day": "Evening",
  "energy": 65
}
```

Allowed `mood` values:
`Reflective`, `Calm`, `Focused`, `Energized`, `Unwind`, `Relax`, `Chill`, `Recharge`, `Romantic`

Allowed `time_of_day` values:
`Morning`, `Afternoon`, `Evening`, `Night`

`energy` range: `0` to `100`

Response:

```json
[
  "Song Name 1",
  "Song Name 2",
  "Song Name 3"
]
```

The response always returns exactly 20 song names when successful.
