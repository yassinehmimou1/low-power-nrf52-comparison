# Manual GitHub migration guide — PCA10040

The previous public repository targeted nRF52840 DK (PCA10056). This update changes the **primary** firmware target to nRF52 DK (PCA10040, nRF52832).

## Delete obsolete paths on GitHub

These old files must not remain next to the new ones, because they describe or build the wrong board:

- `bare-metal/linker/nrf52840_xxaa.ld`
- `zephyr/boards/nrf52840dk_nrf52840.overlay`
- `assets/linkedin_reference_chart.png` (renamed to `linkedin_original_chart.png`)
- `assets/board_photo_pca10040_reference.png` (renamed to `board_photo_pca10040.png`)

## Add new paths

- `bare-metal/linker/nrf52_xxaa.ld`
- `zephyr/boards/nrf52dk_nrf52832.overlay`
- `assets/board_photo_pca10040.png`
- `assets/linkedin_original_chart.png`
- `assets/system_off_reported_results.png`
- `measurements/metadata_template.json`
- `MIGRATION_GUIDE.md`

## Replace existing paths

Replace existing README, docs, code, Makefiles, CSV, Python and test files with the versions in this archive, preserving folder structure. The GitHub web editor can replace an existing file using the pencil icon; **Add file → Upload files** is useful for new files. Commit in manageable groups and verify the file tree afterwards.

Do not upload the ZIP as one blob. The archive includes a top-level `low-power-nrf52-comparison/` folder; upload the **contents** of that folder to the repository root, not the containing folder itself.

## Verify the final result

- `README.md` must say **PCA10040 / nRF52832**.
- `system-off/bare-metal/Makefile` must define `NRF52832_XXAA`.
- `system-off/zephyr/` must build for `nrf52dk/nrf52832`.
- The old nRF52840 linker script and overlay must be removed.
- `analysis/reference_values.csv` must say `author-reported measurement on PCA10040`, with `raw traces not supplied in repository`.
- Run `python -m unittest discover -s tests -v` locally.
- Build and flash on PCA10040 before claiming firmware validation.
