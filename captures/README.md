# BLE Captures

This directory contains raw Bluetooth Low Energy captures from the Carawater ISP15.

The captures are used to reverse engineer and verify the ISP15 BLE protocol.

## Test device

```text
Device: Carawater ISP15
BLE name: ISP_42_539c
```

Individual ISP15 devices may use different BLE names.

## Capture format

Each capture should include, whenever possible:

- Date and time
- Pump state
- Selected pressure level
- Values displayed by the official Carawater app
- BLE characteristic
- Raw hexadecimal packet
- Additional notes about the test conditions

Example:

```text
Date: 2026-10-19
State: Running
Pressure level: 2

App values:
Voltage: 13.2 V
Current: 2.5 A
Temperature: 14.0 °C
Pressure: 2.00 bar
Flow: 1.4 L/min

Characteristic:
FF01

Raw:
AA93...
```

## Important

Raw captures should not be modified after recording.

Interpretations of the protocol belong in:

`docs/protocol.md`

This separation allows findings to be checked again later if assumptions about the protocol change.
