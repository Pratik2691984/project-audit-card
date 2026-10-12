# Project Audit Card & Computational Linguistics Engine

A multi-disciplinary research workspace combining metadata specification tooling for portfolio audit tracking with formal implementations of classical Sanskrit grammar (*Śāstra*) and prosody (*Chhandas*).

---

## 1. What Exists on Disk (Active Implementations)

The core active development lives in `core/` and `tests/`:

* **Pāṇinian AST & Sandhi Engine (`core/linguistics/ast/`)**:
  * **Ac-Sandhi (Vowels)**: 6.1.101 (*akaḥ savarṇe dīrghaḥ*), 6.1.109 (*eṅaḥ padāntād ati*), 6.1.88 (*vṛddhir eci*), 6.1.87 (*ād guṇaḥ* with 1.1.51 *uraṇ raparaḥ*), 6.1.78 (*eco'yavāyāvaḥ*), 6.1.77 (*iko yaṇaci*), and 8.3.19 (*lopaḥ śākalyasya* with *asiddhatva* blocking secondary sandhi).
  * **Adhikāra Provenance**: 6.1.84 (*ekaḥ pūrvaparayoḥ*) tracked explicitly on `DerivationStep` records.
  * **Hal-Sandhi (Consonants)**: 8.4.40 (*stoḥ ścunā ścuḥ*) and 8.4.41 (*ṣṭunā ṣṭuḥ*).
  * **Visarga-Sandhi**: 8.2.66 (*sasajuṣo ruḥ*), 6.1.113 (*ato ror aplutād aplute*), 6.1.114 (*haśi ca*), and 8.3.17 (*bhobhagoaghopūrvasya yo'śi*).
* **Pāṇinian Prakriyā Engine (`core/linguistics/prakriya/`)**:
  * Step-by-step morphosyntactic derivation tracking from root (*dhātu*) and lakāra to inflected verbal forms (*tiṅanta*).
* **Piṅgala Prosody Engine (`core/linguistics/prosody/`)**:
  * Laghu-Guru weight determination, *trika-gaṇa* decomposition, verse segmentation, Anuṣṭubh cadence validation, and Toṭaka meter recognition.
* **Śivasūtra Engine (`core/linguistics/ast/sivasutras.py`)**:
  * Canonical Pāṇinian *anubandha* / *it* marker resolution and arbitrary *pratyāhāra* expansion (`ac`, `hal`, `ik`, `yaṇ`, `ec`, `yañ`, `al`).

---

## 2. Specification Only (Portfolio Manifest)

* `audit_manifest.json` and `src/data/initialProjects.ts` specify the portfolio taxonomy and audit schema across 40 research projects (19 baseline + 14 batch-promoted + experimental tracks). 
* The corresponding external project subdirectories are managed in separate repositories and documented here as metadata specifications.

---

## 3. How to Run & Verify

### Run the Linguistics Test Suite
```bash
python -m unittest discover -s tests/linguistics -p "test_*.py" -v