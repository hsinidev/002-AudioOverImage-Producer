import json
import subprocess
import os
import numpy as np
from typing import Dict, Any, Optional, Tuple
from utils.logger import get_logger

logger = get_logger()

class AudioAnalyzer:
    """Probes audio metadata via FFprobe and performs NumPy spectrum/waveform binning."""

    @staticmethod
    def probe_audio_metadata(ffprobe_path: str, audio_path: str) -> Dict[str, Any]:
        """
        Run ffprobe JSON extraction to get exact duration (down to fractional ms),
        sample rate, channels, bitrate, format name.
        """
        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        cmd = [
            ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            audio_path
        ]

        creation_flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=creation_flags
        )

        if result.returncode != 0:
            raise RuntimeError(f"FFprobe metadata probe failed: {result.stderr}")

        data = json.loads(result.stdout)
        format_info = data.get("format", {})
        streams = data.get("streams", [])

        audio_stream = None
        for stream in streams:
            if stream.get("codec_type") == "audio":
                audio_stream = stream
                break

        duration_sec = float(format_info.get("duration", 0.0))
        if duration_sec == 0.0 and audio_stream:
            duration_sec = float(audio_stream.get("duration", 0.0))

        sample_rate = int(audio_stream.get("sample_rate", 44100)) if audio_stream else 44100
        channels = int(audio_stream.get("channels", 2)) if audio_stream else 2
        bitrate = int(format_info.get("bit_rate", 0)) if format_info.get("bit_rate") else 0
        codec_name = audio_stream.get("codec_name", "unknown") if audio_stream else "unknown"

        info = {
            "path": audio_path,
            "filename": os.path.basename(audio_path),
            "duration": duration_sec,
            "sample_rate": sample_rate,
            "channels": channels,
            "bitrate": bitrate,
            "codec": codec_name,
            "format": format_info.get("format_long_name", "Audio Track")
        }
        logger.info(f"Probed Audio: {info['filename']} | Duration: {duration_sec:.3f}s | {sample_rate}Hz | {channels}ch")
        return info

    @staticmethod
    def extract_pcm_samples(ffmpeg_path: str, audio_path: str, max_samples: int = 1000) -> np.ndarray:
        """
        Extract raw PCM s16le mono samples from audio file using FFmpeg pipe
        and calculate normalized amplitude array using NumPy vectorization.
        """
        if not ffmpeg_path or not os.path.isfile(audio_path):
            # Fallback to random waveform for preview
            return np.random.uniform(0.1, 0.9, size=max_samples)

        try:
            cmd = [
                ffmpeg_path,
                "-v", "quiet",
                "-i", audio_path,
                "-f", "s16le",
                "-ac", "1",
                "-ar", "8000",
                "pipe:1"
            ]
            creation_flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creation_flags
            )
            raw_data, _ = proc.communicate(timeout=10)
            
            if not raw_data:
                return np.random.uniform(0.1, 0.9, size=max_samples)

            audio_data = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
            if len(audio_data) == 0:
                return np.random.uniform(0.1, 0.9, size=max_samples)

            # Absolute amplitude normalization
            audio_data = np.abs(audio_data) / 32768.0

            # Resample / chunk into max_samples bins
            chunk_size = max(1, len(audio_data) // max_samples)
            binned = [
                np.mean(audio_data[i : i + chunk_size]) 
                for i in range(0, len(audio_data), chunk_size)
            ][:max_samples]

            binned_arr = np.array(binned, dtype=np.float32)
            max_val = np.max(binned_arr)
            if max_val > 0:
                binned_arr = binned_arr / max_val
            return binned_arr

        except Exception as e:
            logger.warning(f"PCM sample extraction failed ({e}), returning synthetic preview array.")
            return np.random.uniform(0.1, 0.9, size=max_samples)
