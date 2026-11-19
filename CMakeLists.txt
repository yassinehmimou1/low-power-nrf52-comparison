cmake_minimum_required(VERSION 3.20)
project(low_power_nrf52_comparison NONE)

find_package(Python3 COMPONENTS Interpreter)
if(Python3_Interpreter_FOUND)
  add_custom_target(test_analysis
    COMMAND ${Python3_EXECUTABLE} -m unittest discover -s tests -v
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Run host-side power-analysis unit tests")
  add_custom_target(power_analysis_help
    COMMAND ${Python3_EXECUTABLE} analysis/power_analysis.py --help
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Show power-analysis CLI help")
else()
  message(STATUS "Python 3 not found: host-side analysis targets are unavailable")
endif()

message(STATUS "Firmware builds are intentionally independent: use bare-metal/Makefile or west build in zephyr/.")
