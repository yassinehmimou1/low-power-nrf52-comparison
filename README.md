# Low-Power Embedded Firmware — Bare-Metal vs Zephyr RTOS on Nordic nRF52

A reproducible firmware study comparing a register-level bare-metal implementation with a Zephyr RTOS implementation on the **Nordic nRF52840 DK (PCA10056)**.

> **Measurement integrity:** this repository contains no claimed hardware measurements. The CSV template is empty. The optional example dataset is explicitly labelled `SIMULATED` and exists only to demonstrate the analysis script. Replace it with measurements captured on your own hardware before publishing numerical conclusions.

## Project overview

Both firmware variants execute the same workload:

1. Wait for a periodic event (default: every 5,000 ms).
2. Wake the CPU from System ON idle.
3. Assert a measurement marker GPIO while executing a deterministic CPU workload.
4. Optionally illuminate LED1 for 50 ms (`SCENARIO_LED` / `SCENARIO_LED_ENABLE`).
5. Return to idle until the next RTC/kernel-timer event.

The marker on **P0.03 (Arduino A0)** is intended for oscilloscope or logic-analyzer timing. LED1 is **P0.13, active-low**. Disable the LED during low-current measurements if its current would dominate the MCU measurement; use the same setting for both firmware variants.

## Objectives

- Compare a direct-register Cortex-M4 firmware with a Zephyr application.
- Understand RTC-driven wake-up and interrupt handling.
- Use Zephyr GPIO, kernel timer, semaphore, DeviceTree and Kconfig APIs.
- Measure active, idle and cycle energy without inventing data.
- Estimate battery life while documenting the limitations of the estimate.

## Hardware requirements

### Required

- **Nordic nRF52840 DK, PCA10056** (nRF52840 SoC, 1 MiB Flash, 256 KiB RAM, Cortex-M4F up to 64 MHz).
- USB cable for initial programming/debugging.
- External current measurement equipment for power results: preferably **Nordic Power Profiler Kit II (PPK2)**; a suitable power analyzer or calibrated shunt + oscilloscope can also be used.

### Board signals used

| Function | nRF52840 pin | DK mapping |
|---|---:|---|
| LED1 (optional) | P0.13 | Active-low green LED |
| Timing marker | P0.03 | Arduino A0 |
| RTC wake-up | RTC2 compare (bare-metal) | Internal peripheral; no external pin |
| Zephyr periodic tick | Zephyr system clock RTC driver | Internal peripheral; managed by Zephyr |

The board has external 32.768 kHz and 32 MHz oscillators. The bare-metal variant explicitly selects the 32.768 kHz crystal for LFCLK. Zephyr uses the board/SoC clock configuration.

### Current measurement on the DK

The nRF52840 DK exposes VDD current measurement through **P22**, with **SB40** and **R90** involved in the measurement path. Board revisions can differ: follow the Nordic DK user guide for the exact revision before cutting or modifying a solder bridge. The usual procedure isolates the SoC supply path, connects the measuring instrument in series at P22, and powers the board from a clean external source. Disconnect the interface-MCU USB after programming and avoid a serial terminal on the virtual COM port during measurement. Do not power the DUT through the debugger USB during precision measurements unless the official setup explicitly requires it.

**Safety:** do not connect a PPK2 or ammeter in current-measurement mode across a supply. Confirm polarity, voltage range and current limit before powering the board. Restore the solder bridge/jumper only as described by the board guide.

## Software requirements

### Common tools

- Git
- Python 3.9+
- CMake 3.20+ (only for the root host-side helper targets)
- ARM GNU Toolchain (`arm-none-eabi-gcc`, `arm-none-eabi-objcopy`, `arm-none-eabi-size`)
- SEGGER J-Link software / J-Link Commander or Nordic nRF Command Line Tools

### Bare-metal toolchain

- **nRF5 SDK 17.1.0** (external dependency; not redistributed here).
- ARM GNU Toolchain compatible with the SDK. A known nRF5 SDK-era toolchain is GNU Arm Embedded 10.3-2021.10; newer toolchains may work but must be verified locally.
- SDK paths expected by the Makefile: `modules/nrfx/mdk`, `components/toolchain/cmsis/include`, `modules/nrfx/mdk/gcc_startup_nrf52840.S`, and `modules/nrfx/mdk/system_nrf52840.c`.

### Zephyr toolchain

- Zephyr **v3.7.0** (pinned for reproducibility; hardware model v2 board name).
- West and the Zephyr workspace modules.
- Zephyr SDK 0.17.x or another Zephyr-supported ARM toolchain.
- Board target: `nrf52840dk/nrf52840`.

Zephyr v3.7.0 is deliberately pinned rather than using `latest`. If upgrading Zephyr, rebuild and revalidate the board target, Kconfig symbols, DeviceTree overlay and PM behavior.

## Repository architecture

```text
low-power-nrf52-comparison/
├── README.md
├── CMakeLists.txt
├── LICENSE
├── .gitignore
├── common/
│   ├── include/scenario.h
│   └── src/scenario.c
├── bare-metal/
│   ├── Makefile
│   ├── README.md
│   ├── include/app_config.h
│   ├── linker/nrf52840_xxaa.ld
│   └── src/main.c
├── zephyr/
│   ├── CMakeLists.txt
│   ├── Kconfig
│   ├── prj.conf
│   ├── README.md
│   ├── boards/nrf52840dk_nrf52840.overlay
│   └── src/main.c
├── analysis/
│   ├── power_analysis.py
│   ├── comparison.md
│   ├── equations.md
│   └── examples/simulated_example.csv
├── measurements/
│   ├── README.md
│   └── template.csv
├── tests/
│   ├── README.md
│   ├── test_plan.md
│   └── test_power_analysis.py
└── docs/
    ├── architecture.md
    ├── methodology.md
    └── technical_report.md
```

## Build instructions

### 1. Bare-metal firmware

Install nRF5 SDK 17.1.0 separately and set `SDK_ROOT` to its extracted directory.

Linux/macOS:

```bash
cd bare-metal
make SDK_ROOT=/absolute/path/to/nRF5_SDK_17.1.0
```

Windows users can use the ARM GNU toolchain from MSYS2, WSL or a compatible shell. The Makefile expects `arm-none-eabi-*` tools in `PATH`.

Build without LED current (recommended for the MCU low-power baseline):

```bash
make clean
make SDK_ROOT=/absolute/path/to/nRF5_SDK_17.1.0 SCENARIO_LED_ENABLE=0
```

Build with LED1 enabled for functional demonstration:

```bash
make clean
make SDK_ROOT=/absolute/path/to/nRF5_SDK_17.1.0 SCENARIO_LED_ENABLE=1
```

Output: `bare-metal/build/low_power_bare_metal.hex` and `.elf`.

### 2. Zephyr firmware

Create a Zephyr v3.7.0 workspace (the SDK and Zephyr source are not bundled):

```bash
python3 -m pip install --user west
west init -m https://github.com/zephyrproject-rtos/zephyr --mr v3.7.0 ~/zephyrproject
cd ~/zephyrproject
west update
west zephyr-export
python3 -m pip install -r zephyr/scripts/requirements.txt
```

Install and register the Zephyr SDK following the Zephyr v3.7.0 getting-started guide. Set `ZEPHYR_BASE` to `~/zephyrproject/zephyr` and build this repository's application:

```bash
export ZEPHYR_BASE="$HOME/zephyrproject/zephyr"
west build -b nrf52840dk/nrf52840 /absolute/path/to/low-power-nrf52-comparison/zephyr -d /absolute/path/to/low-power-nrf52-comparison/build/zephyr
```

For the benchmark configuration without LED load, edit `zephyr/prj.conf` and set `CONFIG_SCENARIO_LED=n`, then rebuild. For the functional LED demo, use `CONFIG_SCENARIO_LED=y`.

The build output is in `build/zephyr/zephyr.hex`.

## Flashing and execution

### Bare-metal

Using Nordic `nrfjprog` (if installed):

```bash
nrfjprog --family NRF52 --program bare-metal/build/low_power_bare_metal.hex --verify
nrfjprog --family NRF52 --reset
```

Alternatively, use J-Link Commander with the generated HEX file and the nRF52840 target. Exact J-Link commands depend on the installed J-Link version and probe selection.

### Zephyr

```bash
west flash -d build/zephyr --runner jlink
```

If the runner is not available in the installed Zephyr environment, use the board's default runner or install/configure the SEGGER J-Link software. Do not assume the flash command succeeded until the tool reports success.

### Expected behavior

- A short marker pulse occurs once per period on P0.03.
- If enabled, LED1 turns on for 50 ms every 5 seconds.
- The bare-metal application uses RTC2 compare interrupts and `WFE`.
- The Zephyr application uses `k_timer`, a semaphore and the Zephyr idle thread. The kernel timer/SoC clock implementation is responsible for waking the application.

No UART logging is enabled in the benchmark firmware because UART activity, the interface MCU and debug connections can materially alter the measured current.

## Measurement methodology

1. Use the same physical DK, supply voltage, board configuration, measurement instrument, sampling rate and LED setting for both variants.
2. Program the firmware, then isolate the SoC supply according to the DK revision guide.
3. Remove debugger/serial activity from the measurement path. Ensure no unused peripheral or GPIO load remains active.
4. Capture at least 60 seconds after a stable start-up interval; use a sufficiently high sample rate to resolve the wake-up workload and short pulse.
5. Record timestamp, current, voltage, implementation, phase and data origin for every sample.
6. Repeat at least five runs per firmware. Keep the measurement setup unchanged between runs.
7. Export/convert the data to `measurements/template.csv` format and run the analysis script.

```bash
python analysis/power_analysis.py \
  --input measurements/run_01.csv \
  --capacity-mah 220 \
  --period-s 5.0
```

Use the actual battery's rated capacity and voltage. Battery life is an idealized estimate, not a guaranteed runtime.

## Results and limitations

- No physical measurement result is claimed by this repository.
- `analysis/examples/simulated_example.csv` is synthetic and must never be cited as a hardware result.
- The Python unit tests validate calculations on synthetic inputs only; they do not validate the firmware on an nRF52840 board.
- Firmware build and flash status must be established on the user's machine with the specified external SDKs/toolchains.
- The board's LEDs, interface MCU, regulators, debugger, USB supply, pull-ups, external sensors and measurement instrument can dominate or distort current measurements.
- Bare-metal uses a dedicated RTC2 instance. Zephyr owns its system timer and scheduler; the two implementations do not use the same timer peripheral. The workload and period are functionally matched, but timer-driver overhead is part of the architecture being compared.
- The default comparison is **System ON idle**, not System OFF. The nRF52840 cannot use its internal RTC to wake from System OFF; System OFF wake causes a reset and requires a different scenario design.

## Bare-metal vs Zephyr comparison

See [`analysis/comparison.md`](analysis/comparison.md) for the qualitative comparison and [`docs/technical_report.md`](docs/technical_report.md) for the report template. Do not add measured conclusions until real data has been captured.

## Future improvements

- Add PPK2 export adapters and confidence intervals across repeated runs.
- Capture current profiles at high sampling rates and separate CPU, LED and board-level loads.
- Add a second experiment for System OFF with GPIO/reset wake and retained-state analysis.
- Add GPIO interrupt wake-up and debounce tests.
- Compare different LFCLK sources and clock configurations.
- Add automated build CI for a pinned Zephyr manifest and an available ARM GCC toolchain.
- Add energy-per-useful-operation metrics and compiler/build metadata to each measurement run.

## References

- [Nordic nRF52840 DK — current measurement guide](https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/hw_measure_current.html)
- [Nordic nRF52840 Product Specification — current consumption and power modes](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/chapters/current_consumption/doc/frontpage.html)
- [Zephyr v3.7.0 documentation](https://docs.zephyrproject.org/3.7.0/)
- [Zephyr nRF52840 DK board documentation](https://docs.zephyrproject.org/3.7.0/boards/arm/nrf52840dk_nrf52840/doc/index.html)
- [Zephyr System Power Management](https://docs.zephyrproject.org/3.7.0/services/pm/system.html)
- [Zephyr kernel timers](https://docs.zephyrproject.org/3.7.0/kernel/services/timing/timers.html)
