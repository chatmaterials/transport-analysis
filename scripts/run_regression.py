#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=True)


def run_json(*args: str):
    return json.loads(run(*args).stdout)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    carrier = run_json("scripts/analyze_carrier_type.py", "fixtures/band/bands.dat", "--occupied-bands", "2", "--fermi", "0.35", "--json")
    ensure(carrier["carrier_tendency"] == "electron-like", "transport-analysis should identify an electron-like tendency")
    mass = run_json("scripts/analyze_effective_mass.py", "fixtures/effective_mass/effective_mass.dat", "--json")
    ensure(abs(mass["effective_mass_me"] - 1.90499105775) < 1e-3, "transport-analysis should estimate the effective mass")
    trend = run_json("scripts/analyze_transport_trend.py", "--band-path", "fixtures/band/bands.dat", "--dos-path", "fixtures/dos/dos.dat", "--mass-path", "fixtures/effective_mass/effective_mass.dat", "--occupied-bands", "2", "--fermi", "0.35", "--json")
    ensure(trend["regime"] == "semiconducting", "transport-analysis should identify a semiconducting regime")
    temp_dir = Path(tempfile.mkdtemp(prefix="transport-analysis-report-"))
    try:
        report_path = Path(
            run(
                "scripts/export_transport_report.py",
                "--band-path",
                "fixtures/band/bands.dat",
                "--dos-path",
                "fixtures/dos/dos.dat",
                "--mass-path",
                "fixtures/effective_mass/effective_mass.dat",
                "--occupied-bands",
                "2",
                "--fermi",
                "0.35",
                "--output",
                str(temp_dir / "TRANSPORT_REPORT.md"),
            ).stdout.strip()
        )
        report_text = report_path.read_text()
        ensure("# Transport Analysis Report" in report_text, "transport report should have a heading")
        ensure("## Carrier Type" in report_text and "## Effective Mass" in report_text, "transport report should include carrier and mass sections")
    finally:
        shutil.rmtree(temp_dir)
    print("transport-analysis regression passed")


if __name__ == "__main__":
    main()
