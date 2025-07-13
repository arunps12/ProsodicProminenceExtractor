import numpy as np
import parselmouth
import torchaudio
from scipy.signal import butter, lfilter
import textgrid
import os


def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)


def compute_event_params(array, frame_duration=0.02):
    n = len(array)
    A_event = np.zeros(n)
    D_event = np.zeros(n)
    for i in range(1, n - 1):
        prev, curr, next_ = array[i - 1], array[i], array[i + 1]
        Arise = max(0, curr - prev)
        Afall = max(0, curr - next_)
        A_event[i] = abs(Arise) + abs(Afall)
        D_event[i] = frame_duration * ((Arise > 0) + (Afall > 0))
    return A_event, D_event


def extract_prosodic_features(samples, sr, lambda_=0.5, beta_=0.5):
    sound = parselmouth.Sound(samples, sampling_frequency=sr)
    duration = sound.duration

    pitch = sound.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=500).selected_array['frequency']
    frame_len = int(0.02 * sr)
    hop_len = frame_len
    frames = np.lib.stride_tricks.sliding_window_view(samples, window_shape=frame_len)[::hop_len]
    rms_energy = np.sqrt(np.mean(frames**2, axis=1))

    mid_band_signal = bandpass_filter(samples, 300, 2200, sr)
    mid_frames = np.lib.stride_tricks.sliding_window_view(mid_band_signal, window_shape=frame_len)[::hop_len]
    mid_energy = np.sqrt(np.mean(mid_frames**2, axis=1))

    pitch_interp = np.interp(
        np.linspace(0, duration, len(mid_energy)),
        np.linspace(0, duration, len(pitch)),
        np.nan_to_num(pitch, nan=0)
    )

    if len(pitch_interp) >= frame_len:
        pitch_frames = np.lib.stride_tricks.sliding_window_view(pitch_interp, window_shape=frame_len)[::hop_len]
        pitch_per_frame = np.mean(pitch_frames, axis=1)
    else:
        pitch_per_frame = np.zeros(len(mid_energy))

    A_pitch, D_pitch = compute_event_params(pitch_per_frame)
    A_mid, D_mid = compute_event_params(mid_energy)

    min_len = min(len(mid_energy), len(rms_energy), len(A_pitch), len(D_pitch))
    mid_energy = mid_energy[:min_len]
    rms_energy = rms_energy[:min_len]
    A_pitch = A_pitch[:min_len]
    D_pitch = D_pitch[:min_len]

    prominence = lambda_ * mid_energy + beta_ * (rms_energy * A_pitch * D_pitch)
    prominence = (prominence - np.min(prominence)) / (np.max(prominence) - np.min(prominence) + 1e-8)

    return prominence, min_len, duration


def extract_word_prominence_from_prosody(wav_path, textgrid_path, tier_name="word", utt_threshold=0.3, lambda_=0.5, beta_=0.5):
    waveform, sr = torchaudio.load(wav_path)
    samples = waveform[0].numpy()
    tg = textgrid.TextGrid.fromFile(textgrid_path)
    
    # Collect utterances by merging short gaps between intervals
    tier = next((t for t in tg.tiers if t.name.lower() == tier_name.lower()), None)
    if tier is None:
        raise ValueError(f"No tier named '{tier_name}' found in {textgrid_path}")

    utterances = []
    current_start = None
    current_end = None

    for interval in tier.intervals:
        if interval.mark.strip():
            if current_start is None:
                current_start = interval.minTime
            current_end = interval.maxTime
        elif current_end is not None:
            # If next word appears after long silence
            next_start = interval.maxTime
            if next_start - current_end > utt_threshold:
                utterances.append((current_start, current_end))
                current_start = None
                current_end = None

    if current_start is not None:
        utterances.append((current_start, current_end))

    # Compute prominence per word, normalized by utterance
    results = {}
    for u_start, u_end in utterances:
        start_sample = int(sr * u_start)
        end_sample = int(sr * u_end)
        utter_samples = samples[start_sample:end_sample]
        prominence, num_frames, duration = extract_prosodic_features(utter_samples, sr, lambda_, beta_)
        frame_times = np.linspace(u_start, u_end, num_frames, endpoint=False)
        frame_duration = (u_end - u_start) / num_frames
        frame_starts = frame_times
        frame_ends = frame_times + frame_duration

        raw_scores = {}
        for interval in tier.intervals:
            word = interval.mark.strip()
            if not word:
                continue
            if not (u_start <= interval.minTime < u_end):
                continue
            frame_indices = np.where((frame_starts < interval.maxTime) & (frame_ends > interval.minTime))[0]
            score = float(np.sum(prominence[frame_indices])) if len(frame_indices) > 0 else 0.0
            raw_scores[(interval.minTime, word)] = score

        # Normalize within utterance
        values = list(raw_scores.values())
        min_val, max_val = np.min(values), np.max(values)
        norm_scores = {
            k: (v - min_val) / (max_val - min_val + 1e-8) for k, v in raw_scores.items()
        }

        for k in raw_scores:
            results[k] = {"raw": raw_scores[k], "norm": norm_scores[k]}

    return results
