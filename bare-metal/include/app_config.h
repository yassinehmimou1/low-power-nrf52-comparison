#ifndef BARE_METAL_APP_CONFIG_H
#define BARE_METAL_APP_CONFIG_H

#ifndef SCENARIO_LED_ENABLE
#define SCENARIO_LED_ENABLE 1
#endif

#define LFCLK_HZ                 32768UL
#define RTC_PRESCALER_VALUE      0UL
#define RTC_TICKS_FROM_MS(ms)    (((LFCLK_HZ * (uint32_t)(ms)) + 500UL) / 1000UL)
#define RTC_PERIOD_TICKS         RTC_TICKS_FROM_MS(SCENARIO_PERIOD_MS)
#define RTC_PULSE_TICKS          RTC_TICKS_FROM_MS(SCENARIO_PULSE_MS)

#define LED1_PIN                 17U  /* P0.17, active-low on nRF52 DK PCA10040 */
#define MARKER_PIN               3U   /* P0.03, Arduino A0 */

#if (RTC_PERIOD_TICKS >= 0x1000000UL)
#error "RTC period exceeds the 24-bit RTC counter range"
#endif

#if (RTC_PULSE_TICKS == 0UL) || (RTC_PULSE_TICKS >= RTC_PERIOD_TICKS)
#error "RTC pulse duration must be non-zero and shorter than the period"
#endif

#endif /* BARE_METAL_APP_CONFIG_H */
