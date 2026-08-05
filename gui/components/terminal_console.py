import customtkinter as ctk
from gui.styles.theme_tokens import COLOR_PALETTE, TYPOGRAPHY
from utils.logger import get_logger

logger = get_logger()

class TerminalConsole(ctk.CTkFrame):
    """Collapsible Thread-Safe Stderr Log Terminal Console."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_PALETTE["background_secondary"], corner_radius=6, **kwargs)
        self.is_collapsed = True

        self._build_ui()

    def _build_ui(self):
        """Build terminal console UI layout."""
        self.grid_columnconfigure(0, weight=1)

        # Header Bar
        header_frame = ctk.CTkFrame(self, fg_color=COLOR_PALETTE["surface_card"], height=30)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        lbl_header = ctk.CTkLabel(
            header_frame,
            text="💻 Engine Log Console",
            font=(TYPOGRAPHY["font_family"], 11, "bold"),
            text_color=COLOR_PALETTE["text_secondary"]
        )
        lbl_header.grid(row=0, column=0, padx=10, pady=4, sticky="w")

        # Action Buttons
        btn_clear = ctk.CTkButton(
            header_frame,
            text="Clear", width=50, height=22,
            font=(TYPOGRAPHY["font_family"], 9),
            fg_color=COLOR_PALETTE["background_secondary"],
            hover_color=COLOR_PALETTE["border_color"],
            command=self.clear_logs
        )
        btn_clear.grid(row=0, column=1, padx=5, pady=4)

        self.btn_toggle = ctk.CTkButton(
            header_frame,
            text="▲ Expand", width=70, height=22,
            font=(TYPOGRAPHY["font_family"], 9, "bold"),
            fg_color=COLOR_PALETTE["border_color"],
            hover_color=COLOR_PALETTE["surface_card"],
            command=self.toggle_collapse
        )
        self.btn_toggle.grid(row=0, column=2, padx=(2, 10), pady=4)

        # Textbox Console
        self.textbox = ctk.CTkTextbox(
            self,
            fg_color=COLOR_PALETTE["background_primary"],
            text_color=COLOR_PALETTE["text_primary"],
            font=(TYPOGRAPHY["font_family_mono"], 9),
            wrap="word",
            height=100
        )
        self.textbox.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.textbox.configure(state="disabled")

        # Start collapsed by default to save canvas preview space
        self.textbox.grid_remove()

    def toggle_collapse(self):
        """Toggle terminal visibility."""
        if self.is_collapsed:
            self.textbox.grid()
            self.btn_toggle.configure(text="▼ Collapse")
            self.is_collapsed = False
        else:
            self.textbox.grid_remove()
            self.btn_toggle.configure(text="▲ Expand")
            self.is_collapsed = True

    def append_log(self, text: str):
        """Append log text to console (thread-safe UI update)."""
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text.strip() + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def clear_logs(self):
        """Clear log console text."""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
