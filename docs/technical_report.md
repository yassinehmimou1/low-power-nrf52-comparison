# Technical Report — Low-Power Firmware Comparison on nRF52840

**Status:** implementation package prepared; hardware validation and physical measurements pending.

## 1. Abstract

This project defines a controlled comparison between a register-level bare-metal firmware and a Zephyr RTOS application on the Nordic nRF52840 DK. Both execute a periodic wake-up scenario, toggle a timing marker, run a deterministic CPU workload and return to System ON idle. The purpose is to compare energy use and engineering trade-offs while preserving experimental traceability.

## 2. Hardware and software configuration

- Board: Nordic nRF52840 DK, PCA10056 (record PCB revision during testing).
- SoC: nRF52840, ARM Cortex-M4F, 1 MiB Flash, 256 KiB RAM.
- Bare-metal dependency: nRF5 SDK 17.1.0 (external), ARM GNU toolchain (record exact version).
- RTOS: Zephyr v3.7.0, board target `nrf52840dk/nrf52840`.
- Measurement instrument: **TBD — record model, firmware/software version and calibration status**.

## 3. Workload and architecture

Nominal period: 5,000 ms. Optional LED pulse: 50 ms. Shared CPU workload: 4,096 integer iterations. Bare-metal uses RTC2 compare interrupts and `WFE`; Zephyr uses `k_timer`, a semaphore and the kernel idle thread. P0.03 is the external timing marker.

## 4. Build and validation status

| Item | Status |
|---|---|
| Source files generated | Yes |
| API/configuration review | Static review only; local build required |
| Bare-metal compile | Not verified in this environment |
| Zephyr compile | Not verified in this environment |
| Flashing | Not performed |
| Functional board tests | Not performed |
| Current measurements | Not performed |
| Python analysis unit tests | Run locally and record result before publication |

## 5. Experimental results

No physical measurements are included. Populate the following table only after the test plan is completed.

| Metric | Bare-metal | Zephyr | Notes / run IDs |
|---|---:|---:|---|
| Mean current | TBD | TBD | Real capture only |
| Idle current | TBD | TBD | LED disabled |
| Active peak current | TBD | TBD | State sample rate and instrument range |
| Wake-to-marker latency | TBD | TBD | Distribution across events |
| Energy per cycle | TBD | TBD | Trapezoidal integration |
| Ideal autonomy | TBD | TBD | State battery capacity and assumptions |

## 6. Discussion framework

Discuss measured results only after validating the capture. Explain differences in timer backend, scheduler and synchronization overhead. Separate SoC current from DK-level current. If the measured difference is within instrument uncertainty or run-to-run spread, state that the experiment does not establish a meaningful difference.

## 7. Limitations

- The DK is not a production battery-powered design.
- The LED and debug interface can dominate current.
- The Zephyr and bare-metal timer backends differ.
- The battery-life equation ignores derating, regulator efficiency and cell self-discharge.
- The benchmark measures System ON idle, not System OFF.
- Compilation and hardware execution remain to be verified on the target setup.

## 8. Conclusion

**Pending real build and measurement evidence.** Do not write a conclusion claiming that one architecture consumes less power until repeated physical measurements support it.
