# Measurements and provenance

The project author reports three historical System OFF current values measured on a PCA10040: 4.7 µA, 3.6 µA, and 4.3 µA. The raw traces from those runs have **not** been uploaded. The values in `../analysis/reference_values.csv` are summary values supplied by the author, not synthetic traces.

`template.csv` defines the expected format for new raw sample series. Keep original instrument exports and an associated metadata manifest (see `metadata_template.json`) when available. Only label newly captured data as `MEASURED` when it actually comes from physical instrumentation.

The optional `../analysis/examples/simulated_example.csv` is clearly marked `SIMULATED` and must not be used as evidence for the historical figures.
