# Bare-metal vs Zephyr — qualitative comparison

This is a design-level comparison, not a claim about measured current or latency. Numerical conclusions must be populated from real captures.

| Dimension | Bare-metal implementation | Zephyr implementation |
|---|---|---|
| Architecture | Single main loop plus RTC2 ISR | Kernel main thread, timer callback and semaphore |
| Timer source | Dedicated RTC2 compare channel | Zephyr system clock / board-selected RTC backend |
| Sleep entry | Explicit Cortex-M `WFE` in the application loop | Kernel idle thread waits when no thread is runnable |
| Wake-up | RTC2 compare interrupt | Kernel timer interrupt followed by semaphore scheduling |
| GPIO | Direct `NRF_P0` register access | DeviceTree-backed GPIO driver API |
| Interrupt handling | ISR written and owned by the application | Timer interrupt managed by Zephyr; callback must remain short |
| Resource overhead | Minimal runtime and no scheduler | Kernel, scheduler, timer and synchronization state |
| Timing control | Direct peripheral configuration; application owns race handling | Higher-level timing API; kernel tick/timer semantics and scheduling latency apply |
| Portability | Tied to nRF52840 register map and startup support | More portable across supported Zephyr boards, subject to drivers and DTS |
| Maintainability | Small codebase, but peripheral details are manual | More conventions and configuration, stronger abstraction and extension path |
| Extensibility | Additional tasks require custom event/state machinery | Threads, queues, semaphores, workqueues, drivers and PM framework available |
| Power optimization | Explicit control over selected peripherals and wake sources | Idle behavior plus device/system PM configuration; driver state matters |
| Debugging | Direct register inspection and simple control flow | Richer RTOS-aware debugging, but more layers to inspect |

## Important interpretation points

1. **Zephyr does not inherently consume more energy in every application.** Its baseline overhead depends on enabled kernel services, drivers, clocks, console and board configuration.
2. **Bare-metal does not automatically mean lower current.** A peripheral left enabled, a busy loop, an active HF clock or a poor GPIO configuration can dominate current.
3. The nRF52840's System ON idle is available when the CPU waits for an event while the RTC remains active. The Zephyr idle thread can provide this behavior without application code calling `WFE` directly.
4. The Zephyr timer and the bare-metal RTC2 timer are different timer paths. This comparison intentionally includes the software abstraction and scheduling overhead of Zephyr; it does not claim a cycle-identical timer implementation.
5. The LED current can dominate the low-current portion. Disable it for the primary MCU-focused measurement and use P0.03 as the external timing marker.
6. A fair comparison requires matching period, workload, pulse duration, supply voltage, measurement window, firmware optimization level as closely as practical, and physical setup.

## Results table — fill only from real measurements

| Metric | Bare-metal | Zephyr | Source / run IDs |
|---|---:|---:|---|
| Mean current (µA) | TBD | TBD | TBD |
| Active current peak (mA) | TBD | TBD | TBD |
| Idle current (µA) | TBD | TBD | TBD |
| Active workload duration (µs) | TBD | TBD | TBD |
| Wake-to-marker latency (µs) | TBD | TBD | TBD |
| Energy per cycle (µJ) | TBD | TBD | TBD |
| Estimated autonomy (days) | TBD | TBD | TBD |

No results are entered because no physical measurement dataset has been supplied.
