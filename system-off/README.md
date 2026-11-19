# System OFF experiment — nRF52 DK PCA10040 (nRF52832)

**Hardware:** Nordic nRF52 DK PCA10040, nRF52832 XXAA (512 KiB Flash, 64 KiB RAM).  
**Status:** source adapted to PCA10040; compilation/flashing of these reconstructed sources and reproduction of historical currents are **not verified** here.

## Configurations

| Variant | Firmware | RAM retention configuration | Wake source |
|---|---|---|---|
| Bare-metal standard | `bare-metal/src/main.c`, `RETAIN_RAM_SECTION0=1` | RAM block 0 section 0 retention enabled | BUTTON1 P0.13, GPIO SENSE Low |
| Bare-metal optimized | same, `RETAIN_RAM_SECTION0=0` | RAM block 0 section 0 retention disabled | BUTTON1 P0.13, GPIO SENSE Low |
| Zephyr RTOS | `zephyr/src/main.c` | RAM block 0 section 0 retention disabled | BUTTON1 P0.13, GPIO SENSE Low |

**Important:** These three source configurations are a reproducible *reconstruction*, not proof of the exact binaries/configurations used for the author's historical measurements. Enabling/disabling one retention section is not guaranteed to produce the reported current values. Other RAM retention sections and hardware defaults can influence current. Document actual retention registers and board setup before making causal claims.

System OFF disables the CPU/kernel. BUTTON1 causes a wake-by-reset; no periodic RTC wake is possible in System OFF. Compare *steady-state* current only, excluding boot, debugger and button-press transients. System OFF values do **not** measure RTOS scheduler overhead.

## Build

Install nRF5 SDK 17.1.0 and ARM GNU toolchain separately. From `system-off/bare-metal`:

```bash
make SDK_ROOT=/absolute/path/to/nRF5_SDK_17.1.0 RETAIN_RAM_SECTION0=1
make SDK_ROOT=/absolute/path/to/nRF5_SDK_17.1.0 RETAIN_RAM_SECTION0=0
```

Expected output files: `build/retention_1/system_off_bare_metal.hex` and `build/retention_0/system_off_bare_metal.hex`.

For Zephyr v3.7.0, from a configured workspace:

```bash
west build -b nrf52dk/nrf52832 /absolute/path/to/repo/system-off/zephyr -d build/system-off-zephyr
```

After flashing and disconnecting debug, measure the **SoC supply current** through the PCA10040 measurement path, following the user guide for the exact board revision. Never put an ammeter across the power supply.

## Historical measurements reported by the author

| Variant | Reported System OFF current |
|---|---:|
| Bare-metal standard | 4.7 µA |
| Bare-metal optimized | 3.6 µA |
| Zephyr RTOS | 4.3 µA |

The author reports having measured these values on a PCA10040. **Raw traces, instrument model, voltage, board revision and original firmware binaries are not yet provided in this repository.** Therefore they have not been independently reproduced from the reconstructed sources. See `../docs/system_off_methodology.md`.
