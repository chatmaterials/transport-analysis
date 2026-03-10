---
name: "transport-analysis"
description: "Use when the task is to analyze transport-relevant quantities from DFT-derived results, including carrier-type tendency, effective-mass estimates, simple DOS-informed transport trends, multi-candidate ranking, and compact markdown reports from finished calculations."
---

# Transport Analysis

Use this skill for transport-oriented post-processing rather than generic workflow setup.

## When to use

- estimate whether the electronic structure suggests electron- or hole-like transport tendency
- estimate an effective mass from a simple band-edge dispersion
- summarize a transport trend from band-edge and DOS information
- rank multiple candidate datasets with a compact screening heuristic
- write a compact transport-analysis report from existing data

## Use the bundled helpers

- `scripts/analyze_carrier_type.py`
  Estimate a carrier-type tendency from a band structure and Fermi level.
- `scripts/analyze_effective_mass.py`
  Estimate an effective mass from a simple band-edge dispersion.
- `scripts/analyze_transport_trend.py`
  Summarize a simple transport trend from band-edge and DOS information.
- `scripts/compare_transport_candidates.py`
  Rank multiple candidate datasets with a compact gap-plus-mass screening heuristic.
- `scripts/export_transport_report.py`
  Export a markdown transport-analysis report.

## Guardrails

- Treat these outputs as compact descriptors, not a full Boltzmann transport workflow.
- State the assumed Fermi level and occupied-band count explicitly.
- Distinguish qualitative trend analysis from quantitative transport coefficients.
