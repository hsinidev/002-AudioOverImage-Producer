import os
import re
import sys
import time
import queue
import subprocess
import threading
from typing import Dict, Any, Optional, Tuple
from utils.logger import get_logger
from utils.helpers import format_seconds_to_timecode

logger = get_logger()

class TranscodeWorker(threading.Thread):
    """
    Background Thread executing FFmpeg transcoding with zero-waste static looping,
    hardware acceleration, real-time stderr telemetry parsing, and process-group isolation.
    """

    def __init__(
        self,
        ffmpeg_path: str,
        audio_path: str,
        bg_image_path: str, # Pre-processed image file path
        output_path: str,
        duration_sec: float,
        codec: str,
        codec_flags: list,
        filtergraph_str: str,
        output_label: str,
        fps: int,
        event_queue: queue.Queue
    ):
        super().__init__(daemon=True)
        self.ffmpeg_path = ffmpeg_path
        self.audio_path = audio_path
        self.bg_image_path = bg_image_path
        self.output_path = output_path
        self.duration_sec = max(0.1, duration_sec)
        self.codec = codec
        self.codec_flags = codec_flags
        self.filtergraph_str = filtergraph_str
        self.output_label = output_label
        self.fps = fps
        self.event_queue = event_queue

        self.process: Optional[subprocess.Popen] = None
        self._is_cancelled = False
        self._stop_event = threading.Event()

    def run(self):
        logger.info(f"Starting Transcode Worker thread for output: {self.output_path}")
        start_time = time.time()

        try:
            # Build zero-waste FFmpeg command line
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-loop", "1",
                "-framerate", str(self.fps),
                "-i", self.bg_image_path,
                "-i", self.audio_path
            ]

            if self.filtergraph_str:
                cmd.extend(["-filter_complex", self.filtergraph_str])
                cmd.extend(["-map", self.output_label if self.output_label else "[outv]"])
                cmd.extend(["-map", "1:a"])
            else:
                cmd.extend(["-map", "0:v"])
                cmd.extend(["-map", "1:a"])

            cmd.extend(["-c:v", self.codec])
            cmd.extend(self.codec_flags)

            # Audio encoding flags
            cmd.extend([
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                self.output_path
            ])

            logger.info(f"FFmpeg Command: {' '.join(cmd)}")

            # Process group creation flags on Windows
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | (subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0)

            self.process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                text=True,
                bufsize=1,
                creationflags=creation_flags
            )

            # Regex pattern matchers for stderr telemetry line parsing
            time_regex = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})")
            fps_regex = re.compile(r"fps=\s*([0-9.]+)")
            speed_regex = re.compile(r"speed=\s*([0-9.]+)x")
            frame_regex = re.compile(r"frame=\s*(\d+)")

            last_percent = 0.0

            # Read stderr line-by-line
            while True:
                if self._stop_event.is_set():
                    break

                line = self.process.stderr.readline()
                if not line:
                    if self.process.poll() is not None:
                        break
                    continue

                line_str = line.strip()
                if not line_str:
                    continue

                # Parse metrics
                current_sec = 0.0
                time_match = time_regex.search(line_str)
                if time_match:
                    h, m, s, ms = map(int, time_match.groups())
                    current_sec = h * 3600 + m * 60 + s + (ms / 100.0)

                fps_val = 0.0
                fps_match = fps_regex.search(line_str)
                if fps_match:
                    try:
                        fps_val = float(fps_match.group(1))
                    except ValueError:
                        pass

                speed_val = 1.0
                speed_str = "1.0x"
                speed_match = speed_regex.search(line_str)
                if speed_match:
                    try:
                        speed_val = float(speed_match.group(1))
                        speed_str = f"{speed_val:.2f}x"
                    except ValueError:
                        pass

                frame_val = 0
                frame_match = frame_regex.search(line_str)
                if frame_match:
                    try:
                        frame_val = int(frame_match.group(1))
                    except ValueError:
                        pass

                if current_sec > 0:
                    percent = min(100.0, (current_sec / self.duration_sec) * 100.0)
                    last_percent = percent
                    remaining_sec = max(0.0, self.duration_sec - current_sec)
                    eta_sec = remaining_sec / max(0.1, speed_val)

                    payload = {
                        "event": "TELEMETRY",
                        "percent": round(percent, 2),
                        "current_frame": frame_val,
                        "current_time_sec": round(current_sec, 2),
                        "total_duration_sec": round(self.duration_sec, 2),
                        "fps": round(fps_val, 1),
                        "speed": speed_str,
                        "eta_seconds": round(eta_sec, 1),
                        "log_line": line_str
                    }
                    self.event_queue.put(payload)
                else:
                    # Generic log line
                    self.event_queue.put({
                        "event": "LOG",
                        "text": line_str
                    })

            self.process.wait()

            if self._is_cancelled:
                logger.warning("Render job was cancelled by user.")
                self._cleanup_partial_files()
                self.event_queue.put({"event": "ABORTED", "message": "Render job aborted by user."})
                return

            if self.process.returncode == 0 and os.path.isfile(self.output_path):
                elapsed = time.time() - start_time
                logger.info(f"Render completed successfully in {elapsed:.2f}s: {self.output_path}")
                self.event_queue.put({
                    "event": "COMPLETE",
                    "output_path": self.output_path,
                    "elapsed_sec": round(elapsed, 2)
                })
            else:
                err_msg = f"FFmpeg exited with error code {self.process.returncode}."
                logger.error(err_msg)
                self._cleanup_partial_files()
                self.event_queue.put({"event": "ERROR", "error_msg": err_msg})

        except Exception as e:
            logger.error(f"Transcode worker unhandled exception: {e}")
            self._cleanup_partial_files()
            self.event_queue.put({"event": "ERROR", "error_msg": str(e)})

    def cancel(self):
        """Cancel rendering process safely via Windows taskkill tree PID termination."""
        self._is_cancelled = True
        self._stop_event.set()

        if self.process and self.process.poll() is None:
            logger.info(f"Terminating subprocess PID tree: {self.process.pid}")
            try:
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.process.pid)], capture_output=True)
                else:
                    self.process.terminate()
            except Exception as e:
                logger.error(f"Failed to kill process tree: {e}")

    def _cleanup_partial_files(self):
        """Remove partial mp4 output file if render aborted/failed."""
        if os.path.isfile(self.output_path):
            try:
                os.remove(self.output_path)
                logger.info(f"Cleaned up partial output file: {self.output_path}")
            except Exception as e:
                logger.warning(f"Could not remove partial output file ({self.output_path}): {e}")
