from typing import Dict, Any, Tuple
from utils.logger import get_logger

logger = get_logger()

class FiltergraphBuilder:
    """Constructs dynamic FFmpeg -filter_complex filtergraphs for waveform/spectrum overlays."""

    @staticmethod
    def build_filtergraph(
        export_w: int,
        export_h: int,
        wave_mode: str,          # "Line Waveform", "Solid Bars", "Circular Spectrum", "Audio Frequency Histogram", "None"
        wave_color: str,         # e.g., "#00E676" or "#00E676|#1DE9B6"
        norm_bounds: Tuple[float, float, float, float] # (x_norm, y_norm, w_norm, h_norm)
    ) -> Tuple[str, str]:
        """
        Build complex filtergraph string and output map label.
        Returns: (filter_complex_str, output_video_label)
        """
        if wave_mode == "None" or not norm_bounds:
            # Simple scale pass-through if no overlay requested
            filter_str = f"[0:v]scale={export_w}:{export_h}[outv]"
            return filter_str, "[outv]"

        x_norm, y_norm, w_norm, h_norm = norm_bounds
        
        # Calculate pixel dimensions for visualizer box
        wave_w = int(round(w_norm * export_w))
        wave_h = int(round(h_norm * export_h))
        x_pixel = int(round(x_norm * export_w))
        y_pixel = int(round(y_norm * export_h))

        # Enforce minimum size & even dimensions for FFmpeg
        wave_w = max(64, wave_w if wave_w % 2 == 0 else wave_w + 1)
        wave_h = max(32, wave_h if wave_h % 2 == 0 else wave_h + 1)

        # Sanitize color string for FFmpeg (escape colon / hash if needed)
        # FFmpeg accepts hex formatted like #00E676 or 0x00E676 or color strings like green
        ffmpeg_color = wave_color.replace("#", "0x") if "#" in wave_color else wave_color

        filter_chains = []
        filter_chains.append(f"[0:v]scale={export_w}:{export_h}[bg]")

        if wave_mode == "Line Waveform":
            # showwaves mode=line
            filter_chains.append(
                f"[1:a]showwaves=s={wave_w}x{wave_h}:mode=line:colors={ffmpeg_color}:scale=lin[wave]"
            )
        elif wave_mode == "Solid Bars":
            # showwaves mode=point/p2p or mode=bar
            filter_chains.append(
                f"[1:a]showwaves=s={wave_w}x{wave_h}:mode=p2p:colors={ffmpeg_color}:scale=lin[wave]"
            )
        elif wave_mode == "Audio Frequency Histogram":
            # showfreqs logarithmic bar spectrum
            filter_chains.append(
                f"[1:a]showfreqs=s={wave_w}x{wave_h}:mode=bar:ascale=log:fscale=log:colors={ffmpeg_color}[wave]"
            )
        elif wave_mode == "Circular Spectrum":
            # showfreqs in dot or bar format (or showwaves line format)
            filter_chains.append(
                f"[1:a]showfreqs=s={wave_w}x{wave_h}:mode=dot:ascale=log:fscale=log:colors={ffmpeg_color}[wave]"
            )
        else:
            filter_chains.append(
                f"[1:a]showwaves=s={wave_w}x{wave_h}:mode=line:colors={ffmpeg_color}:scale=lin[wave]"
            )

        filter_chains.append(f"[bg][wave]overlay=x={x_pixel}:y={y_pixel}:format=auto[outv]")
        
        filter_graph = ";".join(filter_chains)
        logger.info(f"Generated Filtergraph: mode={wave_mode} | box={wave_w}x{wave_h} @ ({x_pixel},{y_pixel})")
        return filter_graph, "[outv]"
