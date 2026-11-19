# Measurement protocol — System OFF on nRF52840 DK

## Objective and scope

Compare steady-state **System OFF** current under three documented software configurations on **the same nRF52840 DK (PCA10056)**. This is distinct from the 5 s RTC-driven **System ON Idle** experiment elsewhere in this repository.

## Preconditions

- Record the board's **actual PCB reference** (PCA10056), revision, supply path and regulator settings. The image supplied for the LinkedIn post appears to show **PCA10040** (nRF52 DK), not PCA10056. Do not use it as proof of tests on nRF52840.
- Confirm the current-sense jumpers/solder bridges in the official manual for that revision. Do not cut or modify bridges without checking the revision.
- Record firmware commit, SDK version, compiler version, optimization flags, supply voltage, ambient temperature, instrument, sample rate and wiring.
- Use the same supply voltage, physical DK, instrument, and wake source for every run.
- Remove the USB/debugger connection from the measurement path where required; do not assume USB-supplied DK current equals MCU current.

## Capture sequence

1. Build and flash `system-off/bare-metal` with `RETAIN_RAM_SECTION0=1`.
2. Connect the profiler according to the Nordic current-measurement guide.
3. Let the MCU enter System OFF; verify with a power trace. Do **not** include reset/boot transient in the steady-state average.
4. Record at least 60 s of stable System OFF current and save the raw instrument export.
5. Repeat at least 5 times, recording mean, median, standard deviation, supply voltage and measurement uncertainty.
6. Repeat with `RETAIN_RAM_SECTION0=0`, then with `system-off/zephyr`, without changing the measurement circuit.
7. Press BUTTON1 to verify wake-by-reset, and document the transient separately.
8. Report each firmware's measured current with run IDs, raw CSV traces and the full hardware/software configuration.

## Reported reference numbers from the LinkedIn graphic

| Label in post | Current | Origin | Status |
|---|---:|---|---|
| Bare-metal standard | 4.7 µA | User-provided graphic; attributed to Nordic community | **Not verified on this repository's firmware** |
| Bare-metal optimized | 3.6 µA | User-provided graphic; attributed to Nordic community | **Not verified on this repository's firmware** |
| Zephyr RTOS System OFF | 4.3 µA | User-provided graphic; attributed to Nordic community | **Not verified on this repository's firmware** |

Difference vs standard: `(4.3/4.7 - 1)*100 = -8.51%`.
Difference vs optimized: `(4.3/3.6 - 1)*100 = +19.44%`.

The provenance of the community figures has not been independently confirmed. **Do not present them as measurements taken with this repository.** There is no established one-to-one mapping between the figures and the retention configuration implemented here.

## Scientific caveat

A static System OFF current measurement cannot by itself quantify RTOS overhead, CPU wake latency, or battery autonomy. For meaningful power comparison of software execution, also measure energy per complete wake/active/sleep cycle using the existing System ON experiment.

## Useful official references

- [Nordic nRF52840 POWER](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/power.html)
- [nRF52840 DK current measurement](https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/hw_measure_current.html)
- [Zephyr 3.7 power-off API](https://docs.zephyrproject.org/3.7.0/)
