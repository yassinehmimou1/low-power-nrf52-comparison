# Bare-metal implementation

This application targets the **nRF52 DK PCA10040** and uses direct CMSIS-accessible peripheral registers. It deliberately does not use an RTOS or Nordic SoftDevice.

## Behavior

- Starts the external 32.768 kHz LF crystal.
- Configures RTC2 with prescaler 0 (32,768 ticks/s).
- RTC2 COMPARE0 fires every `SCENARIO_PERIOD_MS` and clears the counter through the RTC shortcut.
- The COMPARE0 ISR raises the optional active-low LED and schedules COMPARE1 for the end of the pulse.
- The main loop runs the shared deterministic workload while P0.03 is high.
- COMPARE1 turns the LED off and disables its one-shot interrupt.
- The main loop waits with the Cortex-M `WFE` instruction and the standard event-register clearing sequence.

## Dependencies

Install nRF5 SDK 17.1.0 separately. The SDK is not included because it is a third-party distribution. The Makefile uses the CMSIS/device headers and startup/system files from that SDK. No nrfx driver is linked: RTC and GPIO are configured directly through the nRF52832 register definitions.

## Build

```bash
make SDK_ROOT=/path/to/nRF5_SDK_17.1.0
make clean
make SDK_ROOT=/path/to/Nordic/nRF5_SDK_17.1.0 SCENARIO_LED_ENABLE=0 SCENARIO_WORKLOAD_ITERATIONS=4096
```

The build requires `arm-none-eabi-gcc`, `arm-none-eabi-objcopy` and `arm-none-eabi-size` in `PATH`.

## Flash

```bash
nrfjprog --family NRF52 --program build/low_power_bare_metal.hex --verify
nrfjprog --family NRF52 --reset
```

## Important limitations

- This is a register-level example for the nRF52832 only, not a portable nRF52 driver layer.
- RTC2 is reserved by this application. Do not enable another component that uses RTC2.
- The board's external 32.768 kHz crystal is selected. A custom board without that crystal needs a different LFCLK source and must be revalidated.
- No UART output is generated to avoid measurement contamination.
- `SCENARIO_LED_ENABLE=1` includes LED current in the measurement. Set it to `0` for an MCU-focused comparison and use P0.03 as the timing marker.
- The firmware has not been claimed as compiled or run on hardware by the repository author. Verify the local SDK/toolchain and run the test plan.
