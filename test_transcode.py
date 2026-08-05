import os
import time
import queue
import numpy as np
from PIL import Image
import wave
import struct

from engine.binary_resolver import BinaryResolver
from engine.hw_accel import HWAccelDetector
from engine.image_processor import ImageProcessor
from engine.ffmpeg_filtergraph import FiltergraphBuilder
from engine.transcode_worker import TranscodeWorker

def generate_synthetic_wav(filename: str, duration_sec: float = 3.0, freq: float = 440.0):
    sample_rate = 44100
    num_samples = int(duration_sec * sample_rate)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            value = int(16384 * np.sin(2 * np.pi * freq * t))
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

def test_full_transcode():
    print("Testing End-to-End MP4 Transcoding Pipeline...")
    ffmpeg, ffprobe = BinaryResolver.resolve_ffmpeg_and_ffprobe()
    assert ffmpeg and os.path.isfile(ffmpeg), "FFmpeg binary required"

    codec = HWAccelDetector.detect_best_encoder(ffmpeg)
    flags = HWAccelDetector.get_encoder_preset_flags(codec)

    # 1. Create synthetic audio & background image
    os.makedirs("test_out", exist_ok=True)
    audio_path = os.path.join("test_out", "synth_audio.wav")
    bg_image_path = os.path.join("test_out", "bg_test.png")
    output_mp4 = os.path.join("test_out", "output_test.mp4")

    if os.path.exists(output_mp4):
        os.remove(output_mp4)

    generate_synthetic_wav(audio_path, duration_sec=3.0)
    bg_img = ImageProcessor.process_background(None, 1920, 1080, mode="Cover")
    bg_img.save(bg_image_path, "PNG")

    # 2. Build Filtergraph
    filtergraph_str, out_label = FiltergraphBuilder.build_filtergraph(
        1920, 1080, "Line Waveform", "#00E676", (0.1, 0.7, 0.8, 0.2)
    )

    # 3. Launch Worker
    event_q = queue.Queue()
    worker = TranscodeWorker(
        ffmpeg_path=ffmpeg,
        audio_path=audio_path,
        bg_image_path=bg_image_path,
        output_path=output_mp4,
        duration_sec=3.0,
        codec=codec,
        codec_flags=flags,
        filtergraph_str=filtergraph_str,
        output_label=out_label,
        fps=30,
        event_queue=event_q
    )

    worker.start()

    # Process telemetry
    finished = False
    start_t = time.time()
    while time.time() - start_t < 15.0:
        try:
            payload = event_q.get(timeout=0.5)
            evt = payload.get("event")
            if evt == "TELEMETRY":
                print(f"[PROGRESS] {payload['percent']}% | FPS: {payload['fps']} | Speed: {payload['speed']}")
            elif evt == "COMPLETE":
                print(f"SUCCESS: MP4 Created at {payload['output_path']}")
                finished = True
                break
            elif evt == "ERROR":
                print(f"FAILED: {payload['error_msg']}")
                break
        except queue.Empty:
            if not worker.is_alive():
                break

    worker.join(timeout=2.0)
    assert finished and os.path.isfile(output_mp4), "Transcode failed to output MP4 file"
    print(f"Test Transcode Passed! MP4 File Size: {os.path.getsize(output_mp4)} bytes")

if __name__ == "__main__":
    test_full_transcode()
