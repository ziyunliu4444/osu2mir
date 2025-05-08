# osu-for-beat-tracking
Pipelines for using Osu! data for beat and downbeat tracking

Follow the following steps if you want to use Osu! data for beat and downbeat tracking:

1. Download .osz files (original beatmap files) using https://github.com/nzbasic/batch-beatmap-downloader. Remember to filter for only ranked beatmaps to ensure quality. For other filters, you can either follow our guide or choose on your own.

2. Use data_partition.py to group the .osz files into files with 1. single uninherited timing point 2. multiple uninherited timing point (>=5s apart) and 3. multiple uninherited timing point (<5s apart). Subset 1 and subset 2 should have high quality, use subset 3 with caution. Further details are in the guide.

3. Use data_conversion.py to convert .osz files into audio and corresponding metered beat annotations in .txt format, which are typically used as ground truth in beat and downbeat tracking research.

Extra:

You can use extract_uninherited_timing_points.py to extract only uninherited timing points in .json format with corresponding audio.

You can use song_info_csv.py to extract information including title, artist, creator, tags, number of uninherited timing points, and mp3 duration for all beatmaps in a folder into a single .csv file.

self_track_madmom.py is the pipeline we used to run madmom inferences in our guide. Use GPU if possible.

madmom_evaluation.py is the script we used to compare madmom result with user's annotations in the guide.
