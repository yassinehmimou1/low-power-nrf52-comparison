# Zephyr implementation

Target: `nrf52840dk/nrf52840`, Zephyr v3.7.0.

## Application design

- `k_timer` generates a periodic timeout using the Zephyr kernel time base.
- The timer expiry callback runs in interrupt context and releases a binary semaphore.
- `main()` waits on the semaphore, wakes to execute the same shared deterministic workload as the bare-metal implementation, and toggles the P0.03 measurement marker.
- If enabled, LED1 is driven through the Zephyr GPIO API for the configured pulse duration.
- `k_sleep()` blocks the main thread during the remainder of the pulse. When no thread is runnable, Zephyr's idle thread waits for the next event; on nRF52840 this is System ON idle, not System OFF.

## DeviceTree and Kconfig

- `boards/nrf52840dk_nrf52840.overlay` defines `zephyr,user/marker-gpios` for P0.03 and disables unused board peripherals (ADC, UART, I2C, SPI, PWM, QSPI, IEEE 802.15.4 and USB) for a cleaner baseline.
- LED1 uses the board-provided `led0` alias (P0.13, active-low).
- `Kconfig` exposes LED use, period, pulse and workload iteration settings.
- `prj.conf` enables GPIO, system PM and tickless kernel, and disables serial console/logging.

The Zephyr board DTS already describes the DK's LED alias. Do not duplicate or replace the complete board DTS in this application.

## Build

From a configured Zephyr v3.7.0 workspace:

```bash
west build -b nrf52840dk/nrf52840 /path/to/repo/zephyr -d /path/to/repo/build/zephyr
```

Set `CONFIG_SCENARIO_LED=n` in `prj.conf` for MCU-focused measurements, then rebuild. Use the same LED configuration for the bare-metal build.

## Flash

```bash
west flash -d /path/to/repo/build/zephyr --runner jlink
```

## Power-management notes

`CONFIG_PM=y` enables Zephyr system PM support. Independently, when no application thread is runnable, the kernel idle thread waits for events; on the nRF52840 this is the wakeable System ON idle behavior used by the periodic timer. The application does not force `PM_STATE_SOFT_OFF` or call `sys_poweroff()`. A periodic RTC-backed kernel timer is incompatible with a simple System OFF sleep experiment on the nRF52840 because the internal RTC cannot wake the SoC from System OFF; that wake-up restarts the system. Use a GPIO/reset source or an external RTC for a separate System OFF experiment.

## Verification status

The source and configuration are supplied for a pinned Zephyr version, but compilation, flashing and board execution must be performed on the target developer's machine. Do not mark this implementation as hardware-validated until the test plan has been executed and recorded.
