#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_carrier_type import analyze as analyze_carrier
from analyze_effective_mass import analyze as analyze_mass


def analyze_dos(path: Path) -> dict[str, float]:
    rows = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        rows.append((float(parts[0]), float(parts[1])))
    if not rows:
        raise SystemExit("DOS file contains no data")
    nearest = min(rows, key=lambda item: abs(item[0]))
    return {"dos_at_fermi": nearest[1]}


def analyze(band_path: Path, dos_path: Path, occupied_bands: int, fermi: float, mass_path: Path | None) -> dict[str, object]:
    carrier = analyze_carrier(band_path, occupied_bands, fermi)
    dos = analyze_dos(dos_path)
    mass = analyze_mass(mass_path) if mass_path else None
    if dos["dos_at_fermi"] < 1e-6:
        regime = "semiconducting"
    else:
        regime = "metallic-like"
    mobility_hint = None
    if mass and mass["effective_mass_me"] is not None:
        mobility_hint = "lighter carriers" if abs(mass["effective_mass_me"]) < 1.0 else "heavier carriers"
    mass_value = abs(mass["effective_mass_me"]) if mass and mass["effective_mass_me"] is not None else None
    quality_score = 0.0
    if regime == "semiconducting":
        quality_score = float(carrier["band_gap_eV"]) / ((mass_value if mass_value is not None else 2.0) * (1.0 + dos["dos_at_fermi"]))
    if regime == "metallic-like":
        screening_class = "degenerate-metal-like"
    elif quality_score >= 0.3:
        screening_class = "promising-semiconductor-like"
    elif quality_score >= 0.1:
        screening_class = "moderate-semiconductor-like"
    else:
        screening_class = "limited-semiconductor-like"
    activation = float(carrier["activation_energy_eV"])
    if activation <= 0.15:
        dopability_hint = "easy-to-activate"
    elif activation <= 0.35:
        dopability_hint = "moderately-activated"
    else:
        dopability_hint = "deep-fermi-level"
    return {
        "carrier_tendency": carrier["carrier_tendency"],
        "band_gap_eV": carrier["band_gap_eV"],
        "activation_energy_eV": carrier["activation_energy_eV"],
        "dos_at_fermi": dos["dos_at_fermi"],
        "regime": regime,
        "effective_mass_me": mass["effective_mass_me"] if mass else None,
        "mobility_hint": mobility_hint,
        "thermoelectric_quality_score": quality_score,
        "screening_class": screening_class,
        "dopability_hint": dopability_hint,
        "observations": ["Transport tendency summarized from band-edge position, DOS at the Fermi level, and optional effective mass."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a simple transport trend from band and DOS data.")
    parser.add_argument("--band-path", required=True)
    parser.add_argument("--dos-path", required=True)
    parser.add_argument("--mass-path")
    parser.add_argument("--occupied-bands", type=int, default=2)
    parser.add_argument("--fermi", type=float, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(
        Path(args.band_path).expanduser().resolve(),
        Path(args.dos_path).expanduser().resolve(),
        args.occupied_bands,
        args.fermi,
        Path(args.mass_path).expanduser().resolve() if args.mass_path else None,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
