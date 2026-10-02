"""
ui/noise_tab.py
---------------
Tab 3: Channel Noise Injection & Butterworth Band-pass Filter Laboratory.
Simulates real communication impairments (AWGN, 60Hz mains hum, clicks),
applies Butterworth zero-phase filtering, displays theoretical frequency response |H(f)|,
and verifies demodulation recovery against the original transmission.
"""

import threading
import tkinter as tk
from typing import TYPE_CHECKING
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
    BTN_WARN, BTN_WARN_HOVER,
    BTN_HEIGHT_MD, BTN_HEIGHT_SM
)

if TYPE_CHECKING:
    from app import MorseSignalLab


class NoiseFilterTab(ctk.CTkFrame):
    """Level 3: Channel noise simulation, bandpass filtering, and error analysis."""

    def __init__(self, parent: ctk.CTkBaseClass, app: "MorseSignalLab"):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._is_filtering = False
        self._is_playing = False
        self.pack(fill='both', expand=True, padx=4, pady=4)

        # 1. Header Information Row
        self._build_header_row()

        # 2. Control Card: Noise & Filter Parameters
        self._build_control_card()

        # 3. Action Toolbar (Add Noise, Apply Filter, Audition Playback)
        self._build_action_toolbar()

        # 4. Plot Mode Segmented Switch
        self._build_view_controls()

        # 5. Dual Matplotlib Canvases
        self._build_plot_canvases()

    # ----------------------------------------------------------------------
    # UI Layout Construction
    # ----------------------------------------------------------------------

    def _build_header_row(self):
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill='x', pady=(2, 6))

        ctk.CTkLabel(
            header_row,
            text="Channel Noise Simulation & Butterworth Band-pass Filtering",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side='left')

        self.status_lbl = ctk.CTkLabel(
            header_row,
            text="Ready. Uses synthesized signal from Signal Lab.",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_lbl.pack(side='right')

    def _build_control_card(self):
        card = ctk.CTkFrame(self, corner_radius=8)
        card.pack(fill='x', pady=(0, 6), padx=2)
        card.grid_columnconfigure(1, weight=1)

        # Channel SNR Slider
        self.snr_var = tk.DoubleVar(value=8)
        ctk.CTkLabel(card, text="Channel SNR (dB):", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky='w', padx=12, pady=4)
        self.snr_val_lbl = ctk.CTkLabel(card, text="8 dB", width=65, font=ctk.CTkFont(size=12, weight="bold"))
        self.snr_val_lbl.grid(row=0, column=2, sticky='e', padx=12, pady=4)
        self.snr_slider = ctk.CTkSlider(
            card, from_=-10, to=30, variable=self.snr_var,
            command=lambda v: self.snr_val_lbl.configure(text=f"{v:.0f} dB")
        )
        self.snr_slider.grid(row=0, column=1, sticky='ew', padx=8, pady=4)

        # Noise Model Options
        self.noise_type_var = ctk.StringVar(value="White Gaussian (AWGN)")
        noise_row = ctk.CTkFrame(card, fg_color="transparent")
        noise_row.grid(row=1, column=0, columnspan=3, sticky='w', padx=12, pady=2)
        ctk.CTkLabel(noise_row, text="Noise Model:", font=ctk.CTkFont(size=12)).pack(side='left', padx=(0, 10))
        ctk.CTkOptionMenu(
            noise_row,
            variable=self.noise_type_var,
            values=["White Gaussian (AWGN)", "60Hz Mains Hum + Noise", "Acoustic Clicks + Noise"],
            width=230
        ).pack(side='left')

        # Carrier Frequency Slider (local to Noise Lab — auto-synced or manually adjustable)
        self.carrier_freq_var = tk.DoubleVar(value=700)
        ctk.CTkLabel(card, text="Carrier Frequency (Hz):", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky='w', padx=12, pady=4)
        self.carrier_val_lbl = ctk.CTkLabel(card, text="700 Hz", width=65, font=ctk.CTkFont(size=12, weight="bold"))
        self.carrier_val_lbl.grid(row=2, column=2, sticky='e', padx=12, pady=4)
        self.carrier_slider = ctk.CTkSlider(
            card, from_=200, to=2000, variable=self.carrier_freq_var,
            command=lambda v: self.carrier_val_lbl.configure(text=f"{v:.0f} Hz")
        )
        self.carrier_slider.grid(row=2, column=1, sticky='ew', padx=8, pady=4)

        # Filter Bandwidth Slider (UI Polish 4.7: stored as instance variable for programmatic sync)
        self.bw_var = tk.DoubleVar(value=200)
        ctk.CTkLabel(card, text="Filter Bandwidth (Hz):", font=ctk.CTkFont(size=12)).grid(row=3, column=0, sticky='w', padx=12, pady=4)
        self.bw_val_lbl = ctk.CTkLabel(card, text="200 Hz", width=65, font=ctk.CTkFont(size=12, weight="bold"))
        self.bw_val_lbl.grid(row=3, column=2, sticky='e', padx=12, pady=4)
        self.bw_slider = ctk.CTkSlider(
            card, from_=50, to=600, variable=self.bw_var,
            command=lambda v: self.bw_val_lbl.configure(text=f"{v:.0f} Hz")
        )
        self.bw_slider.grid(row=3, column=1, sticky='ew', padx=8, pady=4)

        # Filter Order Menu
        self.order_var = ctk.StringVar(value="4th Order")
        order_row = ctk.CTkFrame(card, fg_color="transparent")
        order_row.grid(row=4, column=0, columnspan=3, sticky='w', padx=12, pady=3)
        ctk.CTkLabel(order_row, text="Filter Order:", font=ctk.CTkFont(size=12)).pack(side='left', padx=(0, 10))
        ctk.CTkOptionMenu(
            order_row,
            variable=self.order_var,
            values=["2nd Order", "4th Order", "6th Order"],
            width=120,
            command=lambda _: self.apply_filter()
        ).pack(side='left')

    def _build_action_toolbar(self):
        # Row 1: Processing Pipeline (Left) + Unified Audition Player (Right)
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill='x', pady=(0, 4))

        pipeline_box = ctk.CTkFrame(row1, fg_color="transparent")
        pipeline_box.pack(side='left')

        self.add_noise_btn = ctk.CTkButton(
            pipeline_box,
            text="1. Add Noise",
            width=110,
            height=BTN_HEIGHT_MD,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BTN_WARN,
            hover_color=BTN_WARN_HOVER,
            command=self.add_noise
        )
        self.add_noise_btn.pack(side='left', padx=(0, 6))

        self.apply_filter_btn = ctk.CTkButton(
            pipeline_box,
            text="2. Apply Filter",
            width=115,
            height=BTN_HEIGHT_MD,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BTN_PRIMARY,
            hover_color=BTN_PRIMARY_HOVER,
            command=self.apply_filter
        )
        self.apply_filter_btn.pack(side='left', padx=(0, 6))

        self.decode_btn = ctk.CTkButton(
            pipeline_box,
            text="3. Decode to Text",
            width=125,
            height=BTN_HEIGHT_MD,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BTN_PLAY,
            hover_color=BTN_PLAY_HOVER,
            command=self.decode_filtered
        )
        self.decode_btn.pack(side='left')

        # Right of Row 1: Audition controls
        audition_box = ctk.CTkFrame(row1, fg_color="transparent")
        audition_box.pack(side='right')

        ctk.CTkLabel(
            audition_box,
            text="Audition:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        ).pack(side='left', padx=(0, 6))

        ctk.CTkButton(
            audition_box,
            text="▶ Clean",
            width=65,
            height=BTN_HEIGHT_MD,
            fg_color=BTN_SECONDARY,
            hover_color=BTN_SECONDARY_HOVER,
            text_color=BTN_SECONDARY_TEXT,
            command=lambda: self._play(self.app.current_signal, "Clean")
        ).pack(side='left', padx=(0, 4))

        ctk.CTkButton(
            audition_box,
            text="▶ Noisy",
            width=65,
            height=BTN_HEIGHT_MD,
            fg_color=BTN_SECONDARY,
            hover_color=BTN_SECONDARY_HOVER,
            text_color=BTN_SECONDARY_TEXT,
            command=lambda: self._play(self.app.noisy_signal, "Noisy")
        ).pack(side='left', padx=(0, 4))

        ctk.CTkButton(
            audition_box,
            text="▶ Filtered",
            width=75,
            height=BTN_HEIGHT_MD,
            fg_color=BTN_SECONDARY,
            hover_color=BTN_SECONDARY_HOVER,
            text_color=BTN_SECONDARY_TEXT,
            command=lambda: self._play(self.app.filtered_signal, "Filtered")
        ).pack(side='left', padx=(0, 6))

        ctk.CTkButton(
            audition_box,
            text="■ Stop",
            width=60,
            height=BTN_HEIGHT_MD,
            fg_color=BTN_STOP,
            hover_color=BTN_STOP_HOVER,
            command=sp.stop_playback
        ).pack(side='left')

        # Row 2: Inter-Tab Routing (Left) + View Mode Switch (Right)
        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.pack(fill='x', pady=(0, 5))

        route_box = ctk.CTkFrame(row2, fg_color="transparent")
        route_box.pack(side='left')

        ctk.CTkLabel(
            route_box,
            text="⇄ Data Flow:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        ).pack(side='left', padx=(2, 6))

        ctk.CTkButton(
            route_box,
            text="📥 From Mic",
            width=105,
            height=BTN_HEIGHT_SM + 4,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BTN_TRANSFER,
            hover_color=BTN_TRANSFER_HOVER,
            text_color=BTN_TRANSFER_TEXT,
            command=self.import_from_mic
        ).pack(side='left', padx=(0, 4))

        ctk.CTkButton(
            route_box,
            text="Send Decoded → Converter",
            width=180,
            height=BTN_HEIGHT_SM + 4,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BTN_TRANSFER,
            hover_color=BTN_TRANSFER_HOVER,
            text_color=BTN_TRANSFER_TEXT,
            command=self.send_decoded_to_converter
        ).pack(side='left', padx=(0, 4))

        ctk.CTkButton(
            route_box,
            text="To Mic Decoder →",
            width=135,
            height=BTN_HEIGHT_SM + 4,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BTN_TRANSFER,
            hover_color=BTN_TRANSFER_HOVER,
            text_color=BTN_TRANSFER_TEXT,
            command=self.send_to_mic_decode
        ).pack(side='left')

        # Right of Row 2: Plot View Selector
        self.plot_type_var = ctk.StringVar(value="Time Domain (Waveforms)")
        ctk.CTkSegmentedButton(
            row2,
            values=["Time Domain (Waveforms)", "FFT & Filter Response |H(f)|"],
            variable=self.plot_type_var,
            command=lambda _: self.redraw(),
            width=340
        ).pack(side='right')

    def _build_view_controls(self):
        """Integrated into consolidated toolbar rows above."""
        pass

    def _build_plot_canvases(self):
        self.figure = Figure(figsize=(6, 3.6), dpi=100)
        self.ax_before = self.figure.add_subplot(211)
        self.ax_after = self.figure.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, pady=(2, 4))
        self.redraw()

    # ----------------------------------------------------------------------
    # Event Handlers & Filtering Operations (UI Polish 4.1 & 4.7)
    # ----------------------------------------------------------------------

    def _get_carrier_freq(self) -> float:
        """Return the local carrier frequency setting for filtering."""
        return self.carrier_freq_var.get()

    def _set_carrier_freq(self, freq: float):
        """Set the local carrier frequency slider and label."""
        clamped = max(200, min(2000, freq))
        self.carrier_freq_var.set(clamped)
        if hasattr(self, 'carrier_slider'):
            self.carrier_slider.set(clamped)
        if hasattr(self, 'carrier_val_lbl'):
            self.carrier_val_lbl.configure(text=f"{clamped:.0f} Hz")

    def sync_bandwidth_to_carrier(self, carrier_freq: float):
        """Auto-adjust filter bandwidth to ~30% of the carrier frequency (UI Polish 4.7)."""
        target_bw = float(max(50, min(600, int(round(carrier_freq * 0.30 / 10.0) * 10))))
        self.bw_var.set(target_bw)
        if hasattr(self, 'bw_slider'):
            self.bw_slider.set(target_bw)
        if hasattr(self, 'bw_val_lbl'):
            self.bw_val_lbl.configure(text=f"{target_bw:.0f} Hz")

    def load_clean_signal(self):
        """Called when a clean signal is transmitted from Signal Lab."""
        sig = self.app.current_signal
        sr = self.app.current_sample_rate
        carrier = self.app.signal_tab.freq_var.get()
        self._set_carrier_freq(carrier)
        self.sync_bandwidth_to_carrier(carrier)
        self.status_lbl.configure(
            text=f"Loaded from Signal Lab: {len(sig):,} samples @ {sr} Hz (carrier {carrier:.0f} Hz, BW synced to {self.bw_var.get():.0f} Hz)."
        )
        self.add_noise()

    def load_external_noisy_audio(self, audio: np.ndarray, sr: int, source_name: str = "External Audio"):
        """
        Accept pre-recorded noisy audio (e.g., from Mic tab) for filtering.
        Bypasses synthetic noise injection — the audio IS the noisy signal.
        Auto-detects carrier frequency via Welch PSD and syncs filter bandwidth.
        """
        # Preprocess: remove DC offset, high-pass filter, normalize
        cleaned = sp.preprocess_mic_audio(audio, sr)
        self.app.noisy_signal = cleaned
        self.app.current_sample_rate = sr

        # Auto-detect carrier frequency from the noisy audio
        detected_freq = sp.detect_carrier_frequency(cleaned, sr)
        self._set_carrier_freq(detected_freq)
        self.sync_bandwidth_to_carrier(detected_freq)

        self.status_lbl.configure(
            text=f"Loaded {source_name}: {len(cleaned):,} samples @ {sr} Hz • Carrier detected: {detected_freq:.0f} Hz"
        )
        self.app.show_status(
            f"Noisy audio loaded into Noise Lab (carrier: {detected_freq:.0f} Hz, BW: {self.bw_var.get():.0f} Hz)",
            level="info"
        )
        self.apply_filter()

    def import_from_mic(self):
        """Pull recorded audio from Mic tab into Noise Lab for filtering."""
        audio = self.app.recorded_signal
        sr = self.app.recorded_sample_rate or 44100
        if len(audio) == 0:
            self.app.show_status("No mic recording available — record or load audio in Mic tab first", level="warning")
            return
        self.load_external_noisy_audio(audio, sr, source_name="Mic Recording")

    def add_noise(self):
        """Inject target noise model into the clean signal."""
        clean = self.app.current_signal
        if len(clean) == 0:
            self.app.signal_tab.generate()
            clean = self.app.current_signal

        snr = self.snr_var.get()
        model_str = self.noise_type_var.get()
        ntype = 'white'
        if 'Hum' in model_str:
            ntype = 'hum'
        elif 'Clicks' in model_str:
            ntype = 'clicks'

        noisy = sp.add_noise(clean, snr_db=snr, noise_type=ntype)
        self.app.noisy_signal = noisy
        self.status_lbl.configure(text=f"Injected {model_str} at {snr:.0f} dB SNR. Ready to filter.")
        self.app.show_status(f"Noise injected ({model_str} @ {snr:.0f} dB SNR)", level="info")
        self.apply_filter()

    def _set_filtering(self, busy: bool):
        self._is_filtering = busy
        state = "disabled" if busy else "normal"
        self.apply_filter_btn.configure(state=state)
        self.add_noise_btn.configure(state=state)
        self.decode_btn.configure(state=state)

    def apply_filter(self):
        """Filter the noisy signal using Butterworth band-pass filter in background (UI Polish 4.1)."""
        if self._is_filtering:
            return

        noisy = self.app.noisy_signal
        if len(noisy) == 0:
            self.add_noise()
            noisy = self.app.noisy_signal

        freq = self._get_carrier_freq()
        bw = self.bw_var.get()
        sr = self.app.current_sample_rate
        order = int(self.order_var.get().split()[0].replace('nd', '').replace('th', ''))

        self._set_filtering(True)
        self.app.set_busy(True, "Applying Butterworth band-pass filter...")
        self.status_lbl.configure(text="Filtering signal in background...")

        def _worker():
            try:
                filtered = sp.bandpass_filter(noisy, freq, sr, bandwidth=bw, order=order)
                snr_est = sp.estimate_snr_db(self.app.current_signal, self.app.noisy_signal)
                self.app.run_on_ui_thread(lambda: self._on_filter_complete(filtered, freq, bw, order, snr_est))
            except Exception as e:
                self.app.run_on_ui_thread(lambda: self._on_filter_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_filter_complete(self, filtered: np.ndarray, freq: float, bw: float, order: int, snr_est: float):
        self.app.filtered_signal = filtered
        self.status_lbl.configure(
            text=f"Filtered ±{bw/2:.0f} Hz around {freq:.0f} Hz ({order}th order). Input SNR ~ {snr_est:.1f} dB."
        )
        self.redraw()
        self._set_filtering(False)
        self.app.set_busy(False)
        self.app.show_status(f"Band-pass filter applied (±{bw/2:.0f} Hz around {freq:.0f} Hz)", level="success")

    def _on_filter_error(self, err_msg: str):
        self._set_filtering(False)
        self.app.set_busy(False)
        self.status_lbl.configure(text=f"Filter error: {err_msg}")
        self.app.show_status(f"Filter error: {err_msg}", level="error")

    def redraw(self):
        """Redraw either Time Domain waveforms or FFT spectra with |H(f)| curve."""
        colors = get_plot_theme()
        self.figure.patch.set_facecolor(colors['fig_bg'])
        self.ax_before.clear()
        self.ax_after.clear()

        sr = self.app.current_sample_rate or 44100
        noisy = self.app.noisy_signal
        filtered = self.app.filtered_signal
        plot_type = self.plot_type_var.get()
        freq = self._get_carrier_freq()
        bw = self.bw_var.get()
        order = int(self.order_var.get().split()[0].replace('nd', '').replace('th', ''))

        if "Time Domain" in plot_type:
            if len(noisy) > 0:
                step = max(1, len(noisy) // 20000)
                t = np.arange(0, len(noisy), step) / sr
                self.ax_before.plot(t, noisy[::step], linewidth=0.7, color=colors['noisy'])
                style_axis(self.ax_before, colors, title=f"1. Noisy Signal ({self.noise_type_var.get()} @ {self.snr_var.get():.0f} dB SNR)", ylabel="Amp")
            else:
                style_axis(self.ax_before, colors, title="Noisy Signal (Click '1. Add Noise')", ylabel="Amp")

            if len(filtered) > 0:
                step = max(1, len(filtered) // 20000)
                t = np.arange(0, len(filtered), step) / sr
                self.ax_after.plot(t, filtered[::step], linewidth=0.7, color=colors['filtered'])
                style_axis(self.ax_after, colors, title=f"2. Filtered Signal (Butterworth Band-pass: {freq:.0f} ± {bw/2:.0f} Hz)", xlabel="Time (s)", ylabel="Amp")
            else:
                style_axis(self.ax_after, colors, title="Filtered Signal (Click '2. Apply Filter')", xlabel="Time (s)", ylabel="Amp")

        else:
            # Frequency Spectrum (FFT) and theoretical filter response |H(f)|
            if len(noisy) > 0:
                f_noisy, mag_noisy = sp.compute_fft(noisy, sr)
                self.ax_before.plot(f_noisy, mag_noisy, linewidth=0.9, color=colors['noisy'])
                self.ax_before.set_xlim(0, min(3000, sr / 2.0))
                style_axis(self.ax_before, colors, title="Noisy Signal Spectrum (FFT)", ylabel="Magnitude")

            if len(filtered) > 0:
                f_filt, mag_filt = sp.compute_fft(filtered, sr)
                self.ax_after.plot(f_filt, mag_filt, linewidth=0.9, color=colors['filtered'], label='Filtered Spectrum')

                # Overlay theoretical Butterworth frequency response |H(f)|
                w, h_mag = sp.filter_frequency_response(freq, sr, bandwidth=bw, order=order, num_points=1024)
                if len(w) > 0 and len(mag_filt) > 0:
                    peak_mag = np.max(mag_filt) if np.max(mag_filt) > 0 else 1.0
                    h_scaled = h_mag * peak_mag
                    self.ax_after.plot(w, h_scaled, linewidth=1.5, linestyle='--', color=colors['response'], label=f'|H(f)| Filter Passband')

                self.ax_after.set_xlim(0, min(3000, sr / 2.0))
                self.ax_after.legend(loc='upper right', fontsize=8)
                style_axis(self.ax_after, colors, title=f"Filtered Spectrum vs Butterworth Response |H(f)| ({order}th order)", xlabel="Frequency (Hz)", ylabel="Magnitude")

        self.figure.tight_layout()
        self.canvas.draw()

    def decode_filtered(self):
        """Demodulate the filtered audio in background (UI Polish 4.1 & 4.5)."""
        filtered = self.app.filtered_signal
        if len(filtered) == 0:
            self.app.show_status("No filtered signal — add noise & filter first", level="warning")
            return

        sr = self.app.current_sample_rate
        carrier = self._get_carrier_freq()
        self.app.set_busy(True, "Decoding filtered Morse signal...")

        def _worker():
            try:
                morse, details = sp.decode_signal_to_morse(filtered, sr, carrier_freq=carrier, return_details=True)
                self.app.run_on_ui_thread(lambda: self._on_decode_filtered_complete(morse, details))
            except Exception as e:
                self.app.run_on_ui_thread(lambda: self.app.show_status(f"Decode error: {e}", level="error"))
            finally:
                self.app.run_on_ui_thread(lambda: self.app.set_busy(False))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_decode_filtered_complete(self, morse: str, details: dict):
        text = mc.morse_to_text(morse) if morse else ""
        orig_morse = getattr(self.app, 'current_morse', '')
        orig_text = mc.morse_to_text(orig_morse)

        accuracy_str = "100% Exact match!" if text == orig_text else f"Expected: '{orig_text}'"
        speed = details.get('wpm', 0)
        self.status_lbl.configure(text=f"Decoded: '{text}' ({speed:.1f} WPM) • {accuracy_str}")
        self.app.show_status(f"Decoded: '{text}' ({speed:.1f} WPM) • {accuracy_str}", level="success", duration_ms=5000)

    def send_to_mic_decode(self):
        """Route filtered signal to Tab 4 (Mic / Audio Decoder)."""
        filtered = self.app.filtered_signal
        if len(filtered) == 0:
            self.apply_filter()
            filtered = self.app.filtered_signal
        self.app.mic_tab.load_audio_data(
            filtered,
            self.app.current_sample_rate,
            source_name="Noise Lab (Filtered Audio)"
        )
        self.app.tabview.set("4. Mic & Audio Decode")
        self.app.show_status("Filtered audio routed to Audio Decoder", level="info")

    def send_decoded_to_converter(self):
        """Route the last decoded filtered text to the Converter tab."""
        status_text = self.status_lbl.cget('text')
        # Extract decoded text from status label (format: "Decoded: 'TEXT' (...)")
        import re
        match = re.search(r"Decoded:\s*'([^']*)'", status_text)
        if match:
            decoded = match.group(1)
            self.app.converter_tab.load_text_or_morse(decoded, is_morse=False)
            self.app.tabview.set("1. Converter")
            self.app.show_status(f"Decoded text '{decoded}' sent to Converter", level="success")
        else:
            self.app.show_status("No decoded text available — decode filtered signal first", level="warning")

    def toggle_playback(self):
        """Toggle playback of filtered signal."""
        if getattr(self, '_is_playing', False):
            sp.stop_playback()
            self._is_playing = False
            self.app.show_status("Audio playback stopped", level="info")
        else:
            self._play(self.app.filtered_signal, "Filtered")

    def _play(self, data: np.ndarray, label: str = "Audio"):
        """Audition signal playback without blocking dialogs."""
        if len(data) == 0:
            self.app.show_status(f"Nothing to play — generate {label.lower()} signal first", level="warning")
            return
        try:
            sp.play_signal(data, self.app.current_sample_rate)
            self._is_playing = True
            dur = len(data) / float(self.app.current_sample_rate)
            self.app.show_status(f"Playing {label} signal ({dur:.2f}s)...", level="info")
            self.after(int(dur * 1000) + 100, lambda: setattr(self, '_is_playing', False))
        except RuntimeError as e:
            self.app.show_status(f"Playback error: {e}", level="error")
