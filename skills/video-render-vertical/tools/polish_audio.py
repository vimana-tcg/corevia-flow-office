#!/usr/bin/env python3
"""Studio-grade audio polish for finished reels.

For each final mp4:
1. Extract audio → wav
2. Run ffmpeg filter chain (highpass + compressor + de-esser + loudnorm)
3. Swap audio back into mp4 (no video re-encode)

This is a fast post-process — ~30s per reel. Reuses existing video.

Usage:
  python3 polish_audio.py --workdir output/my_video [reel_name ...]
"""
import argparse
import os
import shutil
import subprocess
from pathlib import Path

# ffmpeg resolved from PATH (override with FFMPEG_BIN env)
FF = os.environ.get("FFMPEG_BIN") or shutil.which("ffmpeg") or "ffmpeg"

# Filter chain — applied to the TTS audio track:
# - afftdn        : light spectral denoise (-12dB reduction)
# - highpass f=85 : kill rumble / room hum below 85 Hz
# - acompressor   : even out loud/quiet — threshold -20dB, ratio 3:1
# - equalizer 4500Hz -3dB : gentle de-esser (sibilance reduction)
# - loudnorm      : broadcast target for short-form social (-16 LUFS, TP -1.5)
FILTER = (
    "afftdn=nr=12:nf=-25,"
    "highpass=f=85,"
    "acompressor=threshold=-20dB:ratio=3:attack=8:release=80:knee=2:makeup=2,"
    "equalizer=f=4500:t=q:w=2:g=-3,"
    "loudnorm=I=-16:LRA=11:TP=-1.5"
)


def polish(name: str, final_dir: Path, polished_dir: Path):
    src = final_dir / f"{name}.mp4"
    if not src.exists():
        print(f"[{name}] skip — no source"); return
    out = polished_dir / f"{name}.mp4"
    print(f"[{name}] polishing audio...", flush=True)
    # One-pass: video stream-copied, audio re-filtered
    cmd = [
        FF, "-y", "-i", str(src),
        "-c:v", "copy",
        "-af", FILTER,
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-map", "0:v:0", "-map", "0:a:0",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[{name}] FAIL\n{r.stderr[-1500:]}")
        return
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"[{name}] OK → {out.name} ({size_mb:.1f} MB)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reels", nargs="*", help="reel names (default: all in final/)")
    ap.add_argument("--workdir", required=True,
                    help="project working dir (contains final/)")
    args = ap.parse_args()

    work = Path(args.workdir).expanduser()
    final_dir = work / "final"
    polished_dir = work / "final_polished"
    polished_dir.mkdir(parents=True, exist_ok=True)

    targets = args.reels or [p.stem for p in final_dir.glob("*.mp4")]
    for t in targets:
        polish(t, final_dir, polished_dir)
    print("polish done.")


if __name__ == "__main__":
    main()
