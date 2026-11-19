SDK_ROOT ?=
GNU_PREFIX ?= arm-none-eabi-
SCENARIO_LED_ENABLE ?= 1
SCENARIO_PERIOD_MS ?= 5000
SCENARIO_PULSE_MS ?= 50
SCENARIO_WORKLOAD_ITERATIONS ?= 4096

CC      := $(GNU_PREFIX)gcc
OBJCOPY := $(GNU_PREFIX)objcopy
SIZE    := $(GNU_PREFIX)size

ifeq ($(strip $(SDK_ROOT)),)
$(error Set SDK_ROOT to the extracted nRF5_SDK_17.1.0 directory)
endif

MDK_DIR := $(SDK_ROOT)/modules/nrfx/mdk
CMSIS_DIR := $(SDK_ROOT)/components/toolchain/cmsis/include
STARTUP := $(MDK_DIR)/gcc_startup_nrf52840.S
SYSTEM := $(MDK_DIR)/system_nrf52840.c

BUILD_DIR := build
TARGET := $(BUILD_DIR)/low_power_bare_metal
LINKER_SCRIPT := linker/nrf52840_xxaa.ld

CFLAGS := -std=c11 -Os -g3 -Wall -Wextra \
          -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard \
          -ffunction-sections -fdata-sections -fno-common \
          -DNRF52840_XXAA -D__HEAP_SIZE=0 -D__STACK_SIZE=2048 \
          -DSCENARIO_LED_ENABLE=$(SCENARIO_LED_ENABLE) \
          -DSCENARIO_PERIOD_MS=$(SCENARIO_PERIOD_MS) \
          -DSCENARIO_PULSE_MS=$(SCENARIO_PULSE_MS) \
          -DSCENARIO_WORKLOAD_ITERATIONS=$(SCENARIO_WORKLOAD_ITERATIONS) \
          -Iinclude -I../common/include -I$(MDK_DIR) -I$(CMSIS_DIR)

LDFLAGS := -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard \
           --specs=nano.specs --specs=nosys.specs \
           -T$(LINKER_SCRIPT) -Wl,--gc-sections -Wl,--cref \
           -Wl,-Map=$(TARGET).map

C_SOURCES := src/main.c ../common/src/scenario.c $(SYSTEM)
OBJECTS := $(patsubst %.c,$(BUILD_DIR)/%.o,$(notdir $(C_SOURCES))) $(BUILD_DIR)/startup.o

.PHONY: all clean check-sdk
all: check-sdk $(TARGET).hex

check-sdk:
	@test -f "$(STARTUP)" || (echo "Missing startup file: $(STARTUP)"; exit 1)
	@test -f "$(SYSTEM)" || (echo "Missing system file: $(SYSTEM)"; exit 1)
	@test -f "$(MDK_DIR)/nrf52840.h" || (echo "Missing nrf52840.h in $(MDK_DIR)"; exit 1)
	@command -v $(CC) >/dev/null || (echo "Missing compiler $(CC)"; exit 1)

$(BUILD_DIR):
	mkdir -p $@

$(BUILD_DIR)/main.o: src/main.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/scenario.o: ../common/src/scenario.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/system_nrf52840.o: $(SYSTEM) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/startup.o: $(STARTUP) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -x assembler-with-cpp -c $< -o $@

$(TARGET).elf: $(BUILD_DIR)/main.o $(BUILD_DIR)/scenario.o $(BUILD_DIR)/system_nrf52840.o $(BUILD_DIR)/startup.o
	$(CC) $^ $(LDFLAGS) -Wl,--start-group -lc -lgcc -lnosys -Wl,--end-group -o $@
	$(SIZE) $@

$(TARGET).hex: $(TARGET).elf
	$(OBJCOPY) -O ihex $< $@

clean:
	rm -rf $(BUILD_DIR)
