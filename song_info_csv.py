import os
import zipfile
import pandas as pd
from mutagen.mp3 import MP3
from mutagen.mp3 import HeaderNotFoundError

def get_mp3_duration_safe(file_path):
    """Get MP3 duration in seconds, handling errors."""
    try:
        audio = MP3(file_path)
        return audio.info.length  # Duration in seconds
    except HeaderNotFoundError:
        print(f"Skipping {file_path}: HeaderNotFoundError")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return None

def parse_osu_metadata(osu_file, root_folder):
    """Extract metadata and timing points from an .osu file, including referenced MP3 path."""
    metadata = {}
    timing_points = []
    uninherited_count = 0
    audio_filename = None

    with open(osu_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        reading_metadata = False
        reading_timing_points = False
        reading_general = False

        for line in lines:
            if line == "[General]":
                reading_general = True
                continue
            if line == "[Metadata]":
                reading_general = False
                reading_metadata = True
                continue
            if line == "[TimingPoints]":
                reading_metadata = False
                reading_timing_points = True
                continue
            if line.startswith("["):
                reading_general = False
                reading_metadata = False
                reading_timing_points = False

            if reading_general and line.startswith("AudioFilename:"):
                audio_filename = line.split(":", 1)[1].strip()

            if reading_metadata and ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

            if reading_timing_points:
                parts = line.split(',')
                if len(parts) > 6:
                    uninherited = int(parts[6])
                    if uninherited == 1:
                        uninherited_count += 1
                timing_points.append(parts)

    audio_path = os.path.join(root_folder, audio_filename) if audio_filename else None

    return {
        "title": metadata.get("Title", "Unknown"),
        "artist": metadata.get("Artist", "Unknown"),
        "creator": metadata.get("Creator", "Unknown"),
        "tags": metadata.get("Tags", ""),
        "num_timing_points": len(timing_points),
        "num_uninherited_points": uninherited_count,
        "audio_path": audio_path,
    }

def process_osz_file(osz_file, extract_root):
    """Extract metadata and MP3 duration from an .osz file."""
    osz_filename = os.path.basename(osz_file).replace(".osz", "")
    song_folder = os.path.join(extract_root, osz_filename)
    os.makedirs(song_folder, exist_ok=True)

    metadata = {}
    try:
        with zipfile.ZipFile(osz_file, 'r') as zip_ref:
            zip_ref.extractall(song_folder)

        # Pick first .osu file found to extract metadata
        osu_files = [f for f in os.listdir(song_folder) if f.endswith(".osu")]
        if not osu_files:
            return None

        osu_file_path = os.path.join(song_folder, osu_files[0])
        metadata = parse_osu_metadata(osu_file_path, song_folder)

        if metadata["audio_path"] and os.path.isfile(metadata["audio_path"]):
            metadata["mp3_duration_seconds"] = get_mp3_duration_safe(metadata["audio_path"])
        else:
            metadata["mp3_duration_seconds"] = None

        metadata["song_name"] = osz_filename

    except zipfile.BadZipFile:
        print(f"Invalid ZIP file: {osz_file}")

    return metadata

def process_osz_folder(folder_path):
    """Process all .osz files in the folder and compile metadata."""
    extract_folder = os.path.join(folder_path, "extracted")
    os.makedirs(extract_folder, exist_ok=True)

    data = []
    for file in os.listdir(folder_path):
        if file.endswith(".osz"):
            osz_file = os.path.join(folder_path, file)
            metadata = process_osz_file(osz_file, extract_folder)
            if metadata:
                data.append(metadata)

    df = pd.DataFrame(data)
    df["variation_rating_uninherited"] = (df["num_uninherited_points"] - 1) / df["mp3_duration_seconds"]
    df.to_csv(os.path.join(folder_path, "non_continuous_timing.csv"), index=False)

    print("Metadata extraction complete. Saved to non_continuous_timing.csv.")

# Example usage
if __name__ == "__main__":
    osu_folder_path = "./osz_folder"  # Replace with your folder path
    process_osz_folder(osu_folder_path)
