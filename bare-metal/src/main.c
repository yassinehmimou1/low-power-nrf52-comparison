#include <stdint.h>
#include "nrf.h"
#include "app_config.h"
#include "scenario.h"

static volatile uint32_t wake_event_pending;
static volatile uint32_t cycle_count;
static volatile uint32_t last_workload_result;

static void gpio_init(void)
{
    /* P0.03 is a high-true instrumentation marker. */
    NRF_P0->PIN_CNF[MARKER_PIN] = 1UL; /* DIR=output; other fields at reset defaults */
    NRF_P0->OUTCLR = (1UL << MARKER_PIN);

#if SCENARIO_LED_ENABLE
    /* LED1 is active-low: output high means LED off. */
    NRF_P0->PIN_CNF[LED1_PIN] = 1UL;
    NRF_P0->OUTSET = (1UL << LED1_PIN);
#endif
}

static void lfclk_init(void)
{
    NRF_CLOCK->EVENTS_LFCLKSTARTED = 0U;
    NRF_CLOCK->LFCLKSRC = CLOCK_LFCLKSRC_SRC_Xtal;
    NRF_CLOCK->TASKS_LFCLKSTART = 1U;

    while (NRF_CLOCK->EVENTS_LFCLKSTARTED == 0U) {
        /* Startup wait: LFCLK is required before RTC2 can run accurately. */
    }

    NRF_CLOCK->EVENTS_LFCLKSTARTED = 0U;
}

static void rtc2_init(void)
{
    NRF_RTC2->TASKS_STOP = 1U;
    NRF_RTC2->PRESCALER = RTC_PRESCALER_VALUE;
    NRF_RTC2->TASKS_CLEAR = 1U;

    NRF_RTC2->EVENTS_COMPARE[0] = 0U;
    NRF_RTC2->EVENTS_COMPARE[1] = 0U;
    NRF_RTC2->CC[0] = RTC_PERIOD_TICKS;
    NRF_RTC2->CC[1] = 0U;

    /* Reset the RTC counter on each periodic compare. */
    NRF_RTC2->SHORTS = RTC_SHORTS_COMPARE0_CLEAR_Msk;

    /* Enable only the periodic interrupt initially; COMPARE1 is one-shot. */
    NRF_RTC2->INTENCLR = 0xFFFFFFFFUL;
    NRF_RTC2->INTENSET = RTC_INTENSET_COMPARE0_Msk;

    NVIC_ClearPendingIRQ(RTC2_IRQn);
    NVIC_SetPriority(RTC2_IRQn, 6U);
    NVIC_EnableIRQ(RTC2_IRQn);

    NRF_RTC2->TASKS_START = 1U;
}

void RTC2_IRQHandler(void)
{
    if (NRF_RTC2->EVENTS_COMPARE[0] != 0U) {
        NRF_RTC2->EVENTS_COMPARE[0] = 0U;

#if SCENARIO_LED_ENABLE
        NRF_P0->OUTCLR = (1UL << LED1_PIN);
#endif

        /* COMPARE0's CLEAR shortcut has reset COUNTER to zero. */
        NRF_RTC2->EVENTS_COMPARE[1] = 0U;
        NRF_RTC2->CC[1] = RTC_PULSE_TICKS;
        NRF_RTC2->INTENSET = RTC_INTENSET_COMPARE1_Msk;

        ++cycle_count;
        wake_event_pending = 1U;
    }

    if (NRF_RTC2->EVENTS_COMPARE[1] != 0U) {
        NRF_RTC2->EVENTS_COMPARE[1] = 0U;
        NRF_RTC2->INTENCLR = RTC_INTENCLR_COMPARE1_Msk;

#if SCENARIO_LED_ENABLE
        NRF_P0->OUTSET = (1UL << LED1_PIN);
#endif
    }
}

int main(void)
{
    gpio_init();
    lfclk_init();
    rtc2_init();

    for (;;) {
        /* Check the flag before sleeping. If the interrupt arrives between
         * this check and WFE, the pending interrupt/event wakes the core;
         * the flag is then observed on the next loop iteration. */
        if (wake_event_pending != 0U) {
            wake_event_pending = 0U;
            NRF_P0->OUTSET = (1UL << MARKER_PIN);
            last_workload_result = scenario_run_workload();
            NRF_P0->OUTCLR = (1UL << MARKER_PIN);
            continue;
        }

        __WFE();
    }
}
