"""
signal_proc.py
---------------
All the actual "signal processing" for the project:

  * Morse string  -> audio waveform (sine-tone synthesis)
  * waveform      -> playback / recording (sounddevice)
  * waveform      -> WAV file save / load (scipy.io.wavfile)
  * waveform      -> frequency spectrum (FFT) & Spectrogram
  * waveform      -> carrier frequency detection (Welch PSD)
  * waveform      -> noisy waveform (AWGN, 60Hz hum, acoustic clicks)
  * noisy waveform -> filtered waveform (Butterworth band-pass)
  * waveform      -> Morse string (robust Hilbert envelope + Otsu adaptive
                     thresholding + debouncing + timing clustering)

Kept independent of tkinter so it can be unit tested or reused in a
notebook / CLI script.
"""

import numpy as np
from scipy import signal as sp_signal
import scipy.io.wavfile as wavfile

try:
    import sounddevice as sd
    SOUND_AVAILABLE = True
except Exception:  # pragma: no cover - environment without audio hardware
    SOUND_AVAILABLE = False


# --------------------------------------------------------------------------
# 1. Morse -> signal (synthesis)
# --------------------------------------------------------------------------

def dot_duration(wpm: float) -> float:
    """
    Standard PARIS timing formula: one dot ("unit") lasts 1.2/wpm seconds.
    A dash = 3 units, intra-letter gap = 1 unit,
    inter-letter gap = 3 units, inter-word gap = 7 units.
    """
    return 1.2 / max(float(wpm), 1e-6)


def _tone(duration, freq, sample_rate, amplitude):
    """One continuous sine tone, with a short fade in/out to avoid clicks."""
    n = max(int(round(sample_rate * duration)), 1)
    t = np.arange(n) / sample_rate
    wave = amplitude * np.sin(2 * np.pi * freq * t)

    fade_len = min(int(0.005 * sample_rate), n // 2)  # 5 ms fade
    if fade_len > 1:
        fade = np.linspace(0.0, 1.0, fade_len)
        wave[:fade_len] *= fade
        wave[-fade_len:] *= fade[::-1]
    return wave


def _silence(duration, sample_rate):
    n = max(int(round(sample_rate * duration)), 0)
    return np.zeros(n, dtype=float)


def morse_to_signal(morse_code: str, freq=700.0, wpm=20.0,
                    sample_rate=44100, amplitude=0.7):
    """
    Turn a Morse string (as produced by morse_code.text_to_morse) into a
    1-D numpy float array representing the audio waveform.
    """
    unit = dot_duration(wpm)
    words = [w for w in morse_code.strip().split(' / ') if w != '']
    chunks = []

    for wi, word in enumerate(words):
        letters = [l for l in word.strip().split(' ') if l != '']
        for li, letter in enumerate(letters):
            for si, symbol in enumerate(letter):
                if symbol == '.':
                    chunks.append(_tone(unit, freq, sample_rate, amplitude))
                elif symbol == '-':
                    chunks.append(_tone(unit * 3, freq, sample_rate, amplitude))
                else:
                    continue  # unknown symbol ('?') -> skip silently
                if si < len(letter) - 1:
                    chunks.append(_silence(unit, sample_rate))       # intra-letter
            if li < len(letters) - 1:
                chunks.append(_silence(unit * 3, sample_rate))       # inter-letter
        if wi < len(words) - 1:
            chunks.append(_silence(unit * 7, sample_rate))           # inter-word

    if not chunks:
        return np.array([], dtype=float)
    return np.concatenate(chunks)


# --------------------------------------------------------------------------
# 2. Playback / recording / WAV I/O
# --------------------------------------------------------------------------

def play_signal(data, sample_rate=44100, blocking=False):
    """Play a waveform through the default output device."""
    if not SOUND_AVAILABLE:
        raise RuntimeError("No audio output device available (sounddevice).")
    if len(data) == 0:
        return
    # Clamp to avoid audio driver clipping distortion
    clipped = np.clip(data, -1.0, 1.0)
    sd.play(clipped, sample_rate)
    if blocking:
        sd.wait()


def stop_playback():
    """Stop any currently playing audio."""
    if SOUND_AVAILABLE:
        sd.stop()


def get_input_devices():
    """Return a list of (index, device_name) for available audio input devices."""
    if not SOUND_AVAILABLE:
        return []
    try:
        devices = sd.query_devices()
        return [(i, d['name']) for i, d in enumerate(devices) if d.get('max_input_channels', 0) > 0]
    except Exception:
        return []


def record_audio(duration, sample_rate=44100, device=None):
    """Record `duration` seconds of mono audio from default mic or specified device index."""
    if not SOUND_AVAILABLE:
        raise RuntimeError("No audio input device available (sounddevice).")
    num_samples = max(int(round(duration * sample_rate)), 1)
    audio = sd.rec(num_samples, samplerate=sample_rate, channels=1, dtype='float64', device=device)
    sd.wait()
    return audio.flatten()


def preprocess_mic_audio(audio: np.ndarray, sample_rate: int = 44100) -> np.ndarray:
    """
    Clean raw microphone audio before further processing:
      1. Remove DC offset (mean subtraction)
      2. Apply gentle high-pass filter (>50 Hz) to remove low-frequency rumble
      3. Normalize amplitude safely to [-0.95, 0.95]
    """
    if len(audio) == 0:
        return audio
    # 1. DC offset removal
    cleaned = audio - np.mean(audio)
    # 2. High-pass filter at 50 Hz to remove power-line rumble and mic drift
    try:
        nyq = sample_rate / 2.0
        cutoff = min(50.0, nyq * 0.8)  # safe cutoff below Nyquist
        b, a = sp_signal.butter(2, cutoff / nyq, btype='highpass')
        cleaned = sp_signal.filtfilt(b, a, cleaned)
    except Exception:
        pass  # Fall through with DC-removed audio if filter fails
    # 3. Safe normalization
    peak = np.max(np.abs(cleaned))
    if peak > 1e-6:
        cleaned = cleaned * (0.95 / peak)
    return cleaned


def save_wav(filepath: str, data: np.ndarray, sample_rate: int = 44100):
    """
    Save 1-D audio array to a standard 16-bit PCM WAV file.
    Normalizes or clamps amplitude safely to prevent clipping.
    """
    if len(data) == 0:
        raise ValueError("Cannot save empty audio data to WAV file.")
    data_norm = np.array(data, dtype=np.float32)
    max_val = np.max(np.abs(data_norm))
    if max_val > 1.0:
        data_norm = data_norm / max_val
    scaled = np.int16(data_norm * 32767)
    wavfile.write(filepath, sample_rate, scaled)


def load_wav(filepath: str):
    """
    Load a WAV file and return (data_mono_float64, sample_rate).
    Converts multi-channel to mono and normalizes amplitudes to [-1.0, 1.0].
    """
    sr, raw = wavfile.read(filepath)
    if raw.ndim > 1:
        # Average across channels for mono
        raw = np.mean(raw, axis=1)
    # Normalize by dtype
    if raw.dtype == np.int16:
        data = raw.astype(np.float64) / 32768.0
    elif raw.dtype == np.int32:
        data = raw.astype(np.float64) / 2147483648.0
    elif raw.dtype == np.uint8:
        data = (raw.astype(np.float64) - 128.0) / 128.0
    else:
        data = raw.astype(np.float64)
        peak = np.max(np.abs(data))
        if peak > 1.0:
            data = data / peak
    return data, sr


# --------------------------------------------------------------------------
# 3. Frequency-domain analysis (FFT, Spectrogram, Carrier Detection)
# --------------------------------------------------------------------------

def compute_fft(data, sample_rate):
    """Return (frequencies, magnitude) of the one-sided amplitude spectrum."""
    n = len(data)
    if n == 0:
        return np.array([]), np.array([])
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    mag = np.abs(np.fft.rfft(data)) / n
    return freqs, mag


def dominant_frequency(data, sample_rate, min_freq=200.0, max_freq=3000.0):
    """Estimate the strongest frequency component in [min_freq, max_freq] Hz."""
    freqs, mag = compute_fft(data, sample_rate)
    if len(freqs) < 2:
        return 700.0
    valid = (freqs >= min_freq) & (freqs <= max_freq)
    if not np.any(valid):
        idx = np.argmax(mag[1:]) + 1
        return float(freqs[idx])
    valid_freqs = freqs[valid]
    valid_mag = mag[valid]
    idx = np.argmax(valid_mag)
    return float(valid_freqs[idx])


def detect_carrier_frequency(data, sample_rate, min_freq=350.0, max_freq=2500.0):
    """
    Accurately estimate the Morse carrier frequency from audio data.
    Uses Welch's power spectral density (PSD) with fine frequency resolution,
    ignoring room rumble/DC (< 350 Hz) and high-frequency noise (> 2500 Hz).
    """
    if len(data) == 0:
        return 700.0
    nperseg = min(len(data), 4096)
    if nperseg < 16:
        return 700.0
    freqs, psd = sp_signal.welch(data, sample_rate, nperseg=nperseg)
    valid = (freqs >= min_freq) & (freqs <= min(max_freq, sample_rate / 2.0 - 50))
    if not np.any(valid):
        return dominant_frequency(data, sample_rate, min_freq, max_freq)
    valid_freqs = freqs[valid]
    valid_psd = psd[valid]
    idx = np.argmax(valid_psd)
    return float(valid_freqs[idx])


def compute_spectrogram(data, sample_rate, nperseg=512, noverlap=384):
    """Return (frequencies, times, Sxx_in_dB) for time-frequency analysis."""
    if len(data) == 0:
        return np.array([]), np.array([])
    nperseg = min(len(data), nperseg)
    if nperseg < 32:
        return np.array([]), np.array([]), np.array([[]])
    noverlap = min(nperseg // 2, noverlap)
    f, t, sxx = sp_signal.spectrogram(data, fs=sample_rate, nperseg=nperseg, noverlap=noverlap)
    # Convert power to dB
    sxx_db = 10 * np.log10(np.maximum(sxx, 1e-12))
    return f, t, sxx_db


# --------------------------------------------------------------------------
# 4. Noise
# --------------------------------------------------------------------------

def add_noise(data, snr_db=10.0, noise_type='white'):
    """
    Add noise to reach target SNR (in dB).
    Supported noise_type:
      - 'white': Additive White Gaussian Noise (AWGN)
      - 'hum': 60Hz mains hum + 120Hz harmonic + white noise
      - 'clicks': White noise + occasional acoustic transient pops/clicks
    """
    if len(data) == 0:
        return data
    sig_power = np.mean(data ** 2)
    if sig_power <= 0:
        sig_power = 1e-12
    noise_power = sig_power / (10 ** (snr_db / 10.0))
    white = np.sqrt(noise_power) * np.random.randn(len(data))

    if noise_type == 'hum':
        t = np.arange(len(data)) / 44100.0
        hum = np.sqrt(noise_power) * 0.7 * (
            np.sin(2 * np.pi * 60 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)
        )
        return data + 0.7 * white + hum
    elif noise_type == 'clicks':
        clicks = np.zeros(len(data))
        num_clicks = max(1, int(len(data) / 20000))
        for _ in range(num_clicks):
            pos = np.random.randint(0, len(data) - 500)
            clicks[pos:pos + 300] += np.sqrt(noise_power) * 2.5 * np.random.randn(300)
        return data + white + clicks

    return data + white


def estimate_snr_db(clean, noisy):
    """Rough SNR estimate given the original clean signal and the noisy signal."""
    if len(clean) == 0 or len(noisy) == 0:
        return float('inf')
    min_len = min(len(clean), len(noisy))
    noise = noisy[:min_len] - clean[:min_len]
    sig_power = np.mean(clean[:min_len] ** 2)
    noise_power = np.mean(noise ** 2)
    if noise_power <= 0:
        return float('inf')
    return 10.0 * np.log10(max(sig_power, 1e-12) / noise_power)


# --------------------------------------------------------------------------
# 5. Filtering
# --------------------------------------------------------------------------

def bandpass_filter(data, center_freq, sample_rate, bandwidth=200.0, order=4):
    """Zero-phase Butterworth band-pass filter around the carrier tone."""
    if len(data) == 0:
        return data
    nyq = sample_rate / 2.0
    low = max((center_freq - bandwidth / 2.0) / nyq, 1e-4)
    high = min((center_freq + bandwidth / 2.0) / nyq, 0.999)
    if low >= high:
        return data
    b, a = sp_signal.butter(order, [low, high], btype='band')
    padlen = 3 * (max(len(a), len(b)) - 1)
    if len(data) <= padlen:
        return data  # too short to filtfilt safely
    return sp_signal.filtfilt(b, a, data)


def filter_frequency_response(center_freq, sample_rate, bandwidth=200.0, order=4, num_points=1024):
    """
    Compute the theoretical frequency response |H(f)| of the Butterworth bandpass filter.
    Returns (frequencies_hz, magnitude_response).
    """
    nyq = sample_rate / 2.0
    low = max((center_freq - bandwidth / 2.0) / nyq, 1e-4)
    high = min((center_freq + bandwidth / 2.0) / nyq, 0.999)
    if low >= high:
        return np.array([]), np.array([])
    b, a = sp_signal.butter(order, [low, high], btype='band')
    w, h = sp_signal.freqz(b, a, worN=num_points, fs=sample_rate)
    return w, np.abs(h)


def lowpass_filter(data, cutoff, sample_rate, order=4):
    """Zero-phase Butterworth low-pass filter."""
    if len(data) == 0:
        return data
    nyq = sample_rate / 2.0
    norm_cutoff = min(max(cutoff / nyq, 1e-4), 0.999)
    b, a = sp_signal.butter(order, norm_cutoff, btype='low')
    padlen = 3 * (max(len(a), len(b)) - 1)
    if len(data) <= padlen:
        return data
    return sp_signal.filtfilt(b, a, data)


# --------------------------------------------------------------------------
# 6. Envelope Detection & Adaptive Thresholding
# --------------------------------------------------------------------------

def envelope(data, sample_rate, smoothing_ms=12.0):
    """
    Amplitude envelope via Hilbert transform followed by moving-average smoothing.
    12ms smoothing provides optimal noise rejection without rounding off dot/dash edges.
    """
    if len(data) == 0:
        return data
    analytic = sp_signal.hilbert(data)
    env = np.abs(analytic)
    window = max(int(sample_rate * smoothing_ms / 1000.0), 3)
    kernel = np.ones(window) / window
    return np.convolve(env, kernel, mode='same')


def otsu_threshold(values, bins=128):
    """
    Compute optimal bimodal threshold using Otsu's method.
    Effectively separates tone active periods (ON) from noise/silence (OFF).
    """
    if len(values) == 0:
        return 0.0
    hist, bin_edges = np.histogram(values, bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    total = np.sum(hist)
    if total == 0:
        return float(np.mean(values))
    sum_total = np.sum(hist * bin_centers)

    weight_b = 0.0
    sum_b = 0.0
    max_var = -1.0
    best_thresh = bin_centers[0]

    for i in range(len(hist)):
        weight_b += hist[i]
        if weight_b == 0:
            continue
        weight_f = total - weight_b
        if weight_f == 0:
            break
        sum_b += hist[i] * bin_centers[i]
        mean_b = sum_b / weight_b
        mean_f = (sum_total - sum_b) / weight_f
        var_between = weight_b * weight_f * ((mean_b - mean_f) ** 2)
        if var_between > max_var:
            max_var = var_between
            best_thresh = bin_centers[i]

    return float(best_thresh)


# --------------------------------------------------------------------------
# 7. Robust Demodulation & Decoding (Audio Waveform -> Morse)
# --------------------------------------------------------------------------

def decode_signal_to_morse(data, sample_rate, carrier_freq=None,
                           bandwidth=200.0, threshold_ratio=None,
                           return_details=False):
    """
    Demodulate and decode a Morse audio signal directly from audio (raw mic or filtered).

    Pipeline:
      1. Carrier detection: Automatically finds dominant carrier frequency via Welch PSD
         if not explicitly supplied.
      2. Bandpass filtering: Eliminates out-of-band acoustic noise, room rumble, and DC drift.
      3. Analytic envelope: Computes smoothed Hilbert amplitude envelope.
      4. Otsu Adaptive Thresholding: Dynamically splits active tone (ON) from quiet room (OFF).
      5. Glitch debouncing: Eliminates transient acoustic clicks / dropouts (< 15 ms).
      6. Lead-in/Lead-out trimming: Ignores silence before and after the Morse transmission.
      7. Dual-Cluster & Off-Gap Timing calibration: Accurately discovers dot duration (T)
         even for all-dash words ("M", "O", "T") or all-dot words ("E", "S", "H") by
         analyzing intra-character gap durations.
      8. Symbol & word segmentation: Produces standard dots, dashes, letter gaps, and word gaps.

    Parameters:
      - data: 1-D numpy array of audio samples
      - sample_rate: sampling frequency in Hz
      - carrier_freq: known carrier frequency, or None to auto-detect
      - bandwidth: filter bandwidth around carrier (default 200 Hz)
      - threshold_ratio: optional fixed ratio of peak envelope (None for Otsu adaptive)
      - return_details: if True, returns (morse_string, metrics_dict)

    Returns:
      morse_string (or tuple (morse_string, metrics_dict))
    """
    empty_result = ('', {}) if return_details else ''
    if len(data) == 0:
        return empty_result

    # 1. Detect or use carrier frequency
    if carrier_freq is None or carrier_freq <= 0:
        carrier = detect_carrier_frequency(data, sample_rate)
    else:
        carrier = float(carrier_freq)

    # 2. Bandpass filter around carrier frequency
    filtered = bandpass_filter(data, carrier, sample_rate, bandwidth=bandwidth)

    # 3. Hilbert envelope + smoothing
    env = envelope(filtered, sample_rate, smoothing_ms=12.0)
    if len(env) == 0:
        return empty_result

    # Evaluate dynamic range & noise floor
    floor_val = float(np.percentile(env, 15))
    peak_val = float(np.percentile(env, 95))

    if peak_val <= 1e-6 or (peak_val / max(floor_val, 1e-6) < 1.25):
        # Signal is pure silence / noise floor without discernible Morse tone
        metrics = {
            'wpm': 0.0,
            'carrier_freq': carrier,
            'threshold': 0.0,
            'snr_est': 0.0,
            'filtered': filtered,
            'envelope': env,
        }
        return ('', metrics) if return_details else ''

    # 4. Threshold calculation
    if threshold_ratio is not None:
        thresh = float(threshold_ratio * np.max(env))
    else:
        otsu_val = otsu_threshold(env)
        # Ensure threshold is safely bounded between noise floor and tone peak
        thresh = float(max(floor_val * 1.15, min(otsu_val, peak_val * 0.85)))

    on = env > thresh

    # 5. Debounce short runs (< 15 ms is physical noise, not Morse)
    min_samples = max(int(sample_rate * 0.015), 2)
    runs = []
    start = 0
    cur_state = bool(on[0])
    for i in range(1, len(on)):
        if bool(on[i]) != cur_state:
            runs.append([cur_state, i - start])
            start = i
            cur_state = bool(on[i])
    runs.append([cur_state, len(on) - start])

    # Clean runs shorter than min_samples by merging with adjacent
    cleaned_runs = []
    for state, length in runs:
        if length < min_samples and cleaned_runs:
            cleaned_runs[-1][1] += length
        else:
            if cleaned_runs and cleaned_runs[-1][0] == state:
                cleaned_runs[-1][1] += length
            else:
                cleaned_runs.append([state, length])

    # 6. Trim leading and trailing silence
    if cleaned_runs and not cleaned_runs[0][0]:
        cleaned_runs.pop(0)
    if cleaned_runs and not cleaned_runs[-1][0]:
        cleaned_runs.pop(-1)

    on_durs = [length / sample_rate for state, length in cleaned_runs if state]
    off_durs = [length / sample_rate for state, length in cleaned_runs if not state]

    if not on_durs:
        metrics = {
            'wpm': 0.0,
            'carrier_freq': carrier,
            'threshold': thresh,
            'snr_est': 0.0,
            'filtered': filtered,
            'envelope': env,
        }
        return ('', metrics) if return_details else ''

    # 7. Unit timing (T) estimation
    if len(on_durs) == 1:
        # Single pulse
        unit = on_durs[0] if on_durs[0] < 0.12 else on_durs[0] / 3.0
    else:
        min_d = min(on_durs)
        max_d = max(on_durs)
        if max_d / max(min_d, 1e-4) >= 1.8:
            # Bimodal cluster: both dots and dashes present
            split = (min_d + max_d) / 2.0
            dots = [d for d in on_durs if d < split]
            dashes = [d for d in on_durs if d >= split]
            t_dot = float(np.median(dots)) if dots else min_d
            t_dash = float(np.median(dashes)) if dashes else max_d
            unit = (t_dot + t_dash / 3.0) / 2.0
        else:
            # Single cluster: all pulses roughly equal duration (e.g. "M", "O", "E", "S")
            med_on = float(np.median(on_durs))
            if off_durs:
                med_off = float(np.median(off_durs))
                # In standard Morse, intra-gap is 1 unit. If pulse is ~3x gap, pulses are dashes!
                if med_on > 2.0 * med_off:
                    unit = med_on / 3.0  # Pulses are dashes
                else:
                    unit = med_on        # Pulses are dots
            else:
                unit = med_on if med_on < 0.12 else med_on / 3.0

    wpm_est = 1.2 / max(unit, 1e-4)
    snr_est = 20.0 * np.log10(max(peak_val, 1e-6) / max(floor_val, 1e-6))

    # 8. Assemble Morse symbols and word separators
    morse = ''
    for state, length in cleaned_runs:
        dur = length / sample_rate
        n_units = dur / unit
        if state:
            morse += '.' if n_units < 2.0 else '-'
        else:
            if n_units < 1.8:
                continue             # intra-letter gap
            elif n_units < 4.5:
                morse += ' '         # inter-letter gap
            else:
                morse += ' / '       # inter-word gap

    morse_result = morse.strip(' /')

    if return_details:
        metrics = {
            'wpm': float(wpm_est),
            'carrier_freq': float(carrier),
            'threshold': float(thresh),
            'snr_est': float(snr_est),
            'filtered': filtered,
            'envelope': env,
            'unit_duration': float(unit)
        }
        return morse_result, metrics

    return morse_result