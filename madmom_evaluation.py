import os
import numpy as np
import pandas as pd
from madmom.evaluation.beats import BeatEvaluation, BeatMeanEvaluation

def extract_selected_metrics(eval_obj):
    return {
        "fmeasure": eval_obj.fmeasure,
        "cmlt": eval_obj.cmlt,
        "amlt": eval_obj.amlt,
    }

def evaluate_folder_f_cmlt_amlt(madmom_folder, label_folder, output_csv):
    beat_evals = []
    downbeat_evals = []
    results = []

    for file in os.listdir(label_folder):
        if not file.endswith("_beats_metered.txt"):
            continue

        song_id = file.replace("_beats_metered.txt", "")
        label_path = os.path.join(label_folder, file)
        beat_path = os.path.join(madmom_folder, f"{song_id}_beats.txt")
        downbeat_path = os.path.join(madmom_folder, f"{song_id}_downbeats.txt")

        if not os.path.exists(beat_path) or not os.path.exists(downbeat_path):
            continue

        # Load detections
        detected_beats = np.loadtxt(beat_path)
        detected_downbeats = np.loadtxt(downbeat_path)

        # Load ground truth
        gt_data = pd.read_csv(label_path, sep="\t", header=None, names=["time", "meter"])
        gt_beats = gt_data["time"].values
        gt_downbeats = gt_data[gt_data["meter"] == 1]["time"].values

        # Evaluate
        beat_eval = BeatEvaluation(detected_beats, gt_beats)
        downbeat_eval = BeatEvaluation(detected_downbeats, gt_downbeats, downbeats=True)

        beat_evals.append(beat_eval)
        downbeat_evals.append(downbeat_eval)

        beat_metrics = extract_selected_metrics(beat_eval)
        downbeat_metrics = extract_selected_metrics(downbeat_eval)

        results.append({
            "song_id": song_id,
            **{f"beat_{k}": v for k, v in beat_metrics.items()},
            **{f"downbeat_{k}": v for k, v in downbeat_metrics.items()},
        })

    # Mean evaluations
    beat_mean = BeatMeanEvaluation(beat_evals)
    downbeat_mean = BeatMeanEvaluation(downbeat_evals)

    results.append({
        "song_id": "MEAN",
        **{f"beat_{k}": v for k, v in extract_selected_metrics(beat_mean).items()},
        **{f"downbeat_{k}": v for k, v in extract_selected_metrics(downbeat_mean).items()},
    })

    # Save
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"✅ Evaluation (F-measure, CMLt, AMLt) complete. Saved to {output_csv}")

if __name__ == "__main__":
    madmom_folder = "./madmom_results"
    label_folder = "./metered_beats"
    output_csv = "./f_cmlt_amlt_results.csv"

    evaluate_folder_f_cmlt_amlt(madmom_folder, label_folder, output_csv)
