# System OFF bare-metal firmware; nRF5 SDK 17.1.0 + ARM GNU toolchain.
SDK_ROOT ?=
GNU_PREFIX ?= arm-none-eabi-
RETAIN_RAM_SECTION0 ?= 1

CC := $(GNU_PREFIX)gcc
OBJCOPY := $(GNU_PREFIX)objcopy
SIZE := $(GNU_PREFIX)size

ifeq ($(strip $(SDK_ROOT)),)
$(error Set SDK_ROOT to the extracted nRF5 SDK 17.1.0 directory)
endif

MDK_DIR := $(SDK_ROOT)/modules/nrfx/mdk
CMSIS_DIR := $(SDK_ROOT)/components/toolchain/cmsis/include
STARTUP := $(MDK_DIR)/gcc_startup_nrf52.S
SYSTEM := $(MDK_DIR)/system_nrf52.c
LINKER := ../../bare-metal/linker/nrf52_xxaa.ld
BUILD_DIR := build/retention_$(RETAIN_RAM_SECTION0)
TARGET := $(BUILD_DIR)/system_off_bare_metal

CFLAGS := -std=c11 -Os -g3 -Wall -Wextra -Werror \
          -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard \
          -ffunction-sections -fdata-sections -fno-common \
          -DNRF52832_XXAA -D__HEAP_SIZE=0 -D__STACK_SIZE=2048 \
          -DRETAIN_RAM_SECTION0=$(RETAIN_RAM_SECTION0) \
          -I$(MDK_DIR) -I$(CMSIS_DIR)
LDFLAGS := -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard \
           --specs=nano.specs --specs=nosys.specs \
           -T$(LINKER) -Wl,--gc-sections -Wl,-Map=$(TARGET).map

.PHONY: all clean check-sdk
all: check-sdk $(TARGET).hex

check-sdk:
	@test -f "$(STARTUP)" || (echo "Missing $(STARTUP)"; exit 1)
	@test -f "$(SYSTEM)" || (echo "Missing $(SYSTEM)"; exit 1)
	@test -f "$(MDK_DIR)/nrf52832.h" || (echo "Missing nrf52832.h"; exit 1)
	@command -v $(CC) >/dev/null || (echo "Missing $(CC)"; exit 1)

$(BUILD_DIR):
	mkdir -p $@

$(BUILD_DIR)/main.o: src/main.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/system_nrf52.o: $(SYSTEM) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/startup.o: $(STARTUP) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -x assembler-with-cpp -c $< -o $@

$(TARGET).elf: $(BUILD_DIR)/main.o $(BUILD_DIR)/system_nrf52.o $(BUILD_DIR)/startup.o
	$(CC) $^ $(LDFLAGS) -Wl,--start-group -lc -lgcc -lnosys -Wl,--end-group -o $@
	$(SIZE) $@

$(TARGET).hex: $(TARGET).elf
	$(OBJCOPY) -O ihex $< $@

clean:
	rm -rf build
