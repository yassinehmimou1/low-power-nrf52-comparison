/* nRF52840 DK (PCA10056) System OFF experiment.
 * Build with RETAIN_RAM_SECTION0=1 (baseline) or 0 (optimized).
 * Button 1 on P0.11 wakes the device; wake-up causes a RESET.
 * IMPORTANT: this code does not generate or imply any specific current.
 */
#include <stdint.h>
#include "nrf.h"

#ifndef RETAIN_RAM_SECTION0
#define RETAIN_RAM_SECTION0 1
#endif

#if (RETAIN_RAM_SECTION0 != 0) && (RETAIN_RAM_SECTION0 != 1)
#error "RETAIN_RAM_SECTION0 must be 0 or 1"
#endif

#define BUTTON1_PIN 11U
#define BUTTON1_MASK (1UL << BUTTON1_PIN)

static void configure_button_wakeup(void)
{
    /* On the PCA10056, BUTTON1 shorts P0.11 to GND when pressed.
     * Internal pull-up keeps the line high when released.
     * SENSE=Low is a valid wake source from System OFF.
     */
    NRF_P0->PIN_CNF[BUTTON1_PIN] =
        (GPIO_PIN_CNF_DIR_Input << GPIO_PIN_CNF_DIR_Pos) |
        (GPIO_PIN_CNF_INPUT_Connect << GPIO_PIN_CNF_INPUT_Pos) |
        (GPIO_PIN_CNF_PULL_Pullup << GPIO_PIN_CNF_PULL_Pos) |
        (GPIO_PIN_CNF_SENSE_Disabled << GPIO_PIN_CNF_SENSE_Pos);

    /* Prevent immediate wake/reset cycling if the user is holding button. */
    while ((NRF_P0->IN & BUTTON1_MASK) == 0U) {
        /* Startup phase only; never included in the System OFF average. */
    }
    /* Clear any stale latch before arming the level-sensitive wake. */
    NRF_P0->LATCH = BUTTON1_MASK;
    NRF_P0->PIN_CNF[BUTTON1_PIN] =
        (NRF_P0->PIN_CNF[BUTTON1_PIN] & ~GPIO_PIN_CNF_SENSE_Msk) |
        (GPIO_PIN_CNF_SENSE_Low << GPIO_PIN_CNF_SENSE_Pos);
}

static void configure_retention(void)
{
    /* One explicitly controlled RAM section (S0 of RAM0).
     * Other RAM retention fields remain at startup defaults.
     * We do NOT switch RAM POWER off while executing code.
     */
#if RETAIN_RAM_SECTION0
    NRF_POWER->RAM[0].POWERSET = POWER_RAM_POWER_S0RETENTION_Msk;
#else
    NRF_POWER->RAM[0].POWERCLR = POWER_RAM_POWER_S0RETENTION_Msk;
#endif
}

int main(void)
{
    configure_button_wakeup();
    configure_retention();

    /* Stop debug-enabled measurements separately; the debugger may
     * prevent reaching the expected microamp current on the DK. */
    __DSB();
    NRF_POWER->SYSTEMOFF = POWER_SYSTEMOFF_SYSTEMOFF_Enter;
    __DSB();

    /* Hardware stays in System OFF until a wake source resets the chip. */
    for (;;) {
        __WFE();
    }
}
