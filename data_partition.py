import os
import shutil
import zipfile


def parse_osu_timing_points(osu_file_obj):
    """Extract uninherited timing points from an open .osu file-like object."""
    lines = osu_file_obj.read().decode('utf-8').splitlines()

    timing_section = False
    uninherited_timing_points = []

    for line in lines:
        line = line.strip()
        if line == "[TimingPoints]":
            timing_section = True
            continue
        if timing_section:
            if line == "" or line.startswith("["):
                break  # End of the Timing Points section
            parts = line.split(",")
            if len(parts) > 6:
                time_position = float(parts[0])  # Timestamp of the timing point
                uninherited = int(parts[6])  # 1 = uninherited, 0 = inherited
                if uninherited == 1:
                    uninherited_timing_points.append(time_position)

    return uninherited_timing_points


def classify_timing_points(timing_points, min_separation=5000):
    """Classify the song based on the number of uninherited timing points and their separation."""
    if len(timing_points) == 1:
        return 'single_timing_point'
    timing_points.sort()
    # Check if any uninherited timing points are less than min_separation ms apart
    for i in range(len(timing_points) - 1):
        if timing_points[i + 1] - timing_points[i] < min_separation:
            return 'multiple_timings_less_than_5s'
    return 'multiple_timings_5s_or_more_apart'


def process_beatmaps(osz_folder, output_folder_single, output_folder_5s_or_more_apart, output_folder_less_than_5s_apart):
    os.makedirs(output_folder_single, exist_ok=True)
    os.makedirs(output_folder_5s_or_more_apart, exist_ok=True)
    os.makedirs(output_folder_less_than_5s_apart, exist_ok=True)

    for filename in os.listdir(osz_folder):
        if not filename.endswith(".osz"):
            continue

        osz_path = os.path.join(osz_folder, filename)

        try:
            with zipfile.ZipFile(osz_path, 'r') as zip_ref:
                osu_filenames = [f for f in zip_ref.namelist() if f.endswith(".osu")]
                if not osu_filenames:
                    print(f"⚠️ No .osu file found in {filename}")
                    continue

                # Just use the first .osu file found
                with zip_ref.open(osu_filenames[0]) as osu_file:
                    timing_points = parse_osu_timing_points(osu_file)

            # Classify the song into one of the three categories
            category = classify_timing_points(timing_points)

            if category == 'single_timing_point':
                dest_folder = os.path.join(output_folder_single)
                print(f"✅ {filename} → Single uninherited timing point")
            elif category == 'multiple_timings_less_than_5s':
                dest_folder = os.path.join(output_folder_less_than_5s_apart)
                print(f"❌ {filename} → Multiple uninherited timing points, < 5s apart")
            else:
                dest_folder = os.path.join(output_folder_5s_or_more_apart)
                print(f"✅ {filename} → Multiple uninherited timing points, ≥ 5s apart")

            os.makedirs(dest_folder, exist_ok=True)
            shutil.move(osz_path, os.path.join(dest_folder, filename))

        except Exception as e:
            print(f"❗ Error processing {filename}: {e}")

    print("🎵 Sorting complete!")


# Example usage
osu_folder = "./osz_with_change"  # Folder containing .osz files
output_folder_single = "./single_timing_point"  # Destination for songs with a single uninherited timing point
output_folder_5s_or_more_apart = "./timing_5s_or_more_apart"  # Destination for songs with timings ≥ 5s apart
output_folder_less_than_5s_apart = "./timing_less_than_5s_apart"  # Destination for songs with timings < 5s apart

process_beatmaps(osu_folder, output_folder_single, output_folder_5s_or_more_apart, output_folder_less_than_5s_apart)
