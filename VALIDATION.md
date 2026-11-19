# Validation status — 2026-11-19

| Item | Status |
|---|---|
| Python unit tests | **10 passed** (`python -m unittest discover -s tests -v`) |
| Community-reference calculations | **Checked** (-8.5% and +19.4%, rounded to 1 decimal) |
| Bare-metal Makefile parsing | **Checked** with `make -n` using a placeholder SDK path |
| Bare-metal System OFF build | **Not run** — nRF5 SDK and ARM cross-compiler unavailable in this environment |
| Zephyr System OFF build | **Not run** — Zephyr v3.7 workspace and SDK unavailable in this environment |
| Firmware flashing on PCA10056 | **Not run** — no physical board attached |
| Physical current measurements | **Not performed** |

The `analysis/reference_values.csv` file contains **user-provided, community-reported numbers**, not measurements from this repository. The System OFF code is an engineering starting point and may require target-specific debugging/adjustment after real compilation and testing. This file intentionally does not claim hardware validation.
