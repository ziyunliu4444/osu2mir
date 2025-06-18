import os
import zipfile
import tempfile
import shutil
import json

def extract_uninherited_timing_points(osu_lines):
    timing_points = []
    reading = False
    for line in osu_lines:
        line = line.strip()
        if line == "[TimingPoints]":
            reading = True
            continue
        if reading:
            if line.startswith("["):
                break
            parts = line.split(",")
            if len(parts) >= 7:
                try:
                    time = float(parts[0])
                    beat_length = float(parts[1])
                    meter = int(parts[2])
                    uninherited = int(parts[6]) == 1
                    if uninherited:
                        timing_points.append({
                            "time": time,
                            "beat_length": beat_length,
                            "meter": meter
                        })
                except ValueError:
                    continue
    return timing_points

def get_audio_filename(osu_lines):
    in_general = False
    for line in osu_lines:
        line = line.strip()
        if line == '[General]':
            in_general = True
            continue
        if in_general:
            if line.startswith('['):
                break
            if line.startswith('AudioFilename:'):
                return line.split(':', 1)[1].strip()
    return None

def process_osz(osz_path, audio_output_dir, json_output_dir):
    song_name = os.path.splitext(os.path.basename(osz_path))[0]

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(osz_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        osu_files = [f for f in os.listdir(tmpdir) if f.endswith(".osu")]
        if not osu_files:
            print(f"❌ No .osu file in {song_name}")
            return

        osu_path = os.path.join(tmpdir, osu_files[0])
        with open(osu_path, 'r', encoding='utf-8') as f:
            osu_lines = f.readlines()

        audio_filename = get_audio_filename(osu_lines)
        if not audio_filename:
            print(f"❌ Audio filename not found in {song_name}")
            return

        audio_path = os.path.join(tmpdir, audio_filename)
        if not os.path.isfile(audio_path):
            print(f"❌ MP3 file '{audio_filename}' missing in {song_name}")
            return

        # Copy audio
        os.makedirs(audio_output_dir, exist_ok=True)
        audio_dest = os.path.join(audio_output_dir, f"{song_name}.mp3")
        shutil.copy(audio_path, audio_dest)

        # Extract and save uninherited timing points to JSON
        uninherited_points = extract_uninherited_timing_points(osu_lines)
        os.makedirs(json_output_dir, exist_ok=True)
        with open(os.path.join(json_output_dir, f"{song_name}_uninherited.json"), 'w') as f:
            json.dump(uninherited_points, f, indent=2)

        print(f"✅ Processed {song_name}")

def process_all_osz_in_folder(folder_path):
    audio_dir = os.path.join(folder_path, "extracted_audio")
    json_dir = os.path.join(folder_path, "uninherited_timing_json")

    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    for file in os.listdir(folder_path):
        if file.endswith('.osz'):
            try:
                process_osz(os.path.join(folder_path, file), audio_dir, json_dir)
            except Exception as e:
                print(f"⚠️ Error processing {file}: {e}")

# === MAIN ===
if __name__ == "__main__":
    input_folder = "./test_osz_folder"  # Replace with your actual folder path
    process_all_osz_in_folder(input_folder)
