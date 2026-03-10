#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_bipolar_risk import analyze as analyze_bipolar
from analyze_carrier_type import analyze as analyze_carrier
from analyze_effective_mass import analyze as analyze_mass
from analyze_transport_trend import analyze as analyze_trend


def locate_required(root: Path, relative_paths: list[str]) -> Path:
    for relative in relative_paths:
        candidate = root / relative
        if candidate.exists():
            return candidate
    raise SystemExit(f"Could not locate any of {relative_paths} in {root}")


def locate_optional(root: Path, relative_paths: list[str]) -> Path | None:
    for relative in relative_paths:
        candidate = root / relative
        if candidate.exists():
            return candidate
    return None


def analyze_case(
    root: Path,
    occupied_bands: int,
    fermi: float,
    target_gap_min: float,
    target_gap_max: float,
    prefer_carrier: str | None,
    temperature_k: float,
) -> dict[str, object]:
    band_path = locate_required(root, ["bands.dat", "band/bands.dat"])
    dos_path = locate_required(root, ["dos.dat", "dos/dos.dat"])
    mass_path = locate_optional(root, ["effective_mass.dat", "effective_mass/effective_mass.dat"])
    carrier = analyze_carrier(band_path, occupied_bands, fermi)
    trend = analyze_trend(band_path, dos_path, occupied_bands, fermi, mass_path, temperature_k)
    mass = analyze_mass(mass_path) if mass_path is not None else None
    bipolar = analyze_bipolar(band_path, occupied_bands, fermi, temperature_k)

    gap = float(carrier["band_gap_eV"])
    if gap < target_gap_min:
        gap_penalty = target_gap_min - gap
    elif gap > target_gap_max:
        gap_penalty = gap - target_gap_max
    else:
        gap_penalty = 0.0
    regime_penalty = 2.0 if trend["regime"] == "metallic-like" else 0.0
    carrier_penalty = 0.25 if prefer_carrier and carrier["carrier_tendency"] != prefer_carrier else 0.0
    mass_value = abs(float(mass["effective_mass_me"])) if mass and mass["effective_mass_me"] is not None else None
    mass_penalty = 0.25 * mass_value if mass_value is not None else 0.5
    quality_penalty = max(0.0, 0.3 - float(trend["thermoelectric_quality_score"]))
    bipolar_penalty = 10.0 * float(bipolar["bipolar_risk_score"])
    score = gap_penalty + regime_penalty + carrier_penalty + mass_penalty + quality_penalty + bipolar_penalty

    return {
        "case": root.name,
        "path": str(root),
        "carrier_tendency": carrier["carrier_tendency"],
        "band_gap_eV": gap,
        "regime": trend["regime"],
        "dos_at_fermi": trend["dos_at_fermi"],
        "effective_mass_me": mass["effective_mass_me"] if mass else None,
        "activation_energy_eV": trend["activation_energy_eV"],
        "thermoelectric_quality_score": trend["thermoelectric_quality_score"],
        "screening_class": trend["screening_class"],
        "bipolar_risk_score": bipolar["bipolar_risk_score"],
        "bipolar_risk_class": bipolar["bipolar_risk_class"],
        "gap_penalty_eV": gap_penalty,
        "regime_penalty": regime_penalty,
        "carrier_penalty": carrier_penalty,
        "mass_penalty": mass_penalty,
        "quality_penalty": quality_penalty,
        "bipolar_penalty": bipolar_penalty,
        "screening_score": score,
    }


def analyze_cases(
    roots: list[Path],
    occupied_bands: int,
    fermi: float,
    target_gap_min: float,
    target_gap_max: float,
    prefer_carrier: str | None,
    temperature_k: float,
) -> dict[str, object]:
    cases = [
        analyze_case(root, occupied_bands, fermi, target_gap_min, target_gap_max, prefer_carrier, temperature_k)
        for root in roots
    ]
    ranked = sorted(cases, key=lambda item: item["screening_score"])
    return {
        "target_gap_window_eV": [target_gap_min, target_gap_max],
        "preferred_carrier": prefer_carrier,
        "temperature_K": temperature_k,
        "ranking_basis": "screening_score = gap_penalty + regime_penalty + carrier_penalty + mass_penalty + quality_penalty + bipolar_penalty",
        "cases": ranked,
        "best_case": ranked[0]["case"] if ranked else None,
        "observations": [
            "This is a compact screening heuristic intended for qualitative ranking, not a Boltzmann transport calculation."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank multiple transport candidates with a simple screening heuristic.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--occupied-bands", type=int, default=2)
    parser.add_argument("--fermi", type=float, required=True)
    parser.add_argument("--target-gap-min", type=float, default=0.5)
    parser.add_argument("--target-gap-max", type=float, default=1.5)
    parser.add_argument("--prefer-carrier", choices=["electron-like", "hole-like"])
    parser.add_argument("--temperature-k", type=float, default=300.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze_cases(
        [Path(path).expanduser().resolve() for path in args.paths],
        args.occupied_bands,
        args.fermi,
        args.target_gap_min,
        args.target_gap_max,
        args.prefer_carrier,
        args.temperature_k,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
