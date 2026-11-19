#include <errno.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/util.h>

#include "scenario.h"

#if CONFIG_SCENARIO_PULSE_MS >= CONFIG_SCENARIO_PERIOD_MS
#error "SCENARIO_PULSE_MS must be shorter than SCENARIO_PERIOD_MS"
#endif

#define MARKER_NODE DT_PATH(zephyr_user)
static const struct gpio_dt_spec marker_gpio =
    GPIO_DT_SPEC_GET(MARKER_NODE, marker_gpios);

#if CONFIG_SCENARIO_LED
static const struct gpio_dt_spec led_gpio =
    GPIO_DT_SPEC_GET(DT_ALIAS(led0), gpios);
#endif

K_SEM_DEFINE(wake_sem, 0, 1);

static void periodic_timer_expiry(struct k_timer *timer)
{
    ARG_UNUSED(timer);
    /* k_sem_give() is ISR-safe; the application work runs in main context. */
    k_sem_give(&wake_sem);
}

K_TIMER_DEFINE(periodic_timer, periodic_timer_expiry, NULL);

int main(void)
{
    int ret;

    if (!device_is_ready(marker_gpio.port)) {
        return -ENODEV;
    }

    ret = gpio_pin_configure_dt(&marker_gpio, GPIO_OUTPUT_INACTIVE);
    if (ret < 0) {
        return ret;
    }

#if CONFIG_SCENARIO_LED
    if (!device_is_ready(led_gpio.port)) {
        return -ENODEV;
    }

    ret = gpio_pin_configure_dt(&led_gpio, GPIO_OUTPUT_INACTIVE);
    if (ret < 0) {
        return ret;
    }
#endif

    k_timer_start(&periodic_timer,
                  K_MSEC(CONFIG_SCENARIO_PERIOD_MS),
                  K_MSEC(CONFIG_SCENARIO_PERIOD_MS));

    for (;;) {
        /* With no runnable application thread, Zephyr's idle thread can
         * enter the SoC's System ON idle state and wait for the next event. */
        k_sem_take(&wake_sem, K_FOREVER);

#if CONFIG_SCENARIO_LED
        (void)gpio_pin_set_dt(&led_gpio, 1); /* Logical active = LED on. */
#endif

        (void)gpio_pin_set_dt(&marker_gpio, 1);
        (void)scenario_run_workload();
        (void)gpio_pin_set_dt(&marker_gpio, 0);

        /* The main thread sleeps during the remainder of the visible pulse.
         * This is intentionally not a busy-wait. */
        k_sleep(K_MSEC(CONFIG_SCENARIO_PULSE_MS));

#if CONFIG_SCENARIO_LED
        (void)gpio_pin_set_dt(&led_gpio, 0);
#endif
    }

    return 0;
}
