import subprocess
from typing import Optional, List
from utils.logger import get_logger

logger = get_logger()

class HWAccelDetector:
    """Probes FFmpeg for available hardware video encoders."""
    
    ENCODER_PRIORITY = [
        ("h264_nvenc", "NVIDIA NVENC Hardware Acceleration"),
        ("h264_qsv", "Intel QuickSync Hardware Acceleration"),
        ("h264_amf", "AMD AMF Hardware Acceleration"),
        ("libx264", "Software CPU Transcoder (libx264)")
    ]

    @classmethod
    def detect_best_encoder(cls, ffmpeg_path: str) -> str:
        """
        Check FFmpeg for supported encoders and return highest priority available codec.
        """
        if not ffmpeg_path:
            logger.warning("No FFmpeg path provided to HWAccelDetector. Defaulting to libx264.")
            return "libx264"

        try:
            cmd = [ffmpeg_path, "-encoders", "-v", "quiet"]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
            )
            output = result.stdout.lower()

            for codec, description in cls.ENCODER_PRIORITY:
                if codec in output:
                    logger.info(f"Hardware acceleration auto-detected: {codec} ({description})")
                    return codec
                    
        except Exception as e:
            logger.error(f"Error checking hardware encoders via FFmpeg: {e}")

        logger.info("Fallback to software CPU codec: libx264")
        return "libx264"

    @classmethod
    def get_encoder_preset_flags(cls, codec: str) -> List[str]:
        """Return optimal preset flags for the given codec."""
        if codec == "h264_nvenc":
            return ["-preset", "p4", "-tune", "hq", "-rc", "vbr", "-cq", "18"]
        elif codec == "h264_qsv":
            return ["-preset", "medium", "-global_quality", "18"]
        elif codec == "h264_amf":
            return ["-usage", "transcoding", "-quality", "quality", "-rc", "cqp", "-qp_p", "18", "-qp_i", "18"]
        else: # libx264
            return ["-preset", "medium", "-crf", "18", "-tune", "stillimage"]
