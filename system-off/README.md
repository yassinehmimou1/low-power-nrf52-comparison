# System OFF — three firmware configurations

**Target hardware:** Nordic nRF52840 DK / PCA10056. **Status:** source code prepared; firmware builds, flashes and current readings **not yet verified on physical hardware**.

This experiment complements, rather than replaces, the original `bare-metal/` and `zephyr/` periodic **System ON Idle** examples.

## What the code actually does

| Configuration | Source | System OFF entry | RAM0 section S0 retention | Wake source |
|---|---|---|---|---|
| Bare-metal standard (retention baseline) | `bare-metal/src/main.c` | `NRF_POWER->SYSTEMOFF` | Explicitly **on** | BUTTON1 P0.11, low-level SENSE |
| Bare-metal optimized (no S0 retention) | Same source, `RETAIN_RAM_SECTION0=0` | `NRF_POWER->SYSTEMOFF` | Explicitly **off** | BUTTON1 P0.11, low-level SENSE |
| Zephyr RTOS System OFF | `zephyr/src/main.c` | Zephyr `sys_poweroff()` | Explicitly **off** | BUTTON1 P0.11, low-level SENSE |

**Important:** `standard` here names the **retention-enabled reference configuration**, not a claim about the Nordic reset defaults. Only the retention bit for RAM0/S0 is deliberately changed; this is not a comprehensive board-level optimization. Other retention fields may differ depending on startup/SDK, so inspect the effective register values when benchmarking.

System OFF is *not* a periodic sleep state: the RTC is not running as a wake source. Pressing BUTTON1 resets the SoC and runs `main()` again. The boot/re-entry interval must be excluded from a steady-state System OFF current average.

The code does not aim to reproduce the 4.7/3.6/4.3 µA numbers. Those values are **user-supplied, community-reported references**, not outputs of these programs.

## Build (requires external toolchains)

Bare-metal — nRF5 SDK 17.1.0 + GNU Arm Embedded:

```bash
cd system-off/bare-metal
make SDK_ROOT=/absolute/path/to/nRF5_SDK_17.1.0 RETAIN_RAM_SECTION0=1
make SDK_ROOT=/absolute/path/to/nRF5_SDK_17.1.0 RETAIN_RAM_SECTION0=0
```

Outputs: `build/retention_1/system_off_bare_metal.hex` and `build/retention_0/system_off_bare_metal.hex`.

Zephyr v3.7.0 (in an initialized workspace):

```bash
west build -b nrf52840dk/nrf52840 /absolute/path/to/repo/system-off/zephyr -d build/system-off-zephyr
```

On Windows PowerShell, replace Unix-style paths with appropriate Windows paths and run from the Zephyr workspace or a configured shell.

## Flash and observe

```bash
nrfjprog --family NRF52 --program system-off/bare-metal/build/retention_1/system_off_bare_metal.hex --verify --reset
# OR for Zephyr:
west flash -d build/system-off-zephyr
```

1. Program one firmware. Disconnect the debug/programming path as required by the official DK current measurement guide.
2. Wire the power profiler **in series** with the SoC current measurement path; follow the specific board revision manual.
3. Wait until startup completes and the chip enters System OFF. Record current after settling, not during boot.
4. Press BUTTON1: the SoC resets; release it to let the firmware re-enter System OFF.
5. Capture at least five steady-state runs per firmware, at a fixed voltage and temperature, and preserve the raw trace.
6. Check the effect of the DK interface MCU, debugger, regulators, pull-ups and current measurement wiring. The DK board current is not necessarily the bare SoC current.

**Safety:** never place a current-mode meter directly across a voltage source.

## Interpretation

System OFF removes almost all runtime activity. A difference between firmware variants in this state is mainly due to *persistent hardware state* (retention, GPIO, wake circuitry, external board loads), not scheduler overhead while the CPU is off. For RTOS scheduling overhead, use the existing **System ON Idle** experiment.

See `../docs/system_off_methodology.md` and `../analysis/reference_values.csv`.
