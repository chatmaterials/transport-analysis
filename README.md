# transport-analysis

Standalone skill for transport-relevant DFT result analysis.

## Install

```bash
npx skills add chatmaterials/transport-analysis -g -y
```

## Local Validation

```bash
python3 -m py_compile scripts/*.py
npx skills add . --list
python3 scripts/analyze_carrier_type.py fixtures/band/bands.dat --occupied-bands 2 --fermi 0.35 --json
python3 scripts/analyze_effective_mass.py fixtures/effective_mass/effective_mass.dat --json
python3 scripts/analyze_transport_trend.py --band-path fixtures/band/bands.dat --dos-path fixtures/dos/dos.dat --occupied-bands 2 --fermi 0.35 --json
python3 scripts/export_transport_report.py --band-path fixtures/band/bands.dat --dos-path fixtures/dos/dos.dat --mass-path fixtures/effective_mass/effective_mass.dat --occupied-bands 2 --fermi 0.35
python3 scripts/run_regression.py
```
