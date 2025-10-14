# filename: beatstoch/generator.py
import random
from typing import List, Tuple, Optional

import numpy as np
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

# General MIDI drum note numbers
DRUMS = {
    "kick": 36,
    "snare": 38,
    "closed_hat": 42,
    "open_hat": 46,
    "ride": 51,
    "clap": 39,
    "tom_low": 41,
    "tom_mid": 45,
    "tom_high": 48,
}


def _triangular(mean: float, spread: float) -> float:
    return np.random.triangular(-spread, 0.0, spread) + mean


def _clip_velocity(val: float, lo: int = 1, hi: int = 127) -> int:
    return max(lo, min(hi, int(round(val))))


def generate_stochastic_pattern(
    bpm: float,
    bars: int = 4,
    meter: Tuple[int, int] = (4, 4),
    steps_per_beat: int = 4,
    swing: float = 0.12,
    intensity: float = 0.9,
    seed: int = 42,
    style: str = "house",
) -> MidiFile:
    random.seed(seed)
    np.random.seed(seed)

    beats_per_bar = meter[0]
    steps_per_bar = beats_per_bar * steps_per_beat

    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(Message("program_change", program=0, time=0))
    tempo = bpm2tempo(bpm)
    track.append(MetaMessage("set_tempo", tempo=tempo, time=0))

    if style == "house":
        # Steady house: reliable four-on-the-floor with consistent hats
        kick_probs = [
            0.98 if (i % steps_per_beat == 0) else 0.05 for i in range(steps_per_bar)
        ]
        snare_probs = [
            0.95 if (i % (2 * steps_per_beat) == steps_per_beat) else 0.03
            for i in range(steps_per_bar)
        ]
        hat_probs = [
            0.90 if (i % (steps_per_beat // 2) != 0) else 0.70
            for i in range(steps_per_bar)
        ]
        instruments = [
            ("kick", kick_probs, (95, 120), 0.003),  # Less jitter for steady feel
            ("snare", snare_probs, (90, 115), 0.004),
            ("closed_hat", hat_probs, (60, 95), 0.002),
            (
                "open_hat",
                [
                    0.15 if i % steps_per_beat == 2 else 0.05
                    for i in range(steps_per_bar)
                ],
                (70, 95),
                0.006,
            ),
        ]
    elif style == "breaks":
        # Steady breaks: predictable syncopated pattern with consistent timing
        kick_probs = [0.90 if i in (0, 6, 8, 14) else 0.10 for i in range(steps_per_bar)]
        snare_probs = [0.92 if i in (4, 12) else 0.08 for i in range(steps_per_bar)]
        hat_probs = [0.85 for _ in range(steps_per_bar)]
        instruments = [
            ("kick", kick_probs, (90, 115), 0.005),  # Less jitter for steady feel
            ("snare", snare_probs, (90, 115), 0.006),
            ("closed_hat", hat_probs, (55, 95), 0.003),
            (
                "open_hat",
                [0.20 if i in (7, 15) else 0.08 for i in range(steps_per_bar)],
                (70, 95),
                0.008,
            ),
        ]
    else:
        # Steady generic: reliable backbeat with consistent timing
        kick_probs = [
            0.95 if (i % steps_per_beat == 0) else 0.05 for i in range(steps_per_bar)
        ]
        snare_probs = [
            0.90 if (i % (2 * steps_per_beat) == steps_per_beat) else 0.05
            for i in range(steps_per_bar)
        ]
        hat_probs = [0.80 for _ in range(steps_per_bar)]
        instruments = [
            ("kick", kick_probs, (85, 115), 0.004),  # Less jitter for steady feel
            ("snare", snare_probs, (85, 115), 0.005),
            ("closed_hat", hat_probs, (60, 95), 0.003),
        ]

    for idx, (name, probs, vel_rng, jitter) in enumerate(instruments):
        scaled = [max(0.0, min(1.0, p * intensity)) for p in probs]
        instruments[idx] = (name, scaled, vel_rng, jitter)

    def _step_to_ticks(step_idx: int, jitter_sec: float) -> int:
        base_beats = step_idx / steps_per_beat
        base_ticks = int(round(mid.ticks_per_beat * base_beats))
        if steps_per_beat % 2 == 0:
            eighth_step = steps_per_beat // 2
            if (step_idx % eighth_step) == (eighth_step - 1):
                swing_ticks = int(round(mid.ticks_per_beat * (0.5 * swing)))
                base_ticks += swing_ticks
        sec_per_beat = tempo / 1_000_000.0
        ticks_per_sec = mid.ticks_per_beat / sec_per_beat
        jitter_ticks = int(round(jitter_sec * ticks_per_sec))
        return base_ticks + jitter_ticks

    events: List[Tuple[int, str, int]] = []
    for bar in range(bars):
        bar_offset_steps = bar * steps_per_bar
        for name, probs, vel_rng, jitter in instruments:
            lo, hi = vel_rng
            for s in range(steps_per_bar):
                if random.random() < probs[s]:
                    mean_vel = (lo + hi) / 2
                    spread = (hi - lo) / 2
                    vel = _clip_velocity(
                        _triangular(mean_vel, spread * 0.6) * intensity, lo, hi
                    )
                    jitter_sec = _triangular(0.0, jitter)
                    abs_step = bar_offset_steps + s
                    tick = _step_to_ticks(abs_step, jitter_sec)
                    events.append((tick, name, vel))

    events.sort(key=lambda x: x[0])

    last_tick = 0
    for tick, name, vel in events:
        delta = tick - last_tick
        note = DRUMS.get(name, DRUMS["closed_hat"])
        track.append(
            Message("note_on", channel=9, note=note, velocity=vel, time=max(0, delta))
        )
        track.append(Message("note_off", channel=9, note=note, velocity=0, time=60))
        last_tick = tick + 60

    return mid


from .bpm import fetch_bpm_from_bpmdatabase


def generate_from_song(
    song_title: str,
    artist: Optional[str] = None,
    bars: int = 8,
    style: str = "house",
    steps_per_beat: int = 4,
    swing: float = 0.10,
    intensity: float = 0.9,
    seed: Optional[int] = None,
    fallback_bpm: Optional[float] = None,
    verbose: bool = False,
) -> Tuple[MidiFile, float]:
    bpm = fetch_bpm_from_bpmdatabase(song_title, artist, verbose=verbose)
    if bpm is None:
        if fallback_bpm is None:
            raise RuntimeError("BPM lookup failed and no fallback BPM provided.")
        bpm = fallback_bpm

    if seed is None:
        seed_str = f"{song_title}|{artist or ''}|{int(bpm)}"
        seed = abs(hash(seed_str)) % (2**31)

    mid = generate_stochastic_pattern(
        bpm=bpm,
        bars=bars,
        meter=(4, 4),
        steps_per_beat=steps_per_beat,
        swing=swing,
        intensity=intensity,
        seed=seed,
        style=style,
    )
    return mid, bpm
