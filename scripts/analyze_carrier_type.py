#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_bands(path: Path) -> list[tuple[float, list[float]]]:
    rows = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        rows.append((float(parts[0]), [float(x) for x in parts[1:]]))
    if not rows:
        raise SystemExit("Band file contains no data")
    return rows


def analyze(path: Path, occupied_bands: int, fermi: float) -> dict[str, object]:
    rows = read_bands(path)
    vbm = max((energies[occupied_bands - 1], k) for k, energies in rows)
    cbm = min((energies[occupied_bands], k) for k, energies in rows)
    dv = abs(fermi - vbm[0])
    dc = abs(cbm[0] - fermi)
    if abs(dv - dc) < 1e-12:
        carrier = "ambiguous"
    elif dc < dv:
        carrier = "electron-like"
    else:
        carrier = "hole-like"
    return {
        "path": str(path),
        "fermi_eV": fermi,
        "vbm_eV": vbm[0],
        "cbm_eV": cbm[0],
        "band_gap_eV": cbm[0] - vbm[0],
        "carrier_tendency": carrier,
        "observations": ["Carrier-type tendency estimated from the relative position of the Fermi level and band edges."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate a carrier-type tendency from band edges.")
    parser.add_argument("path")
    parser.add_argument("--occupied-bands", type=int, default=2)
    parser.add_argument("--fermi", type=float, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.path).expanduser().resolve(), args.occupied_bands, args.fermi)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
