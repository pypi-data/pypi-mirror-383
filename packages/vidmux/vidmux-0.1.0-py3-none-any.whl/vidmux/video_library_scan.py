"""Tools to scan a video library."""

import csv
import json
from pathlib import Path

from vidmux.video_inspection import (
    get_audio_tracks,
    get_format,
    get_subtitles,
    get_video_tracks,
)


def make_track_entries(tracks: list) -> list:
    """Return the track list where each track has index, language, codec and title."""
    return [
        {
            "index": idx,
            "language": track.get("tags", {}).get("language", "unknown"),
            "codec": track.get("codec_name", "unknown"),
            "title": track.get("tags", {}).get("title", ""),
        }
        for idx, track in enumerate(tracks)
    ]


def show_track_entries(
    tracks: list, name: str = "track", output: callable = print
) -> None:
    """Show tracks."""
    for track in tracks:
        idx = track["index"]
        language = track["language"]
        codec = track["codec"]
        title = track["title"]
        output(f"\t{name.capitalize()} {idx+1}: {language=}, {codec=}, {title=}")


def scan_video_library(
    library_path: Path, extensions: list[str] | None = None
) -> list[dict]:
    """Scan all videos in 'library_path' recursively."""
    if extensions is None:
        extensions = [".mp4", ".mkv", ".avi", ".mov"]

    results = []
    for root, _dirs, files in library_path.walk():
        for filename in files:
            file = root / filename
            if file.suffix in extensions:
                print(f"Inspecting '{filename}'...")
                video_tracks = get_video_tracks(file)
                audio_tracks = get_audio_tracks(file)
                subtitles = get_subtitles(file)
                results.append(
                    {
                        "filename": str(file.relative_to(library_path)),
                        "container": get_format(file),
                        "video_tracks": make_track_entries(video_tracks),
                        "audio_tracks": make_track_entries(audio_tracks),
                        "subtitle_tracks": make_track_entries(subtitles),
                    }
                )

    return results


def save_json(results: list[dict], path: Path) -> None:
    """Save results to a JSON file."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    print(f"Saved JSON: {path}")


def save_csv(results: list[dict], path: Path) -> None:
    """Save results to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["filename", "type", "index", "language", "codec", "title"])
        for entry in results:
            for track in entry["audio_tracks"]:
                writer.writerow(
                    [
                        entry["filename"],
                        "audio",
                        track["index"],
                        track["language"],
                        track["codec"],
                        track["title"],
                    ]
                )
            for track in entry["subtitle_tracks"]:
                writer.writerow(
                    [
                        entry["filename"],
                        "subtitle",
                        track["index"],
                        track["language"],
                        track["codec"],
                        track["title"],
                    ]
                )

    print(f"Save CSV: {path}")


def print_to_terminal(results: list[dict]) -> None:
    """Print results to terminal."""
    for entry in results:
        print(entry["filename"])
        show_track_entries(entry["audio_tracks"], name="audio track")
        show_track_entries(entry["subtitle_tracks"], name="subtitle track")


def scan_mode(
    library: Path,
    extensions: list[str],
    show: bool = True,
    json_file: Path | None = None,
    csv_file: Path | None = None,
) -> bool:
    """Run the scan and save/show the output."""
    if not (show or json_file or csv_file):
        print("No output specified. Use --print, --json or --csv.")
        return False

    scan_result = scan_video_library(library, extensions=extensions)

    if show:
        print_to_terminal(scan_result)

    if json_file:
        save_json(scan_result, json_file)

    if csv_file:
        save_csv(scan_result, csv_file)

    return True
