# Experimental methodology

## Hypothesis

The register-level firmware is expected to have less software framework overhead, while Zephyr is expected to offer better abstraction, maintainability and extensibility. Neither expectation is a measurement. The actual current profile depends on clocks, enabled peripherals, firmware configuration, board leakage and measurement setup.

## Independent variables

- Firmware architecture: bare-metal vs Zephyr.
- LED load: enabled vs disabled (primary comparison should use disabled).
- Optional future variables: LFCLK source, CPU frequency, workload size, period and Zephyr configuration.

## Controlled variables

- Same nRF52840 DK and board revision.
- Same supply voltage and source.
- Same measurement instrument, range, sampling rate and wiring.
- Same period, pulse duration and workload iteration count.
- Same LED setting and external load configuration.
- Same capture duration and warm-up procedure.

## Procedure

1. Record board revision and instrument calibration/status.
2. Build both firmwares with identical scenario constants and LED disabled.
3. Flash the first firmware, disconnect debug USB and prepare P22/SB40 according to the DK user guide.
4. Apply a stable external supply and allow the setup to settle.
5. Capture at least 60 seconds with a sampling rate capable of resolving active events. Use the P0.03 marker to align the current trace with wake events.
6. Save the raw instrument export. Convert to the CSV schema without modifying the raw file.
7. Repeat five times, then repeat for the other firmware using the identical setup.
8. Analyze each run independently. Report mean, median and spread across runs in the final report; the current script reports one time-series group at a time.
9. Repeat with LED enabled only as a separate functional/load experiment.

## Instrumentation considerations

A low-bandwidth multimeter may show average current but miss short peaks. A high-bandwidth current profiler or oscilloscope/shunt is needed to capture transient current and wake-up timing. The measurement shunt can add voltage drop; check that the DUT supply remains within specification. Use a clean supply and avoid USB/debugger paths that feed extra board circuitry.

## Data integrity

Every CSV row must identify `data_origin`. `MEASURED` is reserved for data captured from physical hardware. Synthetic examples must use `SIMULATED`. Keep the original PPK2/scope files, metadata and conversion script. Never manually adjust samples to make one implementation appear better.
