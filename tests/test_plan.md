# Firmware test and validation plan

## Test configuration record

For every test campaign, record:

- DK order code and PCB revision (PCA10040 and revision printed on board).
- nRF52832 silicon revision if available.
- Firmware commit hash and build configuration.
- Bare-metal SDK/toolchain or Zephyr revision/toolchain.
- Supply source, voltage, current limit and measurement instrument.
- Whether LED1 is enabled; whether UART/debugger/interface MCU are disconnected.
- Ambient temperature and measurement sample rate.

## Functional tests

| ID | Test | Procedure | Expected result | Evidence |
|---|---|---|---|---|
| F-01 | Startup | Flash and reset each firmware | Firmware starts without hard fault; marker/LED are inactive until first event | Debugger/reset record |
| F-02 | Periodic wake | Observe P0.03 for at least 20 periods | One marker pulse per configured period, nominally 5 s | Scope/logic capture |
| F-03 | Pulse duration | Observe LED1 or a dedicated pulse output | Pulse nominally 50 ms; account for timer quantization and scheduling | Scope capture |
| F-04 | Workload execution | Set breakpoint/watch `last_workload_result` (bare-metal) or inspect generated assembly/trace | Deterministic workload executes once per periodic event | Debug record |
| F-05 | LED disabled | Build both variants with LED disabled | P0.03 still pulses; LED1 remains off | Visual + scope record |

## Interrupt and timing tests

| ID | Test | Procedure | Expected result | Evidence |
|---|---|---|---|---|
| I-01 | RTC2 compare 0 | Bare-metal only; inspect RTC2 event/interrupt | One periodic interrupt per interval | Debugger register snapshot |
| I-02 | RTC2 compare 1 | Bare-metal only; inspect one-shot compare | LED pulse ends once and COMPARE1 interrupt is disabled | Debugger register snapshot |
| I-03 | Kernel timer | Zephyr; observe repeated semaphore release | One timer expiry per configured period; no accumulated semaphore backlog | Trace/scope |
| I-04 | Wake latency | Measure timer event reference to P0.03 rising edge | Latency is measurable and repeatable; report distribution, not a single cherry-picked value | Scope/PPK2 trace |

## Low-power tests

| ID | Test | Procedure | Expected result | Evidence |
|---|---|---|---|---|
| P-01 | Idle current | Capture current between events with LED disabled | Stable low-current plateau; exact value must be measured | Raw current trace |
| P-02 | Active current | Capture wake-up/workload current at sufficient sample rate | Transient peak and pulse width are captured | Raw current trace |
| P-03 | Energy per cycle | Integrate a complete period | Energy estimate is reproducible across runs | Analysis report |
| P-04 | Board leakage | Compare DK setup before/after debugger/USB isolation as specified by Nordic | Non-SoC board loads are identified | Setup notes |

## Regression tests

- Rebuild both implementations after any source/configuration change.
- Verify the same period, pulse and workload iteration settings in both variants.
- Run at least 20 wake cycles after each build.
- Check no RTC2 ownership conflict in bare-metal.
- Check generated Zephyr `build/zephyr/zephyr.dts` and `build/zephyr/.config` to confirm the intended overlay and Kconfig settings.
- Run Python tests after modifying the analysis script.

## Failure analysis checklist

- No marker pulse: verify power, flash result, GPIO pin mapping and firmware reset.
- Bare-metal timer does not run: verify LFCLK started event, RTC2 prescaler, NVIC enable and interrupt vector symbol.
- Zephyr timer does not run: inspect `k_timer_start`, system clock configuration, semaphore and application thread state.
- Unexpectedly high idle current: disable LED, UART, logging, debugger, radio, unused peripherals and external loads; inspect GPIO states and board measurement setup.
- Inconsistent energy results: inspect sample rate, timestamp ordering, instrument autoranging, shunt burden voltage and measurement window alignment.

## Status

All hardware tests are **NOT RUN** until the operator records date, firmware commit, setup and evidence. The host-side Python tests are separate and must not be presented as firmware tests.
