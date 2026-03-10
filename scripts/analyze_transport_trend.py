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
    return {
        "carrier_tendency": carrier["carrier_tendency"],
        "band_gap_eV": carrier["band_gap_eV"],
        "dos_at_fermi": dos["dos_at_fermi"],
        "regime": regime,
        "effective_mass_me": mass["effective_mass_me"] if mass else None,
        "mobility_hint": mobility_hint,
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
