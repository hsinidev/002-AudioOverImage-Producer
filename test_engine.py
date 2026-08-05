import os
import sys
import unittest
import numpy as np
from PIL import Image

from engine.binary_resolver import BinaryResolver
from engine.hw_accel import HWAccelDetector
from engine.audio_analyzer import AudioAnalyzer
from engine.image_processor import ImageProcessor
from engine.ffmpeg_filtergraph import FiltergraphBuilder
from utils.helpers import format_seconds_to_timecode, hex_to_rgb, calculate_aspect_fit_bounds

class TestAudioOverImageEngine(unittest.TestCase):

    def test_helpers(self):
        self.assertEqual(format_seconds_to_timecode(65.5), "00:01:05.500")
        self.assertEqual(hex_to_rgb("#00E676"), (0, 230, 118))
        x, y, w, h = calculate_aspect_fit_bounds(1920, 1080, 800, 600)
        self.assertEqual(w, 800)
        self.assertEqual(h, 450)
        self.assertEqual(x, 0)
        self.assertEqual(y, 75)

    def test_binary_resolver(self):
        ffmpeg, ffprobe = BinaryResolver.resolve_ffmpeg_and_ffprobe()
        print(f"Binary Resolution Result: ffmpeg={ffmpeg}, ffprobe={ffprobe}")

    def test_hw_accel(self):
        ffmpeg, _ = BinaryResolver.resolve_ffmpeg_and_ffprobe()
        best_encoder = HWAccelDetector.detect_best_encoder(ffmpeg)
        self.assertIn(best_encoder, ["h264_nvenc", "h264_qsv", "h264_amf", "libx264"])
        print(f"Best Encoder Detected: {best_encoder}")

    def test_image_processor(self):
        # Create test image
        img = ImageProcessor.process_background(
            None, 1920, 1080, mode="Cover", pad_color_hex="#0A0E14"
        )
        self.assertEqual(img.size, (1920, 1080))
        self.assertEqual(img.mode, "RGBA")

        # Test Dual-Layer Blur
        img_blur = ImageProcessor.process_background(
            "assets/sample_bg.png", 1080, 1920, mode="Dual-Layer Blur"
        )
        self.assertEqual(img_blur.size, (1080, 1920))

    def test_filtergraph_builder(self):
        filter_str, out_label = FiltergraphBuilder.build_filtergraph(
            1920, 1080, "Line Waveform", "#00E676", (0.1, 0.7, 0.8, 0.2)
        )
        self.assertIn("showwaves", filter_str)
        self.assertEqual(out_label, "[outv]")

        filter_freq, _ = FiltergraphBuilder.build_filtergraph(
            1080, 1920, "Audio Frequency Histogram", "#1DE9B6", (0.05, 0.8, 0.9, 0.15)
        )
        self.assertIn("showfreqs", filter_freq)

if __name__ == "__main__":
    unittest.main()
