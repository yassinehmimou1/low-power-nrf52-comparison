#include "scenario.h"

/* Volatile sink prevents the compiler from deleting the benchmark workload. */
static volatile uint32_t workload_sink;

uint32_t scenario_run_workload(void)
{
    uint32_t value = 0x13579BDFU;

    for (uint32_t i = 0U; i < SCENARIO_WORKLOAD_ITERATIONS; ++i) {
        value = (value * 1664525U) + 1013904223U;
        value ^= (value >> 13U);
    }

    workload_sink = value;
    return workload_sink;
}
