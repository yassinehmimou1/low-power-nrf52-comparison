# Validation status — PCA10040 migration (2026-11-19)

| Item | Status |
|---|---|
| Source targets | **Changed** from PCA10056/nRF52840 to PCA10040/nRF52832 |
| System OFF BUTTON1 | **Source updated** to P0.13 (previously P0.11) |
| System ON LED1 | **Source updated** to P0.17 (previously P0.13) |
| nRF5 SDK startup/linker | **Source updated** for nRF52832 XXAA, 512 KiB Flash, 64 KiB RAM |
| Zephyr target | **Changed** to `nrf52dk/nrf52832` |
| Historical values | **Author-reported** 4.7 / 3.6 / 4.3 µA; raw traces not included |
| Python tests | Run `python -m unittest discover -s tests -v`; record local result |
| ARM bare-metal builds | **Not performed** — nRF5 SDK and cross-compiler unavailable in this environment |
| Zephyr builds | **Not performed** — Zephyr v3.7 workspace/SDK unavailable |
| PCA10040 flashing | **Not performed** — physical board unavailable |
| Reproduction of historical currents | **Not independently verified** |

This repository does not claim that the reconstructed System OFF retention configurations are identical to the original flashed firmware. Static review and Python tests cannot replace cross-compilation and physical validation.
