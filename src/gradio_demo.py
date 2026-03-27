import torch, uuid, sys
import os, shutil, glob, subprocess
from pydub import AudioSegment


def mp3_to_wav(mp3_filename, wav_filename, frame_rate):
    mp3_file = AudioSegment.from_file(file=mp3_filename)
    mp3_file.set_frame_rate(frame_rate).export(wav_filename, format="wav")


class SadTalker():

    def __init__(self, checkpoint_path='checkpoints', config_path='src/config', lazy_load=False):
        self.checkpoint_path = checkpoint_path
        self.config_path = config_path
        os.environ['TORCH_HOME'] = checkpoint_path
        self.python = sys.executable
        self.sadtalker_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"SadTalker subprocess runner ready. Python: {self.python}", flush=True)

    def test(self, source_image, driven_audio, preprocess='crop',
             still_mode=False, use_enhancer=False, batch_size=1, size=256,
             pose_style=0, exp_scale=1.0,
             use_ref_video=False, ref_video=None, ref_info=None,
             use_idle_mode=False, length_of_audio=0, use_blink=True,
             result_dir='./results/'):

        print(f"source_image={source_image!r}", flush=True)
        print(f"driven_audio={driven_audio!r}", flush=True)

        # Handle MP3 → WAV conversion
        audio_file = driven_audio
        if driven_audio is not None and driven_audio.lower().endswith('.mp3'):
            wav_file = driven_audio[:-4] + '.wav'
            mp3_to_wav(driven_audio, wav_file, 16000)
            audio_file = wav_file

        run_id = str(uuid.uuid4())
        out_dir = os.path.join(result_dir, run_id)
        os.makedirs(out_dir, exist_ok=True)

        cmd = [
            self.python,
            os.path.join(self.sadtalker_root, 'inference.py'),
            '--driven_audio', audio_file,
            '--source_image', source_image,
            '--result_dir', out_dir,
            '--checkpoint_dir', self.checkpoint_path,
            '--preprocess', preprocess,
            '--size', str(size),
            '--batch_size', str(batch_size),
            '--pose_style', str(pose_style),
        ]
        if still_mode:
            cmd.append('--still')
        if use_enhancer:
            cmd.extend(['--enhancer', 'gfpgan'])

        print(f"Launching inference subprocess (batch_size={batch_size})...", flush=True)
        proc = subprocess.run(cmd, cwd=self.sadtalker_root, timeout=3600)

        if proc.returncode != 0:
            raise RuntimeError(f"inference.py failed with exit code {proc.returncode}")

        mp4_files = sorted(glob.glob(os.path.join(out_dir, '*.mp4')))
        if not mp4_files:
            raise RuntimeError(f"No output video found in {out_dir}")

        return_path = mp4_files[-1]
        print(f"Generated: {return_path}", flush=True)
        return return_path
