# Measurement data

`template.csv` is an intentionally empty schema. It contains no measured values.

## Required columns

- `timestamp_s`: seconds since the beginning of the capture; strictly increasing within each implementation/run.
- `implementation`: use `Bare-Metal` or `Zephyr` consistently.
- `current_mA`: measured current in milliamps, non-negative.
- `voltage_V`: measured supply voltage in volts, positive.
- `phase`: optional annotation such as `idle`, `active`, `wakeup`, `workload`, `pulse`. The script reports phase-specific average current where adjacent samples have matching labels; boundary intervals are labelled `TRANSITION`.
- `data_origin`: exactly `MEASURED` or `SIMULATED`. Do not label generated/example data as measured.
- `run_id`: optional identifier for the capture and repeat number.

The analysis script groups data by `implementation`, `data_origin` and `run_id`, so multiple runs can share one CSV as long as timestamps are strictly increasing within each group. Each run must have at least two samples. Keep the run IDs stable and unique for each capture.

## Capture guidance

- Capture current and voltage synchronously if possible.
- Use a sample rate high enough to resolve the wake-up current pulse. For a workload lasting tens or hundreds of microseconds, kHz sampling may still be insufficient; use the PPK2's supported sampling modes or a scope/shunt for high-bandwidth captures.
- Avoid UART logging and active debugger connections.
- Record board revision, firmware commit, compiler version, Zephyr revision, supply voltage, instrument model, sampling rate, LED setting and environmental conditions in a run log.
- Keep raw instrument exports unchanged. Store converted/normalized CSV separately and retain the original files for traceability.
