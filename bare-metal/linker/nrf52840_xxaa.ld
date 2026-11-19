/* Minimal GNU ld script for nRF52840 (1 MiB Flash, 256 KiB RAM). */
ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x00000000, LENGTH = 1024K
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 256K
}

SECTIONS
{
    .isr_vector : ALIGN(4)
    {
        KEEP(*(.isr_vector))
        KEEP(*(.vectors))
    } > FLASH

    .text : ALIGN(4)
    {
        *(.text*)
        *(.rodata*)
        KEEP(*(.init))
        KEEP(*(.fini))
        . = ALIGN(4);
    } > FLASH

    .ARM.extab : { *(.ARM.extab* .gnu.linkonce.armextab.*) } > FLASH
    .ARM.exidx : { __exidx_start = .; *(.ARM.exidx*) __exidx_end = .; } > FLASH

    .preinit_array :
    {
        PROVIDE_HIDDEN(__preinit_array_start = .);
        KEEP(*(.preinit_array*))
        PROVIDE_HIDDEN(__preinit_array_end = .);
    } > FLASH

    .init_array :
    {
        PROVIDE_HIDDEN(__init_array_start = .);
        KEEP(*(SORT(.init_array.*)))
        KEEP(*(.init_array*))
        PROVIDE_HIDDEN(__init_array_end = .);
    } > FLASH

    .fini_array :
    {
        PROVIDE_HIDDEN(__fini_array_start = .);
        KEEP(*(SORT(.fini_array.*)))
        KEEP(*(.fini_array*))
        PROVIDE_HIDDEN(__fini_array_end = .);
    } > FLASH

    .data : ALIGN(4)
    {
        __data_start__ = .;
        _sdata = .;
        *(.data*)
        . = ALIGN(4);
        _edata = .;
        __data_end__ = .;
    } > RAM AT > FLASH
    __data_load__ = LOADADDR(.data);
    _sidata = LOADADDR(.data);
    __etext = LOADADDR(.data);

    .bss (NOLOAD) : ALIGN(4)
    {
        __bss_start__ = .;
        _sbss = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
        __bss_end__ = .;
    } > RAM

    .noinit (NOLOAD) : ALIGN(4)
    {
        *(.noinit*)
    } > RAM

    /* Nordic's gcc_startup_nrf52840.S defines __StackTop/__StackLimit and
     * __HeapBase/__HeapLimit inside these input sections. Collect them here. */
    .heap_dummy (NOLOAD) : ALIGN(8)
    {
        *(.heap)
        *(.heap*)
    } > RAM

    .stack_dummy (NOLOAD) : ALIGN(8)
    {
        *(.stack)
        *(.stack*)
    } > RAM

    __end__ = .;
    end = .;

    /DISCARD/ : { *(.note.GNU-stack) }
}

ASSERT(__bss_end__ <= __HeapBase, "RAM overflow: data/BSS overlaps heap")
ASSERT(__HeapLimit <= __StackLimit, "RAM overflow: heap overlaps stack")
