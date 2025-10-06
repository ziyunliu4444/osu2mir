import os
import zipfile
import shutil
import tempfile
from mutagen.mp3 import MP3, HeaderNotFoundError


def get_mp3_duration_safe(file_path):
    try:
        audio = MP3(file_path)
        return audio.info.length * 1000  # milliseconds
    except HeaderNotFoundError:
        return None


def frange(start, stop, step):
    while start < stop:
        yield start
        start += step


def extract_metered_beats_correct(osu_lines, dur_ms):
    beats_with_meter = []

    # Collect all uninherited timing points
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
                        timing_points.append((time, beat_length, meter))
                except ValueError:
                    continue

    # Sort by time to be sure
    timing_points.sort()
    timing_points.append((dur_ms, None, None))  # Dummy end

    # Generate metered beats
    for i in range(len(timing_points) - 1):
        start_time, beat_len, meter = timing_points[i]
        end_time = timing_points[i + 1][0]

        beat_index = 1
        bt = start_time
        while bt < end_time:
            if bt >= 0:
                beats_with_meter.append((bt / 1000, beat_index))  # convert to seconds
            beat_index = (beat_index % meter) + 1
            bt += beat_len

    return beats_with_meter


def get_audio_filename_from_osu(osu_lines):
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


def process_osz_file(osz_path, audio_folder, annotation_folder):
    song_name = os.path.splitext(os.path.basename(osz_path))[0]

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(osz_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        osu_files = [f for f in os.listdir(tmpdir) if f.endswith(".osu")]
        if not osu_files:
            print(f"❌ No .osu file found in {song_name}")
            return

        osu_path = os.path.join(tmpdir, osu_files[0])
        with open(osu_path, 'r', encoding='utf-8') as f:
            osu_lines = f.readlines()

        target_mp3_name = get_audio_filename_from_osu(osu_lines)
        if not target_mp3_name:
            print(f"❌ AudioFilename not found in {song_name}")
            return

        target_mp3_path = os.path.join(tmpdir, target_mp3_name)
        if not os.path.isfile(target_mp3_path):
            if os.path.isfile(target_mp3_path.lower()):
                target_mp3_path = target_mp3_path.lower()
            else:
                print(f"❌ Expected mp3 file '{target_mp3_name}' not found in {song_name}")
                return

        duration_ms = get_mp3_duration_safe(target_mp3_path)
        if not duration_ms:
            print(f"❌ Unable to read duration of '{target_mp3_name}'")
            return

        os.makedirs(audio_folder, exist_ok=True)
        shutil.copy(target_mp3_path, os.path.join(audio_folder, f"{song_name}.mp3"))

        beats_with_meter = extract_metered_beats_correct(osu_lines, duration_ms)

        os.makedirs(annotation_folder, exist_ok=True)
        with open(os.path.join(annotation_folder, f"{song_name}_beats_metered.txt"), 'w') as bf:
            for b, m in beats_with_meter:
                bf.write(f"{b:.6f}\t{m}\n")

        print(f"✅ Processed {song_name}")


def process_all_osz(folder_path):
    audio_folder = os.path.join(folder_path, 'new_audio')
    annotation_folder = os.path.join(folder_path, 'metered_beats')
    os.makedirs(audio_folder, exist_ok=True)
    os.makedirs(annotation_folder, exist_ok=True)

    for file in os.listdir(folder_path):
        if file.endswith('.osz'):
            try:
                process_osz_file(os.path.join(folder_path, file), audio_folder, annotation_folder)
            except Exception as e:
                print(f"⚠️ Error processing {file}: {e}")


# === MAIN ===
if __name__ == "__main__":
    input_folder = './osz_folder'  # ← replace with your folder path
    process_all_osz(input_folder)
