import os
import zipfile
import shutil
import pandas as pd
from mutagen.mp3 import MP3
from mutagen.mp3 import HeaderNotFoundError

def get_mp3_duration_safe(file_path):
    try:
        audio = MP3(file_path)
        return audio.info.length
    except (HeaderNotFoundError, Exception) as e:
        print(f"Could not read MP3: {file_path}, error: {e}")
        return None

def parse_osu_file(osu_path):
    metadata = {}
    uninherited_count = 0
    audio_filename = None
    with open(osu_path, 'r', encoding='utf-8') as f:
        section = None
        for line in f:
            line = line.strip()
            if line.startswith('['):
                section = line.strip()
                continue

            if section == "[General]" and line.startswith("AudioFilename:"):
                audio_filename = line.split(":", 1)[1].strip()

            elif section == "[Metadata]" and ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

            elif section == "[TimingPoints]":
                parts = line.split(',')
                if len(parts) > 6 and parts[6].isdigit():
                    if int(parts[6]) == 1:
                        uninherited_count += 1

    return {
        "title": metadata.get("Title", "Unknown"),
        "artist": metadata.get("Artist", "Unknown"),
        "creator": metadata.get("Creator", "Unknown"),
        "tags": metadata.get("Tags", ""),
        "audio_filename": audio_filename,
        "num_uninherited_points": uninherited_count
    }

def process_osz_file(osz_path, temp_dir):
    song_name = os.path.splitext(os.path.basename(osz_path))[0]
    extract_path = os.path.join(temp_dir, song_name)
    os.makedirs(extract_path, exist_ok=True)

    try:
        with zipfile.ZipFile(osz_path, 'r') as zipf:
            zipf.extractall(extract_path)

        osu_files = [f for f in os.listdir(extract_path) if f.endswith(".osu")]
        if not osu_files:
            print(f"No .osu files found in {osz_path}")
            return None

        osu_path = os.path.join(extract_path, osu_files[0])
        meta = parse_osu_file(osu_path)

        audio_filename = meta["audio_filename"]
        if audio_filename:
            mp3_path = os.path.join(extract_path, audio_filename)
            if os.path.isfile(mp3_path):
                duration = get_mp3_duration_safe(mp3_path)
            else:
                print(f"MP3 file not found: {audio_filename} in {song_name}")
                duration = None
        else:
            duration = None

        return {
            "title": meta["title"],
            "artist": meta["artist"],
            "creator": meta["creator"],
            "tags": meta["tags"],
            "num_uninherited_points": meta["num_uninherited_points"],
            "mp3_duration_seconds": duration,
            "song_name": song_name
        }

    except Exception as e:
        print(f"Error processing {osz_path}: {e}")
        return None
    finally:
        shutil.rmtree(extract_path, ignore_errors=True)

def process_osz_folder(folder_path):
    temp_dir = os.path.join(folder_path, "temp_extract")
    os.makedirs(temp_dir, exist_ok=True)

    records = []
    for file in os.listdir(folder_path):
        if file.endswith(".osz"):
            full_path = os.path.join(folder_path, file)
            data = process_osz_file(full_path, temp_dir)
            if data:
                records.append(data)

    shutil.rmtree(temp_dir, ignore_errors=True)

    df = pd.DataFrame(records)
    if not df.empty:
        df["variation_rating_uninherited"] = (df["num_uninherited_points"] - 1) / df["mp3_duration_seconds"]
        df.to_csv(os.path.join(folder_path, "single_timing_song_info.csv"), index=False)
        print("Saved .csv")
    else:
        print("No valid data processed.")

# Run it
if __name__ == "__main__":
    process_osz_folder("./osz_folder")  # Replace with your folder
