# transport-analysis

[![CI](https://img.shields.io/github/actions/workflow/status/chatmaterials/transport-analysis/ci.yml?branch=main&label=CI)](https://github.com/chatmaterials/transport-analysis/actions/workflows/ci.yml) [![Release](https://img.shields.io/github/v/release/chatmaterials/transport-analysis?display_name=tag)](https://github.com/chatmaterials/transport-analysis/releases)

Standalone skill for transport-relevant DFT result analysis, including thermoelectric-style screening descriptors, bipolar-risk checks, and batch candidate ranking.

## Install

```bash
npx skills add chatmaterials/transport-analysis -g -y
```

## Local Validation

```bash
python3 -m py_compile scripts/*.py
npx skills add . --list
python3 scripts/analyze_carrier_type.py fixtures/band/bands.dat --occupied-bands 2 --fermi 0.35 --json
python3 scripts/analyze_bipolar_risk.py fixtures/band/bands.dat --occupied-bands 2 --fermi 0.35 --temperature-k 300 --json
python3 scripts/analyze_effective_mass.py fixtures/effective_mass/effective_mass.dat --json
python3 scripts/analyze_transport_trend.py --band-path fixtures/band/bands.dat --dos-path fixtures/dos/dos.dat --occupied-bands 2 --fermi 0.35 --temperature-k 300 --json
python3 scripts/compare_transport_candidates.py fixtures fixtures/candidates/heavy fixtures/candidates/narrow-gap fixtures/candidates/metallic --occupied-bands 2 --fermi 0.35 --target-gap-min 0.5 --target-gap-max 1.0 --prefer-carrier electron-like --temperature-k 300 --json
python3 scripts/export_transport_report.py --band-path fixtures/band/bands.dat --dos-path fixtures/dos/dos.dat --mass-path fixtures/effective_mass/effective_mass.dat --occupied-bands 2 --fermi 0.35 --temperature-k 300
python3 scripts/run_regression.py
```
