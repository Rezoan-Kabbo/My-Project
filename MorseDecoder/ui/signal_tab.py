"""
ui/signal_tab.py
----------------
Tab 2: Audio Synthesis & Frequency-Domain Analysis Laboratory.
Synthesizes sine-tone Morse audio, visualizes waveforms, computes FFT spectra
and Spectrograms, and exports audio to standard WAV files.
"""

import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from typing import TYPE_CHECKING, Optional
import numpy as np

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import morse_code as mc
import signal_proc as sp
from ui.theme import (
    get_plot_theme, style_axis,
    BTN_PRIMARY, BTN_PRIMARY_HOVER,
    BTN_PLAY, BTN_PLAY_HOVER,
    BTN_STOP, BTN_STOP_HOVER,
    BTN_SECONDARY, BTN_SECONDARY_HOVER, BTN_SECONDARY_TEXT,
    BTN_TRANSFER, BTN_TRANSFER_HOVER, BTN_TRANSFER_TEXT,
    BTN_HEIGHT_MD, BTN_HEIGHT_SM
)

if TYPE_CHECKING:
    from app import MorseSignalLab

SAMPLE_RATE_OPTIONS = ["8000", "16000", "22050", "44100"]


class SignalLabTab(ctk.CTkFrame):
    """Level 2: Signal generation, acoustic synthesis, FFT & Spectrogram visualization."""

    def __init__(self, parent: ctk.CTkBaseClass, app: "MorseSignalLab"):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.cbar = None
        self._is_generating = False
        self._is_playing = False
        self.pack(fill='both', expand=True, padx=4, pady=4)

        # 1. Top Morse Input Row
        self._build_input_row()

        # 2. Synthesis Parameters Card (Sliders & Sample Rate)
        self._build_parameters_card()

        # 3. Action Toolbar (Generate, Play, Stop, Export WAV, Send)
        self._build_action_toolbar()

        # 4. View Mode Switch & Stats Readout
        self._build_view_controls()

        # 5. Embedded Matplotlib Canvas
        self._build_plot_canvas()

        # Generate default initial signal
        self.generate()

    # ----------------------------------------------------------------------
    # UI Layout Construction
    # ----------------------------------------------------------------------

    def _build_input_row(self):
        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(fill='x', pady=(2, 6))

        ctk.CTkLabel(
            entry_frame,
            text="Morse Code Input:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side='left', padx=(0, 8))

        self.morse_var = ctk.StringVar(value=mc.text_to_morse("SOS"))
        self.morse_entry = ctk.CTkEntry(entry_frame, textvariable=self.morse_var, font=('Consolas', 12))
        self.morse_entry.pack(side='left', fill='x', expand=True)

    def _build_parameters_card(self):
        settings_card = ctk.CTkFrame(self, corner_radius=8)
        settings_card.pack(fill='x', pady=(0, 6), padx=2)

        self.freq_var = tk.DoubleVar(value=700)
        self.wpm_var = tk.DoubleVar(value=20)
        self.vol_var = tk.DoubleVar(value=70)
        self.sr_var = ctk.StringVar(value="44100")

        self._create_slider_row(settings_card, "Carrier Frequency (Hz):", self.freq_var, 200, 1500, 0, unit=" Hz")
        self._create_slider_row(settings_card, "Speed (WPM):", self.wpm_var, 5, 40, 1, unit=" WPM")
        self._create_slider_row(settings_card, "Volume (%):", self.vol_var, 0, 100, 2, unit=" %")

        # Sample Rate Option Menu
        sr_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        sr_frame.grid(row=3, column=0, columnspan=3, sticky='w', padx=12, pady=4)
        ctk.CTkLabel(sr_frame, text="Sample Rate:", font=ctk.CTkFont(size=12)).pack(side='left', padx=(0, 10))
        self.sr_menu = ctk.CTkOptionMenu(sr_frame, variable=self.sr_var, values=SAMPLE_RATE_OPTIONS, width=110)
        self.sr_menu.pack(side='left')

    def _create_slider_row(self, parent, label, var, from_, to, row, unit=""):
        parent.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).grid(row=row, column=0, sticky='w', padx=12, pady=3)

        val_lbl = ctk.CTkLabel(parent, text=f"{var.get():.0f}{unit}", width=70, font=ctk.CTkFont(size=12, weight="bold"))
        val_lbl.grid(row=row, column=2, sticky='e', padx=12, pady=3)

        def on_slide(val):
            val_lbl.configure(text=f"{val:.0f}{unit}")

        slider = ctk.CTkSlider(parent, from_=from_, to=to, variable=var, command=on_slide)
        slider.grid(row=row, column=1, sticky='ew', padx=8, pady=3)

    def _build_action_toolbar(self):
        # Row 1: Primary Processing & Audio Controls (Left) + View Mode Selector (Right)
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill='x', pady=(0, 4))

        left_ops = ctk.CTkFrame(row1, fg_color="transparent")
        left_ops.pack(side='left')

        self.generate_btn = ctk.CTkButton(
            left_ops,
            text="⚡ Generate Signal",
            width=135,
            height=BTN_HEIGHT_MD,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=BTN_PRIMARY,
            hover_color=BTN_PRIMARY_HOVER,
            command=self.generate
        )
        self.generate_btn.pack(side='left', padx=(0, 6))

        self.play_btn = ctk.CTkButton(
            left_ops,
            text="▶ Play",
            width=75,
            height=BTN_HEIGHT_MD,
            fg_color=BTN_PLAY,
            hover_color=BTN_PLAY_HOVER,
            command=self.play
        )
        self.play_btn.pack(side='left', padx=(0, 6))

        self.stop_btn = ctk.CTkButton(
            left_ops,
            text="■ Stop",
            width=65,
            height=BTN_HEIGHT_MD,
            fg_color=BTN_STOP,
            hover_color=BTN_STOP_HOVER,
            command=self.stop
        )
        self.stop_btn.pack(side='left', padx=(0, 6))

        self.export_btn = ctk.CTkButton(
            left_ops,
            text="💾 Export WAV...",
            width=115,
            height=BTN_HEIGHT_MD,
            fg_color=BTN_SECONDARY,
            hover_color=BTN_SECONDARY_HOVER,
            text_color=BTN_SECONDARY_TEXT,
            command=self.export_wav
        )
        self.export_btn.pack(side='left')

        # Right side of Row 1: Plot View Mode Segmented Button
        self.plot_mode = ctk.StringVar(value="Waveform")
        self.plot_seg = ctk.CTkSegmentedButton(
            row1,
            values=["Waveform", "FFT Spectrum", "Spectrogram"],
            variable=self.plot_mode,
            command=lambda _: self.redraw(),
            width=280
        )
        self.plot_seg.pack(side='right')

        # Row 2: Inter-Tab Data Flow Hub (Left) + Live Status (Right)
        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.pack(fill='x', pady=(0, 5))

        flow_box = ctk.CTkFrame(row2, fg_color="transparent")
        flow_box.pack(side='left')

        ctk.CTkLabel(
            flow_box,
            text="⇄ Data Flow:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        ).pack(side='left', padx=(2, 6))

        self.import_mic_btn = ctk.CTkButton(
            flow_box,
            text="📥 From Mic",
            width=105,
            height=BTN_HEIGHT_SM + 4,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BTN_TRANSFER,
            hover_color=BTN_TRANSFER_HOVER,
            text_color=BTN_TRANSFER_TEXT,
            command=self.import_from_mic
        )
        self.import_mic_btn.pack(side='left', padx=(0, 4))

        self.import_noise_btn = ctk.CTkButton(
            flow_box,
            text="📥 From Noise Lab",
            width=135,
            height=BTN_HEIGHT_SM + 4,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BTN_TRANSFER,
            hover_color=BTN_TRANSFER_HOVER,
            text_color=BTN_TRANSFER_TEXT,
            command=self.import_from_noise_lab
        )
        self.import_noise_btn.pack(side='left', padx=(0, 8))

        ctk.CTkLabel(
            flow_box,
            text="→",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        ).pack(side='left', padx=(0, 8))

        self.to_noise_btn = ctk.CTkButton(
            flow_box,
            text="To Noise Lab →",
            width=120,
            height=BTN_HEIGHT_SM + 4,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BTN_TRANSFER,
            hover_color=BTN_TRANSFER_HOVER,
            text_color=BTN_TRANSFER_TEXT,
            command=self.send_to_noise_lab
        )
        self.to_noise_btn.pack(side='left', padx=(0, 4))

        self.to_mic_btn = ctk.CTkButton(
            flow_box,
            text="To Mic Decoder →",
            width=130,
            height=BTN_HEIGHT_SM + 4,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BTN_TRANSFER,
            hover_color=BTN_TRANSFER_HOVER,
            text_color=BTN_TRANSFER_TEXT,
            command=self.send_to_mic_decode
        )
        self.to_mic_btn.pack(side='left')

        # Live info readout on right of Row 2
        self.info_var = ctk.StringVar(value="Ready. Click 'Generate Signal' to synthesize audio.")
        self.info_lbl = ctk.CTkLabel(
            row2,
            textvariable=self.info_var,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.info_lbl.pack(side='right', padx=4)

    def _build_view_controls(self):
        """Integrated into consolidated toolbar rows above."""
        pass

    def _build_plot_canvas(self):
        self.figure = Figure(figsize=(6, 3.2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, pady=(2, 4))

    # ----------------------------------------------------------------------
    # Event Handlers & Synthesis Operations (UI Polish 4.1 & 4.2)
    # ----------------------------------------------------------------------

    def set_morse_input(self, morse_str: str):
        """Set Morse entry string and trigger generation."""
        self.morse_var.set(morse_str)
        self.generate()

    def generate(self):
        """Synthesize waveform from the given Morse string in a background thread."""
        if self._is_generating:
            return

        morse = self.morse_var.get().strip()
        if not morse:
            self.app.show_status("Enter a Morse string first", level="warning")
            return

        freq = self.freq_var.get()
        wpm = self.wpm_var.get()
        amp = self.vol_var.get() / 100.0
        sr = int(self.sr_var.get())

        self._set_generating(True)
        self.app.set_busy(True, "Synthesizing Morse signal...")
        self.info_var.set("Synthesizing audio signal in background...")

        def _worker():
            try:
                sig = sp.morse_to_signal(morse, freq=freq, wpm=wpm, sample_rate=sr, amplitude=amp)
                self.app.run_on_ui_thread(lambda: self._on_generate_complete(sig, sr, morse, freq, wpm))
            except Exception as e:
                self.app.run_on_ui_thread(lambda: self._on_generate_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _set_generating(self, busy: bool):
        self._is_generating = busy
        state = "disabled" if busy else "normal"
        self.generate_btn.configure(state=state)
        self.play_btn.configure(state=state)
        self.export_btn.configure(state=state)

    def _on_generate_complete(self, sig: np.ndarray, sr: int, morse: str, freq: float, wpm: float):
        self.app.current_signal = sig
        self.app.current_sample_rate = sr
        self.app.current_morse = morse

        dur = len(sig) / sr if sr else 0.0
        dot_ms = (1.2 / wpm) * 1000.0
        dash_ms = dot_ms * 3.0
        self.info_var.set(
            f"{len(sig):,} samples • {dur:.2f}s • Dot: {dot_ms:.0f}ms • Dash: {dash_ms:.0f}ms • {freq:.0f} Hz @ {sr} Hz"
        )
        self.redraw()
        self._set_generating(False)
        self.app.set_busy(False)
        self.app.show_status(f"Signal synthesized: {len(sig):,} samples ({dur:.2f}s @ {freq:.0f} Hz)", level="success")

    def _on_generate_error(self, err_msg: str):
        self._set_generating(False)
        self.app.set_busy(False)
        self.info_var.set(f"Synthesis failed: {err_msg}")
        self.app.show_status(f"Synthesis error: {err_msg}", level="error")

    def _clear_colorbar(self):
        """Safely remove previous colorbar to avoid duplication across redraws."""
        if hasattr(self, 'cbar') and self.cbar is not None:
            try:
                self.cbar.remove()
            except Exception:
                pass
            self.cbar = None

    def redraw(self):
        """Render the selected plot mode (Waveform, FFT, or Spectrogram) with colorbar support."""
        colors = get_plot_theme()
        self.figure.patch.set_facecolor(colors['fig_bg'])
        self._clear_colorbar()
        self.ax.clear()

        sig = self.app.current_signal
        sr = self.app.current_sample_rate

        if len(sig) == 0:
            style_axis(self.ax, colors, title="No signal generated yet — click 'Generate Signal'")
            self.canvas.draw()
            return

        mode = self.plot_mode.get()

        if mode == "Waveform":
            max_points = 25000
            step = max(1, len(sig) // max_points)
            t = np.arange(0, len(sig), step) / sr
            self.ax.plot(t, sig[::step], linewidth=0.9, color=colors['clean'])
            style_axis(
                self.ax, colors,
                title="Time-Domain Synthesized Waveform",
                xlabel="Time (seconds)",
                ylabel="Amplitude"
            )

        elif mode == "FFT Spectrum":
            freqs, mag = sp.compute_fft(sig, sr)
            self.ax.plot(freqs, mag, linewidth=1.0, color=colors['fft'])
            carrier = self.freq_var.get()
            self.ax.axvline(carrier, color=colors['clean'], linestyle=':', linewidth=1.5, label=f'Carrier ({carrier:.0f} Hz)')
            self.ax.set_xlim(0, min(3000, sr / 2.0))
            self.ax.legend(loc='upper right', fontsize=8)
            style_axis(
                self.ax, colors,
                title="Frequency Spectrum (FFT)",
                xlabel="Frequency (Hz)",
                ylabel="Magnitude"
            )

        else:
            # Time-Frequency Spectrogram with Colorbar (UI Polish 4.2)
            f, t, sxx = sp.compute_spectrogram(sig, sr)
            if len(f) > 0 and len(t) > 0:
                mesh = self.ax.pcolormesh(t, f, sxx, shading='gouraud', cmap='viridis')
                self.ax.set_ylim(0, min(3000, sr / 2.0))
                style_axis(
                    self.ax, colors,
                    title="Time-Frequency Spectrogram (dB)",
                    xlabel="Time (seconds)",
                    ylabel="Frequency (Hz)"
                )
                self.cbar = self.figure.colorbar(mesh, ax=self.ax, pad=0.02, aspect=18)
                self.cbar.set_label("Power (dB)", color=colors['text'], fontsize=8)
                self.cbar.ax.tick_params(colors=colors['text'], labelsize=7)
                for spine in self.cbar.ax.spines.values():
                    spine.set_color(colors['spine'])

        self.figure.tight_layout()
        self.canvas.draw()

    def toggle_playback(self):
        """Toggle playback of synthesized signal."""
        if getattr(self, '_is_playing', False):
            self.stop()
        else:
            self.play()

    def play(self):
        """Play the synthesized waveform through sound hardware."""
        if len(self.app.current_signal) == 0:
            self.app.show_status("Nothing to play — generate a signal first", level="warning")
            return
        try:
            sp.play_signal(self.app.current_signal, self.app.current_sample_rate)
            self._is_playing = True
            dur = len(self.app.current_signal) / float(self.app.current_sample_rate)
            self.app.show_status(f"Playing synthesized audio ({dur:.2f}s)...", level="info")
            self.after(int(dur * 1000) + 100, lambda: setattr(self, '_is_playing', False))
        except RuntimeError as e:
            self.app.show_status(f"Playback error: {e}", level="error")

    def stop(self):
        """Halt audio playback."""
        sp.stop_playback()
        self._is_playing = False
        self.app.show_status("Audio playback stopped", level="info")

    def export_wav(self):
        """Save the synthesized audio as a standard 16-bit WAV file without blocking dialogs."""
        if len(self.app.current_signal) == 0:
            self.app.show_status("Nothing to export — generate a signal first", level="warning")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV Audio", "*.wav")],
            initialfile="synthesized_morse.wav"
        )
        if not path:
            return
        try:
            sp.save_wav(path, self.app.current_signal, self.app.current_sample_rate)
            self.app.show_status(f"WAV saved successfully: {Path(path).name}", level="success", duration_ms=4500)
        except Exception as e:
            self.app.show_status(f"Failed to save WAV: {e}", level="error")

    def send_to_noise_lab(self):
        """Route current clean signal to Tab 3 (Noise Lab)."""
        if len(self.app.current_signal) == 0:
            self.generate()
        self.app.noise_tab.load_clean_signal()
        self.app.tabview.set("3. Noise & Filter")
        self.app.show_status("Signal routed to Noise Lab (bandwidth synced to ~30% carrier)", level="info")

    def send_to_mic_decode(self):
        """Route current signal to Tab 4 (Mic / Audio Decoder)."""
        if len(self.app.current_signal) == 0:
            self.generate()
        self.app.mic_tab.load_audio_data(
            self.app.current_signal,
            self.app.current_sample_rate,
            source_name="Signal Lab (Synthesized)"
        )
        self.app.tabview.set("4. Mic & Audio Decode")
        self.app.show_status("Signal routed to Audio Decoder", level="info")

    def load_external_audio(self, audio: np.ndarray, sr: int, source_name: str = "External Audio"):
        """Load an external audio signal for visual analysis (waveform/FFT/spectrogram)."""
        self.app.current_signal = audio
        self.app.current_sample_rate = sr
        dur = len(audio) / sr if sr else 0.0
        carrier = sp.detect_carrier_frequency(audio, sr)
        self.freq_var.set(carrier)
        self.info_var.set(
            f"Imported {source_name}: {len(audio):,} samples • {dur:.2f}s • Carrier: {carrier:.0f} Hz @ {sr} Hz"
        )
        self.redraw()
        self.app.show_status(
            f"Loaded {source_name} ({len(audio):,} samples, {dur:.2f}s)",
            level="success"
        )

    def import_from_mic(self):
        """Pull recorded audio from Mic tab for visual analysis."""
        audio = self.app.recorded_signal
        sr = self.app.recorded_sample_rate or 44100
        if len(audio) == 0:
            self.app.show_status("No mic recording available — record or load audio in Mic tab first", level="warning")
            return
        self.load_external_audio(audio, sr, source_name="Mic Recording")

    def import_from_noise_lab(self):
        """Pull filtered audio from Noise Lab for visual analysis."""
        filtered = self.app.filtered_signal
        sr = self.app.current_sample_rate or 44100
        if len(filtered) == 0:
            self.app.show_status("No filtered signal available — apply filter in Noise Lab first", level="warning")
            return
        self.load_external_audio(filtered, sr, source_name="Noise Lab (Filtered)")
