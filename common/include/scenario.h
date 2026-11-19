#ifndef LOW_POWER_SCENARIO_H
#define LOW_POWER_SCENARIO_H

#include <stdint.h>

#ifndef SCENARIO_PERIOD_MS
#define SCENARIO_PERIOD_MS 5000U
#endif

#ifndef SCENARIO_PULSE_MS
#define SCENARIO_PULSE_MS 50U
#endif

#ifndef SCENARIO_WORKLOAD_ITERATIONS
#define SCENARIO_WORKLOAD_ITERATIONS 4096U
#endif

#if (SCENARIO_PERIOD_MS == 0U) || (SCENARIO_PULSE_MS == 0U)
#error "Scenario period and pulse duration must be non-zero"
#endif

#if SCENARIO_PULSE_MS >= SCENARIO_PERIOD_MS
#error "Pulse duration must be shorter than the periodic interval"
#endif

/* Deterministic CPU workload shared by both firmware implementations. */
uint32_t scenario_run_workload(void);

#endif /* LOW_POWER_SCENARIO_H */
