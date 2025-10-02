# Osu2MIR

Repository for Osu2MIR: Beat Tracking Dataset Derived From Osu! Data (ISMIR2025 LBD)

arXiv: https://arxiv.org/abs/2509.12667

<img width="680" height="277" alt="thumbnail" src="https://github.com/user-attachments/assets/12fcc65d-6b9c-43a3-b0cf-9ae07aada290" />



## Standalone Dataset

osu2beat2025_metered_beats.zip contains the metered beats of the second subset in our study, covering 741 user annotations for 708 distinct audios. The naming format is `<MD5>`_`<BeatmapSetID>`_beats_metered.txt. We do not own the copyright of the audio files, so you need to download the audio files by yourself, and here's the recommended procedure:

1. Download the beatmap with the given `<BeatmapSetID>` from https://osu.ppy.sh/beatmapsets/BeatmapSetID. (For easier download, you may refer to the original code in https://github.com/nzbasic/batch-beatmap-downloader.)
2. Extract the `.osz` file to obtain the MP3.
3. Compute the MD5 checksum of the MP3 and verify it matches `<MD5>`.


## Constructing Your Own Dataset

### Step 1: Download Beatmaps

Download .osz files (original beatmap files) using https://github.com/nzbasic/batch-beatmap-downloader. Remember to filter for only ranked beatmaps to ensure quality. For other filters, you can either follow our paper or choose on your own.

### Step 2: Partition the Data

Use data_partition.py to group the .osz files into files with 1. single uninherited timing point 2. multiple uninherited timing point (>=5s apart) and 3. multiple uninherited timing point (<5s apart). Subset 1 and subset 2 should have high quality, use subset 3 with caution. Further details are in the paper. Feel free to experiment with other conditions.

### Step 3: Convert to Metered Beats

Use data_conversion.py to convert .osz files into audio and corresponding metered beat annotations in .txt format, which are typically used as ground truth in beat and downbeat tracking research.

## Additional Tools

extract_uninherited_timing_points.py extracts only uninherited timing points in .json format with corresponding audio.

song_info_csv.py extracts information including title, artist, creator, tags, number of uninherited timing points, and mp3 duration for all beatmaps in a folder into a single .csv file.

self_track_madmom.py is the pipeline we used to run madmom inferences in our guide. Use GPU if possible.

madmom_evaluation.py is the script we used to compare madmom result with user's annotations in the guide.

## Tables

The .csv files are the original tables we used for our analysis in the paper, single represents songs with single uninherited timing point, geq5 represents songs with multiple uninherited timing points >=5s apart, le5 represents songs with uninherited timing points <5s apart.

## Contributing

Join us to build a community where beatmap creators and MIR researchers develop and expand tools together to support various needs!

Discord: https://discord.gg/hYM3NkTzAW
