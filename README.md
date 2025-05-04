# osu-for-beat-tracking
Pipelines for using Osu! data for beat and downbeat tracking

.osz files (original beatmap files) can be batch-downloaded at https://github.com/nzbasic/batch-beatmap-downloader

data_partition groups the .osz files into files with 1. single uninherited timing point 2. multiple uninherited timing point (>=5s apart) and 3. multiple uninherited timing point (<5s apart)

data_conversion converts .osz files into audio and corresponding metered beat annotations in .txt format, which are typically used as ground truth in beat and downbeat tracking research

extract_uninherited_timing_points extracts uninherited timing points in .json format with corresponding audio
