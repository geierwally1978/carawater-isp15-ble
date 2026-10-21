# Controlled BLE Tests – 2026-10-21

Device: Carawater ISP15  
BLE name: `ISP_42_539c`  
Status characteristic: `FF01`

## Test conditions

The tests were performed without opening a water tap.

The official Carawater app and BLE Scanner cannot be connected to the ISP15 simultaneously.

Procedure:

1. Connect using the official app.
2. Set the desired state.
3. Record the values displayed by the app.
4. Disconnect the official app.
5. Connect using BLE Scanner.
6. Read FF01.

---

## Test 1 – Pressure Level 2, stopped

App values:

```text
Status:            Stopped
Pressure level:    2
Voltage:           13.6 V
Current:           0.00 A
Water temperature: 14.0 °C
Water pressure:    1.91 bar
Flow:              0.0 L/min
Daily flow:        0 L
Total flow:        61 L
```

FF01 starts with:

```text
AA 93 45 14 00 00 88 00 00 00 16 01 8C 00 00 00 00 00 3D
```

Observed final byte:

```text
58
```

---

## Test 2 – Pressure Level 3, stopped

App values:

```text
Status:            Stopped
Pressure level:    3
Voltage:           13.6 V
Current:           0.00 A
Water temperature: 14.0 °C
Water pressure:    1.90 bar
Flow:              0.0 L/min
Daily flow:        0 L
Total flow:        61 L
```

FF01 starts with:

```text
AA 93 65 14 00 00 87 00 00 00 15 01 8C 00 00 00 00 00 3D
```

Observed final byte:

```text
76
```

---

## Test 3 – Pressure Level 1, stopped

App values:

```text
Status:            Stopped
Pressure level:    1
Voltage:           13.6 V
Current:           0.00 A
Water temperature: 14.0 °C
Water pressure:    1.90 bar
Flow:              0.0 L/min
Daily flow:        0 L
Total flow:        61 L
```

FF01 starts with:

```text
AA 93 25 14 00 00 88 00 00 00 14 01 8C 00 00 00 00 00 3D
```

Observed final byte:

```text
36
```

---

## Test 4 – Pump switched OFF using official app

Starting state:

```text
Pressure level: 1
Status:         Stopped
```

After pressing ON/OFF in the official app, BLE Scanner initially displayed:

```text
00 00 00 00 00 00 00 00 00 30
```

A subsequent manual read of FF01 returned no displayed value.

### Important

The short packet ending in `30` is **not yet confirmed as an OFF status packet**.

It may be a transitional response or another temporary state.

Confirmed observation:

> Normal `AA 93 ...` telemetry was no longer available from FF01 after switching the ISP15 off.

---

## Test 5 – ISP15 switched ON again

The ISP15 was switched on again using the official app.

App values:

```text
Status:            Stopped
Pressure level:    1
Voltage:           13.6 V
Current:           0.00 A
Water temperature: 14.0 °C
Water pressure:    1.91 bar
Flow:              0.0 L/min
Daily flow:        0 L
Total flow:        61 L
```

Immediately afterwards FF01 started with:

```text
AA 93 20 14 00 00 88 00 00 00 13 01 8C 00 00 00 00 00 3D
```

Observed final byte:

```text
30
```

This differs from the previously observed Level 1 stopped state:

```text
AA 93 25 14 ...
```

Therefore byte 2 cannot currently be interpreted simply as the pressure level.

---

## Findings from this test

Strongly supported field candidates:

```text
Offset 6:
0x88 = 136
Possible voltage encoding: 13.6 V

Offset 12:
0x8C = 140
Possible temperature encoding: 14.0 °C

Offset 18:
0x3D = 61
Possible total flow encoding: 61 L
```

Pressure-level/status observations:

```text
Level 1, stopped: 0x25
Level 2, stopped: 0x45
Level 3, stopped: 0x65

Level 1 immediately after switching ON:
0x20
```

The pattern `0x25 / 0x45 / 0x65` strongly correlates with pressure levels 1–3 under the tested stopped conditions.

However, byte 2 appears to contain additional state information and should currently be treated as a **status/flags byte**, not simply a pressure-level byte.

Further testing is required.
