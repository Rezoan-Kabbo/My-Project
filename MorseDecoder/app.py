"""
app.py
-------
MORSE SIGNAL LAB — Modern CustomTkinter desktop application for DSP & Systems (CSE-220).

Tabs:
    1. Converter     - Text <-> Morse, Audio preview, Live PARIS timing & Reference table (Level 1)
    2. Signal Lab     - Sine-tone synthesis, WPM/Freq/Vol, Waveform, FFT & Spectrogram, WAV export (Level 2)
    3. Noise & Filter - AWGN / 60Hz hum / Clicks injection, Bandpass filter, Before/After & Accuracy (Level 3)
    4. Mic Decode     - Robust microphone recording & WAV audio demodulator, carrier detection,
                        adaptive Otsu thresholding, envelope visualization, audio playback & export (Level 4)
"""

# To Run : python app.py

import json
from pathlib import Path
import queue
import sys
import tkinter as tk
from tkinter import messagebox
from typing import Optional
import numpy as np
import customtkinter as ctk   # python -m pip install customtkinter 

import morse_code as mc
import signal_proc as sp

# Modular UI Components
from ui.theme import get_plot_theme, style_axis
from ui.converter_tab import ConverterTab
from ui.signal_tab import SignalLabTab
from ui.noise_tab import NoiseFilterTab
from ui.mic_tab import MicDecodeTab

# Set default CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MorseSignalLab(ctk.CTk):
    """
    Main application window managing shared signal state, window persistence,
    status toasts, and tab coordination.
    """

    def __init__(self):
        super().__init__()
        self.title("Morse Signal Lab — DSP & Systems (CSE-220)")
        self.geometry("1020x780")
        self.minsize(880, 680)

        self._status_timer: Optional[str] = None
        self._task_queue: queue.Queue = queue.Queue()
        self._poll_ui_queue()

        # Shared application signal state
        self.current_signal: np.ndarray = np.array([])
        self.current_sample_rate: int = 44100
        self.current_morse: str = mc.text_to_morse("SOS")
        self.noisy_signal: np.ndarray = np.array([])
        self.filtered_signal: np.ndarray = np.array([])
        self.recorded_signal: np.ndarray = np.array([])
        self.recorded_sample_rate: int = 44100
        self.recorded_details: dict = {}

        # 1. Top Header Bar
        self._build_header()

        # 2. Bottom Status Bar / Toast Container (UI Polish 4.5)
        self._build_status_bar()

        # 3. Main Tabview Container
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill='both', expand=True, padx=14, pady=(0, 6))

        tab_conv = self.tabview.add("1. Converter")
        tab_sig = self.tabview.add("2. Signal Lab")
        tab_noise = self.tabview.add("3. Noise & Filter")
        tab_mic = self.tabview.add("4. Mic & Audio Decode")

        # 4. Instantiate Tab Frames
        self.converter_tab = ConverterTab(tab_conv, self)
        self.signal_tab = SignalLabTab(tab_sig, self)
        self.noise_tab = NoiseFilterTab(tab_noise, self)
        self.mic_tab = MicDecodeTab(tab_mic, self)

        # 5. Restore saved window geometry and appearance mode (UI Polish 4.4)
        self._restore_window_state()

        # 6. Window close handler to persist window state
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Notify if physical sound hardware is unavailable
        if not sp.SOUND_AVAILABLE:
            self.after(250, lambda: self.show_status(
                "Audio hardware unavailable: Sound recording/playback muted. DSP synthesis/decode fully functional.",
                level="warning",
                duration_ms=6000
            ))

    # ----------------------------------------------------------------------
    # Config & State Persistence (UI Polish 4.4)
    # ----------------------------------------------------------------------

    @staticmethod
    def _get_config_path() -> Path:
        try:
            return Path.home() / ".morse_signal_lab_config.json"
        except Exception:
            return Path(__file__).parent / ".morse_signal_lab_config.json"

    def _restore_window_state(self):
        """Restore window size, position, and appearance mode from config file."""
        cfg_path = self._get_config_path()
        if not cfg_path.exists():
            return
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            geom = data.get("geometry")
            if geom and isinstance(geom, str) and "x" in geom:
                self.geometry(geom)
            mode = data.get("appearance_mode")
            if mode in ("Dark", "Light", "System"):
                ctk.set_appearance_mode(mode)
                if hasattr(self, 'theme_switch'):
                    self.theme_switch.set(mode)
        except Exception:
            pass

    def _save_window_state(self):
        """Persist current window geometry and appearance mode."""
        try:
            cfg_path = self._get_config_path()
            data = {
                "geometry": self.geometry(),
                "appearance_mode": ctk.get_appearance_mode()
            }
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _on_close(self):
        """Handle window closing cleanly."""
        self._save_window_state()
        sp.stop_playback()
        self.destroy()

    def run_on_ui_thread(self, callback):
        """Thread-safe dispatch of callbacks to Tkinter main event loop."""
        self._task_queue.put(callback)

    def _poll_ui_queue(self):
        """Process queued UI callbacks from worker threads."""
        try:
            while not self._task_queue.empty():
                try:
                    cb = self._task_queue.get_nowait()
                    cb()
                except Exception as e:
                    print(f"Error executing UI callback: {e}", file=sys.stderr)
        finally:
            self.after(25, self._poll_ui_queue)

    # ----------------------------------------------------------------------
    # Header & Status Bar Construction (UI Polish 4.5)
    # ----------------------------------------------------------------------

    def _build_header(self):
        """Constructs the top brand header, audio readiness badge, and theme switcher."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill='x', padx=16, pady=(10, 4))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="📡 MORSE SIGNAL LAB",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_lbl.pack(side='left')

        subtitle_lbl = ctk.CTkLabel(
            header_frame,
            text="CSE-220 • Signals & Systems Project",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_lbl.pack(side='left', padx=12, pady=(2, 0))

        # Audio status indicator badge
        sound_status = "● Audio Ready" if sp.SOUND_AVAILABLE else "○ Audio Muted"
        sound_color = "#10b981" if sp.SOUND_AVAILABLE else "#94a3b8"
        sound_lbl = ctk.CTkLabel(
            header_frame,
            text=sound_status,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=sound_color
        )
        sound_lbl.pack(side='left', padx=10, pady=(2, 0))

        # Theme Switcher
        self.theme_switch = ctk.CTkOptionMenu(
            header_frame,
            values=["Dark", "Light", "System"],
            width=90,
            command=self._change_appearance_mode
        )
        self.theme_switch.set("Dark")
        self.theme_switch.pack(side='right')

        theme_lbl = ctk.CTkLabel(header_frame, text="Theme:", font=ctk.CTkFont(size=12))
        theme_lbl.pack(side='right', padx=6)

    def _build_status_bar(self):
        """Constructs the bottom status bar with toast messages and busy indicator."""
        self.status_bar = ctk.CTkFrame(self, height=28, corner_radius=0, fg_color=("gray85", "gray17"))
        self.status_bar.pack(side='bottom', fill='x')

        # Left: Status indicator icon & message
        self.status_icon = ctk.CTkLabel(
            self.status_bar,
            text="●",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#10b981",
            width=16
        )
        self.status_icon.pack(side='left', padx=(10, 4), pady=3)

        self.status_msg = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color=("gray20", "gray80")
        )
        self.status_msg.pack(side='left', padx=2, pady=3)

        # Center/Right: Indeterminate busy progress bar (hidden when idle)
        self.busy_bar = ctk.CTkProgressBar(self.status_bar, width=130, height=8, mode="indeterminate")

        # Far Right: Status badge
        engine_lbl = ctk.CTkLabel(
            self.status_bar,
            text="DSP Engine Active",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        engine_lbl.pack(side='right', padx=12, pady=3)

    # ----------------------------------------------------------------------
    # Toast Notifications & Busy Indicator (UI Polish 4.1 & 4.5)
    # ----------------------------------------------------------------------

    def show_status(self, text: str, level: str = "info", duration_ms: int = 3500):
        """
        Display a non-blocking toast/status message in the bottom status bar.
        Levels: 'info', 'success', 'warning', 'error', 'busy', 'ready'
        """
        colors = {
            'info': ("#0284c7", "ℹ"),
            'success': ("#10b981", "✓"),
            'warning': ("#f59e0b", "⚠"),
            'error': ("#ef4444", "✖"),
            'ready': ("#10b981", "●"),
            'busy': ("#8b5cf6", "◌"),
        }
        color, icon = colors.get(level, ("#0284c7", "ℹ"))
        self.status_icon.configure(text=icon, text_color=color)
        self.status_msg.configure(text=text)

        if self._status_timer is not None:
            self.after_cancel(self._status_timer)
            self._status_timer = None

        if duration_ms > 0 and level not in ('busy', 'ready'):
            self._status_timer = self.after(duration_ms, self._reset_status)

    def set_busy(self, is_busy: bool, message: str = "Computing..."):
        """Toggle the busy indicator in the status bar for heavy computations."""
        if is_busy:
            self.show_status(message, level="busy", duration_ms=0)
            self.busy_bar.pack(side='right', padx=12, pady=8)
            self.busy_bar.start()
        else:
            self.busy_bar.stop()
            self.busy_bar.pack_forget()
            self.show_status("Ready", level="ready", duration_ms=0)

    def _reset_status(self):
        """Revert status bar to Ready state."""
        self.status_icon.configure(text="●", text_color="#10b981")
        self.status_msg.configure(text="Ready")
        self._status_timer = None

    # ----------------------------------------------------------------------
    # Theme & Clipboard Management (UI Polish 4.6 & 4.5)
    # ----------------------------------------------------------------------

    def _change_appearance_mode(self, new_mode: str):
        """Switch appearance mode (Dark, Light, System) and update all active plots and tables."""
        ctk.set_appearance_mode(new_mode)
        # UI Polish 4.6: Update Converter Tab reference table along with plots
        self.converter_tab.redraw()
        self.signal_tab.redraw()
        self.noise_tab.redraw()
        self.mic_tab.redraw()
        self.show_status(f"Appearance theme switched to {new_mode}", level="info", duration_ms=2500)

    def copy_to_clipboard(self, text: str, desc: str = "Copied to clipboard!"):
        """Safely copy text to OS clipboard and display non-blocking status confirmation."""
        if not text:
            self.show_status("Nothing to copy", level="warning")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.show_status(desc, level="success")


# Export symbols for backward compatibility
__all__ = [
    "MorseSignalLab",
    "ConverterTab",
    "SignalLabTab",
    "NoiseFilterTab",
    "MicDecodeTab",
    "get_plot_theme",
    "style_axis"
]


if __name__ == '__main__':
    app = MorseSignalLab()
    app.mainloop()