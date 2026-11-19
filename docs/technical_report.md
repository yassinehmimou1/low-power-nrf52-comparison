# Technical report — PCA10040 / nRF52832

## Scope

Two separate firmware experiments on Nordic nRF52 DK **PCA10040**, targeting the **nRF52832 XXAA** (512 KiB Flash, 64 KiB RAM):

1. **System OFF**: static deep-sleep comparison across three firmware configurations, BUTTON1 P0.13 wake-by-reset. The author reports 4.7 µA (bare-metal standard), 3.6 µA (bare-metal optimized) and 4.3 µA (Zephyr). The raw acquisition traces and original firmware build artifacts have not yet been provided; the current firmware is a reconstruction.
2. **System ON Idle**: periodic 5 s RTC2 / Zephyr timer wake, common CPU workload, P0.03 marker, optional P0.17 LED. No measured currents are supplied for this experiment.

## Historical System OFF results (author-reported)

| Variant | Reported current | Trace status |
|---|---:|---|
| Bare-metal standard | 4.7 µA | Original raw trace not included |
| Bare-metal optimized | 3.6 µA | Original raw trace not included |
| Zephyr RTOS | 4.3 µA | Original raw trace not included |

Comparisons: Zephyr vs standard **−8.5%**, Zephyr vs optimized **+19.4%**. These are arithmetic comparisons of reported steady-state currents, not evidence of RTOS scheduler overhead or energy per cycle.

## Firmware and validation

- Bare-metal: nRF5 SDK 17.1.0 + ARM GNU toolchain, startup `gcc_startup_nrf52.S`, SoC `NRF52832_XXAA`.
- Zephyr: v3.7.0, board target `nrf52dk/nrf52832`.
- GPIO: BUTTON1 P0.13, LED1 P0.17, marker P0.03.
- Compilation, flashing and measured-current reproduction **pending on physical PCA10040**. See `../VALIDATION.md`.

## Experimental limitations and next steps

Document instrument and calibration, PCB revision, voltage, temperature, SoC current supply path, firmware binary hashes and raw traces. Repeat at least five runs per firmware. The current code toggles one RAM retention section to illustrate a reproducible configuration difference; it does **not** establish that this was the only difference in the historical experiment.

For System ON, measure active/idle current, wake-to-marker latency and energy per cycle using a suitable profiler and the shared workload. Do not infer full battery life from System OFF current alone.
