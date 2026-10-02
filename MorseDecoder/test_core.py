"""
test_core.py
-------------
Comprehensive sanity and regression tests for morse_code.py and signal_proc.py
that do NOT require tkinter or an audio device, so they can run anywhere:

    python test_core.py
"""

import os
import tempfile
import numpy as np

import morse_code as mc
import signal_proc as sp


def test_text_roundtrip():
    for text in ["HELLO WORLD", "SOS", "Python 3.12!", "A B C", "FAST CW 2026"]:
        morse = mc.text_to_morse(text)
        back = mc.morse_to_text(morse)
        assert back == text.upper(), f"Roundtrip failed for {text!r}: got {back!r}"
    print("[OK] text <-> morse roundtrip")


def test_signal_generation():
    morse = mc.text_to_morse("SOS")
    sig = sp.morse_to_signal(morse, freq=700, wpm=20, sample_rate=8000, amplitude=0.8)
    assert len(sig) > 0
    assert np.max(np.abs(sig)) <= 0.8 + 1e-9
    print(f"[OK] signal generation ({len(sig)} samples, {len(sig)/8000:.2f}s)")
    return sig


def test_fft_recovers_frequency(sig):
    freq_est = sp.dominant_frequency(sig, 8000)
    assert abs(freq_est - 700) < 15, f"Expected ~700 Hz, got {freq_est} Hz"
    print(f"[OK] FFT dominant frequency ~= {freq_est:.1f} Hz")


def test_carrier_detection():
    for f in [550, 750, 1000]:
        morse = mc.text_to_morse("TEST")
        sig = sp.morse_to_signal(morse, freq=f, wpm=18, sample_rate=16000)
        # Add background room noise and DC offset
        noisy = sig + 0.05 * np.random.randn(len(sig)) + 0.02
        detected = sp.detect_carrier_frequency(noisy, 16000)
        assert abs(detected - f) < 25, f"Expected ~{f} Hz, got {detected} Hz"
    print("[OK] carrier frequency detection across multiple frequencies")


def test_noise_filter_decode_pipeline(sig):
    noisy = sp.add_noise(sig, snr_db=6)
    filtered = sp.bandpass_filter(noisy, 700, 8000, bandwidth=250)
    morse_out = sp.decode_signal_to_morse(filtered, 8000)
    text_out = mc.morse_to_text(morse_out)
    assert text_out == "SOS", f"Expected SOS, got {text_out!r}"
    print(f"[OK] noise -> filter -> decode pipeline recovered: {text_out!r}")


def test_dash_only_and_dot_only_words():
    for word in ["M", "O", "T", "E", "HI", "NO"]:
        morse = mc.text_to_morse(word)
        sig = sp.morse_to_signal(morse, freq=750, wpm=20, sample_rate=16000)
        padded = np.concatenate([np.zeros(2000), sig, np.zeros(2000)])
        morse_decoded = sp.decode_signal_to_morse(padded, 16000, carrier_freq=750)
        text_decoded = mc.morse_to_text(morse_decoded)
        assert text_decoded == word, f"Expected {word}, got {text_decoded!r} (morse: {morse_decoded})"
    print("[OK] dash-only and single-pulse word decoding ('M', 'O', 'T', 'E', 'HI', 'NO')")


def test_realistic_mic_recording_decode():
    """Simulates real room mic audio: lead/trail silence, 60Hz hum, DC offset, clicks."""
    text = "HELLO WORLD"
    morse = mc.text_to_morse(text)
    sig = sp.morse_to_signal(morse, freq=700, wpm=18, sample_rate=44100)
    lead = np.zeros(int(44100 * 1.0))
    trail = np.zeros(int(44100 * 1.0))
    audio = np.concatenate([lead, sig, trail])

    t = np.arange(len(audio)) / 44100.0
    noise = 0.04 * np.sin(2 * np.pi * 60 * t) + 0.02 * np.random.randn(len(audio)) + 0.015
    audio_noisy = audio + noise
    # Add a loud transient click
    audio_noisy[3000:3300] += 0.5

    morse_out, details = sp.decode_signal_to_morse(audio_noisy, 44100, return_details=True)
    text_out = mc.morse_to_text(morse_out)
    assert text_out == text, f"Realistic mic decode failed! Expected {text!r}, got {text_out!r}"
    assert details['wpm'] > 12 and details['wpm'] < 25
    print(f"[OK] realistic mic recording decode recovered: {text_out!r} (est. {details['wpm']:.1f} WPM)")


def test_wav_file_roundtrip():
    sig = sp.morse_to_signal(mc.text_to_morse("WAV TEST"), freq=800, wpm=22, sample_rate=16000)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        tmp_path = f.name
    try:
        sp.save_wav(tmp_path, sig, 16000)
        loaded, sr = sp.load_wav(tmp_path)
        assert sr == 16000
        assert len(loaded) == len(sig)
        assert np.max(np.abs(loaded - sig)) < 1e-3
        print("[OK] WAV save and load roundtrip")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_invalid_morse_detection():
    assert mc.is_valid_morse(".... . .-.. .-.. --- / .-- --- .-. .-.. -..")
    assert not mc.is_valid_morse("HELLO")
    print("[OK] morse validity check")


if __name__ == '__main__':
    test_text_roundtrip()
    sig = test_signal_generation()
    test_fft_recovers_frequency(sig)
    test_carrier_detection()
    test_noise_filter_decode_pipeline(sig)
    test_dash_only_and_dot_only_words()
    test_realistic_mic_recording_decode()
    test_wav_file_roundtrip()
    test_invalid_morse_detection()
    print("\nAll core & advanced DSP tests passed successfully.")