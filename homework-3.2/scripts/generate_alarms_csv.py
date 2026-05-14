#!/usr/bin/env python3
"""
Reproducible synthetic alarm CSV (Homework 3.2).
Use scripts/AI_PROMPT_FOR_ALARMS.md if you prefer ChatGPT-generated rows instead.
"""
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "alarms.csv"
N = 2000
FALSE_RATE = 0.15


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    is_false = RNG.random(N) < FALSE_RATE

    duration = np.zeros(N)
    peak = np.zeros(N)
    rep = np.zeros(N, dtype=int)
    hour = RNG.integers(0, 24, size=N)

    # True alarms: longer duration, higher peak, fewer repeats on average
    dur_true = RNG.uniform(30, 280, size=N)
    peak_true = RNG.uniform(0.35, 1.0, size=N)
    rep_true = RNG.integers(0, 12, size=N)

    # False alarms: shorter, weaker peak, more chatter
    dur_false = RNG.uniform(1, 90, size=N)
    peak_false = RNG.uniform(0.05, 0.55, size=N)
    rep_false = RNG.integers(5, 45, size=N)

    duration[is_false] = dur_false[is_false]
    duration[~is_false] = dur_true[~is_false]
    peak[is_false] = peak_false[is_false]
    peak[~is_false] = peak_true[~is_false]
    rep[is_false] = rep_false[is_false]
    rep[~is_false] = rep_true[~is_false]

    df = pd.DataFrame(
        {
            "id": np.arange(1, N + 1),
            "duration_sec": np.round(duration, 2),
            "peak_amplitude": np.round(peak, 4),
            "repetition_count": rep,
            "hour_of_day": hour,
            "is_false_alarm": is_false.astype(int),
        }
    )
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df)} rows to {OUT}")


if __name__ == "__main__":
    main()
