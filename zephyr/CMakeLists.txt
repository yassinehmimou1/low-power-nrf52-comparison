cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(low_power_zephyr_comparison)

target_sources(app PRIVATE
    src/main.c
    ../common/src/scenario.c
)
target_include_directories(app PRIVATE ../common/include)

target_compile_definitions(app PRIVATE
    SCENARIO_PERIOD_MS=${CONFIG_SCENARIO_PERIOD_MS}
    SCENARIO_PULSE_MS=${CONFIG_SCENARIO_PULSE_MS}
    SCENARIO_WORKLOAD_ITERATIONS=${CONFIG_SCENARIO_WORKLOAD_ITERATIONS}
)
