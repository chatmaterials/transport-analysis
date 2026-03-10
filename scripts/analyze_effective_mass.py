#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


HBAR2_OVER_ME = 7.619964231


def solve_3x3(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    a = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    n = 3
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(a[r][i]))
        a[i], a[pivot] = a[pivot], a[i]
        factor = a[i][i]
        if abs(factor) < 1e-14:
            raise SystemExit("Singular matrix in effective-mass fit")
        for j in range(i, n + 1):
            a[i][j] /= factor
        for r in range(n):
            if r == i:
                continue
            scale = a[r][i]
            for j in range(i, n + 1):
                a[r][j] -= scale * a[i][j]
    return [a[i][n] for i in range(n)]


def analyze(path: Path) -> dict[str, object]:
    rows = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        rows.append((float(parts[0]), float(parts[1])))
    if len(rows) < 3:
        raise SystemExit("At least three (k,E) points are required")
    s_k4 = sum(k**4 for k, _ in rows)
    s_k3 = sum(k**3 for k, _ in rows)
    s_k2 = sum(k**2 for k, _ in rows)
    s_k1 = sum(k for k, _ in rows)
    s_e = sum(e for _, e in rows)
    s_k2e = sum(k * k * e for k, e in rows)
    s_ke = sum(k * e for k, e in rows)
    a, b, c = solve_3x3(
        [
            [s_k4, s_k3, s_k2],
            [s_k3, s_k2, s_k1],
            [s_k2, s_k1, float(len(rows))],
        ],
        [s_k2e, s_ke, s_e],
    )
    curvature = 2.0 * a
    effective_mass = HBAR2_OVER_ME / curvature if abs(curvature) > 1e-14 else None
    mass_magnitude = abs(effective_mass) if effective_mass is not None else None
    if mass_magnitude is None:
        mobility_class = None
    elif mass_magnitude < 0.5:
        mobility_class = "very-light"
    elif mass_magnitude < 1.5:
        mobility_class = "light"
    elif mass_magnitude < 5.0:
        mobility_class = "moderate"
    else:
        mobility_class = "heavy"
    return {
        "path": str(path),
        "curvature_eV_A2": curvature,
        "effective_mass_me": effective_mass,
        "mass_magnitude_me": mass_magnitude,
        "band_edge_type": "conduction-like" if curvature > 0 else "valence-like",
        "mobility_class": mobility_class,
        "band_edge_energy_eV": c,
        "observations": ["Effective mass estimated from a quadratic fit around the sampled band edge."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate an effective mass from a band-edge dispersion.")
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.path).expanduser().resolve())
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
