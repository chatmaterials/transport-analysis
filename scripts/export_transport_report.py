#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from analyze_carrier_type import analyze as analyze_carrier
from analyze_effective_mass import analyze as analyze_mass
from analyze_transport_trend import analyze as analyze_trend


def render_markdown(carrier: dict[str, object], mass: dict[str, object] | None, trend: dict[str, object]) -> str:
    lines = [
        "# Transport Analysis Report",
        "",
        "## Carrier Type",
        f"- Carrier tendency: `{carrier['carrier_tendency']}`",
        f"- Band gap (eV): `{carrier['band_gap_eV']:.4f}`",
        "",
        "## Transport Trend",
        f"- Regime: `{trend['regime']}`",
        f"- DOS at Fermi: `{trend['dos_at_fermi']:.4f}`",
    ]
    if mass is not None:
        lines.extend(
            [
                "",
                "## Effective Mass",
                f"- Effective mass (m_e): `{mass['effective_mass_me']:.4f}`",
                f"- Curvature (eV A^-2): `{mass['curvature_eV_A2']:.4f}`",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a markdown transport-analysis report.")
    parser.add_argument("--band-path", required=True)
    parser.add_argument("--dos-path", required=True)
    parser.add_argument("--mass-path")
    parser.add_argument("--occupied-bands", type=int, default=2)
    parser.add_argument("--fermi", type=float, required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    band_path = Path(args.band_path).expanduser().resolve()
    dos_path = Path(args.dos_path).expanduser().resolve()
    carrier = analyze_carrier(band_path, args.occupied_bands, args.fermi)
    mass = analyze_mass(Path(args.mass_path).expanduser().resolve()) if args.mass_path else None
    trend = analyze_trend(band_path, dos_path, args.occupied_bands, args.fermi, Path(args.mass_path).expanduser().resolve() if args.mass_path else None)
    output = Path(args.output).expanduser().resolve() if args.output else Path.cwd() / "TRANSPORT_REPORT.md"
    output.write_text(render_markdown(carrier, mass, trend))
    print(output)


if __name__ == "__main__":
    main()
