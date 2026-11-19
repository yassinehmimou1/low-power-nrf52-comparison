# Architecture

## Functional scenario

The comparison fixes the application workload and changes the software architecture. The nominal period is 5 seconds, the optional LED pulse is 50 ms, and the shared CPU workload performs 4,096 deterministic integer iterations.

```text
                 +-----------------------------+
                 |  Periodic wake-up source    |
                 +--------------+--------------+
                                |
               +----------------+----------------+
               |                                 |
        Bare-metal path                    Zephyr path
        RTC2 COMPARE0                      Kernel timer expiry
        RTC2 ISR                           Timer callback (ISR)
               |                                 |
        Set event flag                      Give semaphore
               |                                 |
        Main loop wakes                     Main thread wakes
               |                                 |
               +----------------+----------------+
                                |
                     Assert P0.03 marker
                                |
                     Shared CPU workload
                                |
                     Deassert P0.03 marker
                                |
                     Optional LED pulse
                                |
                     Return to idle
```

## Hardware resource allocation

| Resource | Bare-metal | Zephyr |
|---|---|---|
| CPU | Cortex-M4F | Cortex-M4F under Zephyr scheduler |
| LFCLK | 32.768 kHz crystal explicitly started | Board clock configuration |
| Periodic timebase | RTC2 | Zephyr system clock backend |
| LED | P0.13 direct register | `led0` DeviceTree alias / GPIO driver |
| Marker | P0.03 direct register | `zephyr,user/marker-gpios` |
| Sleep | `__WFE()` | Zephyr idle thread / SoC idle implementation |

## System ON vs System OFF

The benchmark uses **System ON idle**. The CPU waits for an event, while the RTC remains active and RAM is retained. This permits the periodic RTC wake-up without rebooting.

System OFF is a distinct, deeper state. The nRF52840 internal RTC cannot wake the chip from System OFF; a supported GPIO/NFC/LPCOMP/USB/reset wake source is required, and wake-up restarts execution. A System OFF comparison therefore needs a separate application scenario and should not be mixed into this periodic System ON experiment.

## Design fairness

The timer peripherals are not identical: bare-metal uses RTC2 explicitly; Zephyr uses the Zephyr system clock implementation. The shared workload, GPIO marker, period and pulse duration are held constant. The difference in timer/OS overhead is part of the comparison and must be measured rather than assumed.
