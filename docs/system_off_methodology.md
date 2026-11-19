# System OFF measurement methodology — PCA10040

## Hardware and provenance

The project author reports System OFF measurements on a Nordic nRF52 DK **PCA10040** (nRF52832): 4.7 µA (bare-metal standard), 3.6 µA (bare-metal optimized), and 4.3 µA (Zephyr). These are **author-reported historical results**; no original instrument exports or original flashed binaries are supplied in this repository. The current sources are a reconstruction intended to support reproduction, not a verified match to the original test.

Record before attempting to reproduce: PCB revision, nRF52832 chip variant, instrument model and calibration, source voltage, temperature, supply jumper/solder bridge configuration, firmware commit and binary SHA256, SDK/compiler versions, Zephyr version, GPIO and RAM retention registers, logging/debugger state, and capture settings.

## Experimental protocol

1. Build the three PCA10040-targeted System OFF variants. Record firmware hashes.
2. Program the first firmware. Remove debugger/USB and any unintended external loads in accordance with the **PCA10040** revision-specific current measurement instructions.
3. Wire the profiler in **series** with the SoC supply path, never across the supply. Confirm correct polarity, voltage and current limits.
4. Verify BUTTON1 on **P0.13** wakes the device via reset; allow it to re-enter System OFF after release.
5. Capture stable System OFF current for at least 60 s, excluding startup/reset/button transients.
6. Repeat at least five times at the same voltage and temperature; preserve raw exports and per-run metadata.
7. Repeat the same setup for the other two firmware variants; do not change wiring or profiler settings.
8. Calculate run means, median, standard deviation and uncertainty. Compare with historical author-reported numbers, but do not assume the reconstructed retention settings exactly match the original firmware.

## Reported results and calculations

| Variant | Current | Provenance |
|---|---:|---|
| Bare-metal standard | 4.7 µA | Author-reported PCA10040 measurement; raw trace pending |
| Bare-metal optimized | 3.6 µA | Author-reported PCA10040 measurement; raw trace pending |
| Zephyr System OFF | 4.3 µA | Author-reported PCA10040 measurement; raw trace pending |

Zephyr versus standard: `(4.3/4.7 - 1)*100 = -8.51%`.  
Zephyr versus optimized: `(4.3/3.6 - 1)*100 = +19.44%`.

These values characterize *steady-state System OFF*, not scheduler cost, wake latency, or full-cycle battery life. To compare scheduler and wake energy, use the separate System ON Idle experiment.

## Raw evidence to add when available

Place original acquisition exports in `measurements/raw/` (if suitable for publication), plus a run manifest documenting board revision, instrument, voltage, temperature, build hashes, retention registers and sampling rate. Do not synthesize traces to match the three summary numbers.
