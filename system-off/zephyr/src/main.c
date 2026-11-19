/* nRF52 DK (PCA10040) Zephyr v3.7.0 System OFF experiment.
 * Wake source: button1 (sw0, P0.13, active-low); waking resets the SoC.
 * Unlike System ON Idle, there is no RTC wake or scheduled kernel work.
 */
#include <errno.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/poweroff.h>
#include <zephyr/sys/util.h>
#include <soc.h>

#if !DT_NODE_EXISTS(DT_ALIAS(sw0))
#error "The nRF52 DK (PCA10040) must expose the sw0 DeviceTree alias"
#endif

static const struct gpio_dt_spec button = GPIO_DT_SPEC_GET(DT_ALIAS(sw0), gpios);

int main(void)
{
    int ret;

    if (!device_is_ready(button.port)) {
        return -ENODEV;
    }
    ret = gpio_pin_configure_dt(&button, GPIO_INPUT);
    if (ret < 0) {
        return ret;
    }

    /* Button1 is active-low: wait for release to avoid a reset loop. */
    do {
        ret = gpio_pin_get_dt(&button);
        if (ret < 0) {
            return ret;
        }
        if (ret != 0) {
            k_msleep(10);
        }
    } while (ret != 0);

    /* The DK sw0 alias is on P0.13. Set hardware SENSE to Low so it
     * remains a wake source after the Zephyr kernel powers down.
     * gpio_pin_configure_dt() above configures input and pull-up from DTS.
     */
    BUILD_ASSERT(DT_GPIO_PIN(DT_ALIAS(sw0), gpios) == 13,
                 "Expected button1 on P0.13");
    NRF_P0->LATCH = BIT(button.pin);
    NRF_P0->PIN_CNF[button.pin] =
        (NRF_P0->PIN_CNF[button.pin] & ~GPIO_PIN_CNF_SENSE_Msk) |
        (GPIO_PIN_CNF_SENSE_Low << GPIO_PIN_CNF_SENSE_Pos);

    /* Match the optimized bare-metal experiment's explicit S0 setting.
     * Other retention bits are not modified by this application.
     */
    NRF_POWER->RAM[0].POWERCLR = POWER_RAM_POWER_S0RETENTION_Msk;
    __DSB();
    sys_poweroff(); /* Does not return on successful System OFF entry. */

    return 0;
}
