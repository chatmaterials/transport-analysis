#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from analyze_carrier_type import analyze as analyze_carrier


KB_EV_K = 8.617333262145e-5


def classify_risk(score: float) -> str:
    if score < 1e-4:
        return "low-bipolar-risk"
    if score < 1e-2:
        return "moderate-bipolar-risk"
    return "high-bipolar-risk"


def analyze(path: Path, occupied_bands: int, fermi: float, temperature_k: float) -> dict[str, object]:
    carrier = analyze_carrier(path, occupied_bands, fermi)
    gap = float(carrier["band_gap_eV"])
    if temperature_k <= 0:
        raise SystemExit("Temperature must be positive")
    score = math.exp(-gap / (2.0 * KB_EV_K * temperature_k))
    return {
        "path": str(path),
        "temperature_K": temperature_k,
        "band_gap_eV": gap,
        "bipolar_risk_score": score,
        "bipolar_risk_class": classify_risk(score),
        "observations": [
            "Bipolar risk was estimated from a simple intrinsic excitation factor based on the band gap and temperature."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate a compact bipolar-conduction risk from the band gap and temperature.")
    parser.add_argument("path")
    parser.add_argument("--occupied-bands", type=int, default=2)
    parser.add_argument("--fermi", type=float, required=True)
    parser.add_argument("--temperature-k", type=float, default=300.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(
        Path(args.path).expanduser().resolve(),
        args.occupied_bands,
        args.fermi,
        args.temperature_k,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
