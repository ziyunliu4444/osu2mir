import os
import json
from madmom.features.downbeats import RNNDownBeatProcessor, DBNDownBeatTrackingProcessor

# ===== Configuration =====
AUDIO_FOLDER = './audio'
OUTPUT_FOLDER = './madmom_results'
CHECKPOINT_FILE = './processing_checkpoint.json'  # File to track progress

# Ensure folders exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ===== Initialize Processors =====
rnn_processor = RNNDownBeatProcessor()
dbn_processor = DBNDownBeatTrackingProcessor(beats_per_bar=[3, 4], fps=100)

# ===== Checkpoint System =====
def load_checkpoint():
    """Load last processed file from checkpoint"""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f).get('last_processed')
    return None

def save_checkpoint(filename):
    """Save progress to checkpoint file"""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'last_processed': filename}, f)

# ===== Processing Function =====
def process_audio_file(audio_path):
    """Process single audio file and save results"""
    try:
        # Process with Madmom
        downbeat_act = rnn_processor(audio_path)
        beat_downbeat_times = dbn_processor(downbeat_act)
        
        # Prepare output paths
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        beats_path = os.path.join(OUTPUT_FOLDER, f'{base_name}_beats.txt')
        downbeats_path = os.path.join(OUTPUT_FOLDER, f'{base_name}_downbeats.txt')
        
        # Save results
        with open(beats_path, 'w') as bf, open(downbeats_path, 'w') as df:
            for beat_time, beat_num in beat_downbeat_times:
                bf.write(f"{beat_time:.4f}\n")
                if beat_num == 1:
                    df.write(f"{beat_time:.4f}\n")
        
        # Update checkpoint
        save_checkpoint(os.path.basename(audio_path))
        print(f"✅ Successfully processed {os.path.basename(audio_path)}")
        
    except Exception as e:
        print(f"❌ Failed to process {os.path.basename(audio_path)}: {str(e)}")

# ===== Main Processing Loop =====
def main():
    # Get sorted list of audio files (MP3)
    audio_files = sorted(
        f for f in os.listdir(AUDIO_FOLDER) 
        if f.lower().endswith(('.mp3')))
    
    # Find where to resume
    last_processed = load_checkpoint()
    start_index = audio_files.index(last_processed) + 1 if last_processed in audio_files else 0
    
    print(f"Found {len(audio_files)} files. Resuming from #{start_index + 1}...")
    
    # Process files
    for i in range(start_index, len(audio_files)):
        audio_file = audio_files[i]
        process_audio_file(os.path.join(AUDIO_FOLDER, audio_file))
        print(f"Progress: {i + 1}/{len(audio_files)} ({((i + 1)/len(audio_files))*100:.1f}%)")

if __name__ == "__main__":
    main()
    print("All files processed!")