import sys
import os
import traceback
from utils.logger import setup_logger, get_logger

# Initialize system logger
logger = setup_logger("AudioOverImageProducer")

def main():
    """Main application entry point."""
    logger.info("Initializing AudioOverImage Producer...")

    try:
        # High DPI awareness on Windows
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(2) # Per-monitor DPI aware
            except Exception as e:
                logger.debug(f"DPI Awareness setup fallback: {e}")

        from gui.app import App
        app = App()
        app.mainloop()

    except Exception as e:
        logger.critical(f"Unhandled Application Exception: {e}\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
