#!/usr/bin/env python3
"""Montage pipeline — assembles vertical 9:16 reels from a cut plan.

For each reel:
1. Reads its TTS mp3 (or generates silent placeholder if TTS missing)
2. Cuts source video segments per cut plan
3. Adjusts speed of each segment so total = TTS duration (or freeze/live mode)
4. Stacks segments to 9:16 (blur background + centered original)
5. Burns drawtext subtitles (line-by-line, ~3-5 words per chunk)
6. Outputs final mp4

Cut plan is loaded from <workdir>/scripts/cut_plan.json (see SKILL.md). Each reel
entry is either phrase-sync (list of [video_id, timestamp, mode]) or a legacy list
of [video_id, start_sec, end_sec, subtitle_text] segments.

Usage:
  python3 montage.py --workdir output/my_video <reel_name>
  python3 montage.py --workdir output/my_video all
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ffmpeg/ffprobe resolved from PATH (override with FFMPEG_BIN / FFPROBE_BIN env)
FF = os.environ.get("FFMPEG_BIN") or shutil.which("ffmpeg") or "ffmpeg"
FP = os.environ.get("FFPROBE_BIN") or shutil.which("ffprobe") or "ffprobe"

# Bundled font — ships with this skill, works for Cyrillic.
SKILL_DIR = Path(__file__).resolve().parent.parent
FONT = str(SKILL_DIR / "assets" / "fonts" / "Montserrat.ttf")
SUB_COLOR = "#F9A825"  # gold


def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print("CMD:", " ".join(cmd))
        print("STDOUT:", r.stdout[-1000:])
        print("STDERR:", r.stderr[-2000:])
        raise RuntimeError("ffmpeg failed")
    return r


def probe_duration(path: Path) -> float:
    r = run([FP, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)])
    return float(r.stdout.strip())


def make_silent_audio(out_path: Path, seconds: float):
    """Generate silent placeholder mp3 of given duration."""
    run([FF, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", f"{seconds:.3f}", "-q:a", "9", "-acodec", "libmp3lame", str(out_path)])


def _wrap_lines(text: str, max_chars: int) -> list:
    """Greedy word-wrap into list of lines, each ≤ max_chars."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        candidate = (cur + " " + w).strip()
        if len(candidate) <= max_chars or not cur:
            cur = candidate
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _layout_subs(text: str) -> tuple:
    """Pick fontsize + lines layout that fits within 1080px width.
    Returns (lines, fontsize). Max 3 lines."""
    text = text.strip().rstrip(".,!?:;")
    for fontsize, max_chars in [(76, 24), (68, 28), (60, 32), (54, 36)]:
        lines = _wrap_lines(text, max_chars)
        if len(lines) <= 3:
            return lines, fontsize
    return _wrap_lines(text, 40), 50


def make_segment(src_video: Path, start: float, end: float, target_dur: float,
                 out_path: Path, sub_text: str, mode: str = "speed"):
    """Cut from src, scale to 9:16 (blur bg + centered), draw subtitle, adjust to target_dur.
    mode: 'speed' (speed adjust to fit), 'freeze' (single frame held), 'live' (1x speed clip [start:start+target_dur])."""
    if mode == "live":
        # 1x speed real clip — no speedup, no freeze. Use [start:start+target_dur].
        speed = 1.0
        end = start + target_dur
    elif mode == "freeze":
        speed = 1.0
    else:
        # Legacy speed mode
        src_dur = end - start
        speed = src_dur / target_dur

    # Auto-wrap: respect explicit '|' if user set it; otherwise word-wrap by width.
    if "|" in sub_text:
        lines = [s.strip() for s in sub_text.split("|") if s.strip()]
        fontsize = 64 if max(len(l) for l in lines) > 22 else 68
    else:
        lines, fontsize = _layout_subs(sub_text)

    def esc(s):
        return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    lines = [esc(l) for l in lines]

    # Position N lines centered around y=1320 (safe above social UI).
    line_h = fontsize + 10
    n = len(lines)
    total_h = n * line_h
    top_y = 1320 - total_h // 2

    drawtext_chain = []
    for i, line in enumerate(lines):
        y = top_y + i * line_h
        drawtext_chain.append(
            f"drawtext=fontfile='{FONT}':text='{line}':"
            f"fontcolor={SUB_COLOR}:fontsize={fontsize}:x=(w-text_w)/2:y={y}:"
            f"borderw=6:bordercolor=black"
        )
    drawtext_str = ",".join(drawtext_chain)

    if mode == "freeze":
        # Two-step freeze: 1) extract single PNG frame, 2) loop PNG for target_dur.
        png_path = out_path.with_suffix(".png")
        run([FF, "-y", "-ss", str(start), "-i", str(src_video),
             "-frames:v", "1", "-q:v", "2", str(png_path)])
        vf = (
            f"[0:v]split=2[base][bg];"
            f"[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"boxblur=luma_radius=40:luma_power=2,eq=brightness=-0.2[blurred];"
            f"[base]scale=1080:-2[fg];"
            f"[blurred][fg]overlay=(W-w)/2:(H-h)/2[bgfg];"
            f"[bgfg]{drawtext_str}[v]"
        )
        run([FF, "-y", "-loop", "1", "-framerate", "30", "-i", str(png_path),
             "-filter_complex", vf,
             "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium",
             "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
             "-t", f"{target_dur:.3f}", str(out_path)])
        png_path.unlink(missing_ok=True)
    else:
        # speed or live: trim a real clip
        vf = (
            f"[0:v]trim=start={start}:end={end},setpts=(PTS-STARTPTS)/{speed},"
            f"split=2[base][bg];"
            f"[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"boxblur=luma_radius=40:luma_power=2,eq=brightness=-0.2[blurred];"
            f"[base]scale=1080:-2[fg];"
            f"[blurred][fg]overlay=(W-w)/2:(H-h)/2[bgfg];"
            f"[bgfg]{drawtext_str}[v]"
        )
        run([FF, "-y", "-i", str(src_video), "-filter_complex", vf,
             "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium",
             "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
             "-t", f"{target_dur:.3f}", str(out_path)])


def _split_sub(text: str) -> str:
    """Pass-through — actual layout decided by _layout_subs in make_segment."""
    return text.strip().rstrip(".,!?:;")


def load_cut_plan(work: Path) -> dict:
    """Load the per-reel cut plan from <workdir>/scripts/cut_plan.json."""
    plan_path = work / "scripts" / "cut_plan.json"
    if not plan_path.exists():
        raise SystemExit(f"No cut plan at {plan_path} — see SKILL.md for the schema.")
    return json.loads(plan_path.read_text(encoding="utf-8"))


def build_reel(reel_id: str, reels: dict, work: Path, lang: str):
    src_dir = work / "source"
    tts_dir = work / "tts"
    out_dir = work / "final"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = work / "renders"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    spec = reels[reel_id]
    tts_mp3 = tts_dir / f"{reel_id}.mp3"

    work_dir = tmp_dir / reel_id
    work_dir.mkdir(parents=True, exist_ok=True)
    parts = []

    silent = False
    target = 0.0
    if spec.get("phrase_sync") and tts_mp3.exists():
        # Phrase-sync mode: 1 visual clip per Whisper segment, subtitle = verbatim phrase.
        tx_json = work / "transcripts" / "tts" / f"{reel_id}.json"
        tx = json.loads(tx_json.read_text())
        whisper_segs = tx["segments"]
        # If Whisper segments are too long (speaks without pauses), word-group instead.
        if any((s["end"] - s["start"]) > 4.5 for s in whisper_segs):
            words = tx.get("words", [])
            if words:
                grouped = []
                cur_words = []
                cur_start = words[0]["start"]
                MAX_CHUNK_DUR = 2.2
                MAX_CHUNK_WORDS = 5
                for w in words:
                    if cur_words and (
                        w["start"] - cur_start > MAX_CHUNK_DUR
                        or len(cur_words) >= MAX_CHUNK_WORDS
                    ):
                        grouped.append({
                            "start": cur_start,
                            "end": cur_words[-1]["end"],
                            "text": " ".join(cw["word"] for cw in cur_words),
                        })
                        cur_words = [w]
                        cur_start = w["start"]
                    else:
                        cur_words.append(w)
                if cur_words:
                    grouped.append({
                        "start": cur_start,
                        "end": cur_words[-1]["end"],
                        "text": " ".join(cw["word"] for cw in cur_words),
                    })
                whisper_segs = grouped
                print(f"  [word-grouped {len(grouped)} chunks from {len(words)} words]", flush=True)
        visuals = spec["visuals"]
        n_w = len(whisper_segs)
        n_v = len(visuals)
        if n_v < n_w:
            visuals = list(visuals) + [visuals[-1]] * (n_w - n_v)
        target = probe_duration(tts_mp3)
        print(f"[{reel_id}] phrase-sync: target={target:.2f}s, {n_w} phrases", flush=True)
        for i, wseg in enumerate(whisper_segs):
            v = visuals[i]
            # Support both old format (vid, start, end) and new (vid, t, mode)
            if len(v) == 3 and isinstance(v[2], str):
                vid, t, mode = v
                vstart, vend = t, t + 5  # vend dummy for live; freeze ignores end
            else:
                vid, vstart, vend = v
                mode = "speed"
            # Sync FIX: each segment lasts until the NEXT phrase begins (includes pause).
            seg_start = wseg["start"]
            seg_end_in_audio = whisper_segs[i + 1]["start"] if i + 1 < n_w else target
            phrase_dur = seg_end_in_audio - seg_start
            sub_text = _split_sub(wseg["text"])
            part = work_dir / f"seg_{i:02d}.mp4"
            if not part.exists():
                make_segment(src_dir / f"{vid}.mov", vstart, vend, phrase_dur, part, sub_text, mode=mode)
            parts.append(part)
            print(f"  ph{i}: {phrase_dur:.2f}s [{mode}] {vid}@{vstart} sub={wseg['text'].strip()!r}", flush=True)
    else:
        # Legacy equal-segment mode
        silent = not (tts_mp3.exists() and tts_mp3.stat().st_size > 1000)
        if silent:
            target = sum(end - start for _, start, end, _ in spec["segments"])
        else:
            target = probe_duration(tts_mp3)
        n = len(spec["segments"])
        per = target / n
        print(f"[{reel_id}] target={target:.2f}s, {n} segments, per≈{per:.2f}s, silent={silent}", flush=True)
        for i, (vid, start, end, sub) in enumerate(spec["segments"]):
            part = work_dir / f"seg_{i:02d}.mp4"
            if not part.exists():
                make_segment(src_dir / f"{vid}.mov", start, end, per, part, sub)
            parts.append(part)
            print(f"  seg{i}: {vid}[{start}-{end}] -> {part.name}", flush=True)

    # Concat list
    concat_txt = work_dir / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{p}'" for p in parts))
    silent_video = work_dir / "silent_video.mp4"
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
         "-c", "copy", str(silent_video)])

    # Now overlay audio
    out_mp4 = out_dir / f"{reel_id}.mp4"
    if silent:
        sil = work_dir / "silent.mp3"
        make_silent_audio(sil, target)
        audio_in = sil
    else:
        audio_in = tts_mp3

    run([FF, "-y", "-i", str(silent_video), "-i", str(audio_in),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(out_mp4)])

    print(f"[{reel_id}] DONE → {out_mp4}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reels", nargs="*", default=["all"],
                    help="reel ids from cut_plan.json, or 'all'")
    ap.add_argument("--workdir", required=True,
                    help="project working dir (contains source/, tts/, scripts/cut_plan.json)")
    ap.add_argument("--lang", default="ru", help="subtitle/caption language hint")
    args = ap.parse_args()

    work = Path(args.workdir).expanduser()
    reels = load_cut_plan(work)

    targets = list(reels.keys()) if "all" in args.reels else args.reels
    for t in targets:
        if t not in reels:
            print(f"unknown reel: {t}; available: {', '.join(reels)}")
            continue
        build_reel(t, reels, work, args.lang)


if __name__ == "__main__":
    main()
