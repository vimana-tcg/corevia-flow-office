#!/usr/bin/env python3
"""Transcribe TTS mp3s to word-level timestamps for montage alignment.

Output JSON has segments[] with .words[].{word,start,end}, used by montage.py to
align both video cuts and live-caption subtitles.

Transcription backend: OpenAI Whisper (whisper-1) via OPENAI_API_KEY. The key is
read from the environment or from a local .env file (never hardcoded, never fetched
from a remote server).

Usage:
  python3 transcribe_tts.py --workdir output/my_video [--lang ru] [reel_name ...]
"""
import argparse
import json
import os
from pathlib import Path


def load_api_key():
    """OPENAI_API_KEY from env, or from a local .env (cwd or ./.env)."""
    if os.environ.get("OPENAI_API_KEY"):
        return
    for env_path in (Path(".env"), Path.cwd() / ".env"):
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return
    raise SystemExit(
        "OPENAI_API_KEY not set. Export it or add it to a local .env file."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reels", nargs="*", help="reel names (default: all mp3s in tts/)")
    ap.add_argument("--workdir", required=True,
                    help="project working dir (contains tts/)")
    ap.add_argument("--lang", default="ru", help="transcription language hint")
    args = ap.parse_args()

    load_api_key()
    from openai import OpenAI
    client = OpenAI()

    work = Path(args.workdir).expanduser()
    tts_dir = work / "tts"
    out_dir = work / "transcripts" / "tts"
    out_dir.mkdir(parents=True, exist_ok=True)

    names = args.reels or [p.stem for p in tts_dir.glob("*.mp3")]
    for name in names:
        src = tts_dir / f"{name}.mp3"
        if not src.exists():
            print(f"skip {name} — no tts")
            continue
        out_json = out_dir / f"{name}.json"
        if out_json.exists() and out_json.stat().st_size > 100:
            print(f"[{name}] cached")
            continue
        print(f"[{name}] transcribing word-level...", flush=True)
        with src.open("rb") as f:
            resp = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
                language=args.lang,
            )
        data = resp.model_dump() if hasattr(resp, "model_dump") else resp.to_dict()
        out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        n_words = len(data.get("words", []))
        n_segs = len(data.get("segments", []))
        print(f"[{name}] OK — {n_words} words, {n_segs} segments", flush=True)

    print("done.")


if __name__ == "__main__":
    main()
