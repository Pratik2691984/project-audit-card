# Project Audit Card

A Pāṇinian computational linguistics engine with supporting audit tooling.

## What exists

- core/linguistics/prosody/ — Piṅgala meter scansion (L/G weights, gaṇa decomposition, wildcard cadence matching, verse scanner)
- core/linguistics/ast/ — Śivasūtra pratyāhāra expansion, sandhi (ac/hal/visarga), Pāṇinian derivation tree
- core/linguistics/prakriya/ — tiṅanta conjugation engine (all 10 gaṇas: Bhvādi through Curādi; parasmaipada present active)
- udit_manifest.json — **spec only.** Describes 40 research projects; none exist on disk
- src/ — React audit dashboard (renders the manifest)

## Run tests

    python -m unittest discover -s tests/linguistics -p "test_*.py" -v

## Build dashboard

    npm ci
    npm run build

## Status

81 tests green. All 10 classical gaṇas implemented for laṭ parasmaipada. Ātmanepada and other lakāras not yet implemented.