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

    # Adjust pitch_floor based on utterance duration
    pitch_floor = max(75, 1.0 / duration)  # Avoid too low pitch_floor for short segments
    pitch_ceiling = 500

    try:
        pitch = sound.to_pitch(time_step=0.01, pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling).selected_array['frequency']
    except Exception as e:
        print(f"Skipping utterance: {e}")
        return np.array([]), 0, duration

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

    if min_len == 0:
        return np.array([]), 0, duration

    prominence = lambda_ * mid_energy + beta_ * (rms_energy * A_pitch * D_pitch)
    prominence = (prominence - np.min(prominence)) / (np.max(prominence) - np.min(prominence) + 1e-8)

    return prominence, min_len, duration



def extract_word_prominence_from_prosody(wav_path, textgrid_path, tier_name="word", utt_threshold=0.3, lambda_=0.5, beta_=0.5):
    waveform, sr = torchaudio.load(wav_path)
    samples = waveform[0].numpy()
    tg = textgrid.TextGrid.fromFile(textgrid_path)

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
            next_start = interval.maxTime
            if next_start - current_end > utt_threshold:
                utterances.append((current_start, current_end))
                current_start = None
                current_end = None

    if current_start is not None:
        utterances.append((current_start, current_end))

    results = {}
    for u_start, u_end in utterances:
        start_sample = int(sr * u_start)
        end_sample = int(sr * u_end)
        utter_samples = samples[start_sample:end_sample]

        try:
            prominence, num_frames, duration = extract_prosodic_features(utter_samples, sr, lambda_, beta_)
        except Exception as e:
            print(f"Skipping utterance from {u_start:.2f}s to {u_end:.2f}s due to error: {e}")
            continue

        if len(prominence) == 0 or num_frames == 0:
            print(f" Feature extraction failed for audio segment {u_start:.2f}s–{u_end:.2f}s (may be due to silence or short duration). Skipping segment.")
            continue

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
            if len(frame_indices) == 0:
                print(f"Skipping word '{word}' (no overlapping frames).")
                continue

            try:
                score = float(np.sum(prominence[frame_indices]))
                raw_scores[(interval.minTime, word)] = score
            except Exception as e:
                print(f"Skipping word '{word}' due to scoring error: {e}")
                continue

        if len(raw_scores) == 0:
            continue  # skip normalization if no valid scores

        min_val, max_val = np.min(list(raw_scores.values())), np.max(list(raw_scores.values()))
        for k, v in raw_scores.items():
            norm = (v - min_val) / (max_val - min_val + 1e-8)
            results[k] = {"raw": v, "norm": norm}

    return results
