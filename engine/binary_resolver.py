import os
import sys
import shutil
from typing import Optional, Tuple
from utils.logger import get_logger

logger = get_logger()

class BinaryResolver:
    """
    4-Tier Binary Resolution Engine for ffmpeg.exe and ffprobe.exe:
    Tier 1: sys._MEIPASS (PyInstaller bundle directory)
    Tier 2: Application execution directory / 'bin' subfolder
    Tier 3: System PATH (shutil.which)
    Tier 4: Manual selection fallback / interactive prompt
    """
    
    @staticmethod
    def get_binary_path(binary_name: str) -> Optional[str]:
        """Resolve absolute path for binary (ffmpeg.exe or ffprobe.exe)."""
        if not binary_name.lower().endswith(".exe"):
            binary_name_exe = f"{binary_name}.exe"
        else:
            binary_name_exe = binary_name
            
        # Tier 1: PyInstaller _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            meipass_path = os.path.join(sys._MEIPASS, binary_name_exe)
            if os.path.isfile(meipass_path):
                logger.info(f"Resolved {binary_name} via PyInstaller bundle: {meipass_path}")
                return meipass_path
            
        # Tier 2: Application root and ./bin subfolder
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        local_bin_path = os.path.join(app_dir, "bin", binary_name_exe)
        if os.path.isfile(local_bin_path):
            logger.info(f"Resolved {binary_name} via local bin directory: {local_bin_path}")
            return local_bin_path
            
        local_root_path = os.path.join(app_dir, binary_name_exe)
        if os.path.isfile(local_root_path):
            logger.info(f"Resolved {binary_name} via app root directory: {local_root_path}")
            return local_root_path

        # Tier 3: System PATH
        path_in_env = shutil.which(binary_name_exe) or shutil.which(binary_name)
        if path_in_env and os.path.isfile(path_in_env):
            logger.info(f"Resolved {binary_name} via system PATH: {path_in_env}")
            return path_in_env

        logger.warning(f"Could not automatically resolve binary: {binary_name}")
        return None

    @classmethod
    def resolve_ffmpeg_and_ffprobe(cls) -> Tuple[Optional[str], Optional[str]]:
        """Resolve both ffmpeg and ffprobe paths."""
        ffmpeg = cls.get_binary_path("ffmpeg")
        ffprobe = cls.get_binary_path("ffprobe")
        return ffmpeg, ffprobe
