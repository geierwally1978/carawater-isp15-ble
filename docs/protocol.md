# Carawater ISP15 BLE Protocol

> Reverse-engineering notes for the Bluetooth Low Energy protocol used by the Carawater ISP15 water pump.

## Project status

🚧 **Work in progress**

This protocol is currently being reverse engineered using controlled comparisons between values displayed by the official Carawater app and raw BLE data.

The current focus is the `FF01` status characteristic.

No unknown or guessed commands have been written to `FF02`.

---

# Device

Tested device:

| Property | Value |
|---|---|
| Device | Carawater ISP15 |
| BLE name | `ISP_42_539c` |
| BLE type | Bluetooth Low Energy |
| Pairing | Not required during current tests |

The BLE name may differ between individual ISP15 units.

---

# GATT structure

## Device Information Service

Service:

```text
0x180A
```

Observed characteristics:

| UUID | Description | Properties |
|---|---|---|
| `0x2A24` | Model Number String | Read |
| `0x2A25` | Serial Number String | Read |
| `0x2A27` | Hardware Revision String | Read |
| `0x2A28` | Software Revision String | Read |
| `0x2A29` | Manufacturer Name String | Read |

---

## Custom ISP15 Service

Service UUID:

```text
0000FF00-0000-1000-8000-00805F9B34FB
```

Two custom characteristics were discovered.

### FF01 – status / telemetry

UUID:

```text
0000FF01-0000-1000-8000-00805F9B34FB
```

Properties:

```text
READ
NOTIFY
```

FF01 carries status and telemetry information from the ISP15.

Normal observed status frames begin with:

```text
AA 93
```

---

### FF02 – commands

UUID:

```text
0000FF02-0000-1000-8000-00805F9B34FB
```

Properties:

```text
WRITE
WRITE_NO_RESPONSE
NOTIFY
```

FF02 is the most likely characteristic used by the official app to control the ISP15.

Expected commands include:

- ON
- OFF
- Pressure Level 1
- Pressure Level 2
- Pressure Level 3
- Reset

The actual command format has **not yet been captured or confirmed**.

No guessed commands should be sent to the device.

---

# FF01 status frame

A typical FF01 frame starts with:

```text
AA 93
```

Example:

```text
AA 93 25 14 00 00 88 00 00 00 14 01 8C 00 00 00 00 00 3D ...
```

Several fields can already be correlated with values shown by the official app.

---

# Current field map

Offsets are zero-based.

| Offset | Example | Current interpretation | Confidence |
|---:|---|---|---|
| 0 | `AA` | Frame header | Confirmed |
| 1 | `93` | Frame type/header | Confirmed in observed normal frames |
| 2 | `25` / `45` / `65` / `20` | Status / mode flags | Confirmed dynamic, encoding unknown |
| 3 | `14` | Unknown | Unknown |
| 4–5 | `00 00` | Unknown | Unknown |
| 6 | `88` | Supply voltage, probably value / 10 | Strong evidence |
| 7–9 | varies | Unknown | Unknown |
| 10–11 | varies | Unknown dynamic field | Unknown |
| 12 | `8C` | Water temperature, probably value / 10 | Strong evidence |
| 13–17 | varies / zero | Unknown | Unknown |
| 18 | `3D` | Total water volume, at least for observed values | Strong evidence |
| remaining | varies | Unknown | Unknown |
| final byte | varies | Possible checksum / CRC | Suspected |

This table will be updated as more controlled captures become available.

---

# Supply voltage

During controlled testing the official app displayed:

```text
13.6 V
```

At the same time, FF01 contained at offset 6:

```text
88
```

Hexadecimal `0x88` equals decimal `136`.

This strongly suggests:

```text
voltage = byte[6] / 10
```

Example:

```text
0x88 = 136
136 / 10 = 13.6 V
```

Another capture contained:

```text
0x87 = 135
```

which would represent:

```text
13.5 V
```

A small voltage change between disconnecting the official app and reading with BLE Scanner is plausible.

**Status: strong evidence, not yet considered fully confirmed.**

---

# Water temperature

During all controlled tests the official app displayed:

```text
14.0 °C
```

FF01 consistently contained at offset 12:

```text
8C
```

Hexadecimal `0x8C` equals decimal `140`.

This strongly suggests:

```text
water_temperature = byte[12] / 10
```

Example:

```text
0x8C = 140
140 / 10 = 14.0 °C
```

**Status: strong evidence.**

A future test at a different water temperature is required for final confirmation.

---

# Total water volume

During controlled testing the official app displayed:

```text
Total flow: 61 L
```

FF01 contained at offset 18:

```text
3D
```

Hexadecimal `0x3D` equals decimal `61`.

This strongly suggests that this field contains the total water volume.

Example:

```text
0x3D = 61
```

Earlier captures also showed this field changing as the total value displayed by the app increased.

The size and possible multi-byte representation of this counter still need to be investigated, especially for values above 255 L.

**Status: strong evidence.**

---

# Status / mode byte

Offset 2 is one of the most interesting fields currently under investigation.

Controlled tests were performed with:

- no water tap opened
- pump motor stopped
- same temperature
- same total water volume
- nearly identical supply voltage
- only the pressure level changed

The following values were observed:

| State | Offset 2 |
|---|---:|
| Level 1, stopped | `0x25` |
| Level 2, stopped | `0x45` |
| Level 3, stopped | `0x65` |

This gives the pattern:

```text
Level 1: 0x25
Level 2: 0x45
Level 3: 0x65
```

The difference between pressure levels is:

```text
+0x20
```

This is strong evidence that pressure-level information is encoded in this byte.

However, offset 2 is **not simply the pressure-level number**.

---

# Additional status flags

After switching the ISP15 OFF using the official app and then switching it ON again, the following state was observed:

Official app:

```text
Status:            Stopped
Pressure level:    1
Voltage:           13.6 V
Current:           0.00 A
Water temperature: 14.0 °C
Water pressure:    1.91 bar
Flow:              0.0 L/min
Total flow:        61 L
```

Immediately afterwards FF01 started with:

```text
AA 93 20 14 ...
```

This is different from the previously observed stable Level 1 stopped state:

```text
AA 93 25 14 ...
```

Therefore:

```text
0x20
0x25
```

can both occur while the official app reports Level 1.

This strongly suggests that offset 2 is a **bit field containing multiple status flags**, rather than a simple mode value.

Possible information encoded in this byte may include:

- selected pressure level
- initialization state
- pump enabled state
- pump running/stopped state
- other controller status flags

The individual bits have not yet been decoded.

---

# Controlled pressure-level captures

## Level 1 – stopped

App:

```text
Voltage:           13.6 V
Current:           0.00 A
Water temperature: 14.0 °C
Water pressure:    1.90 bar
Flow:              0.0 L/min
Total flow:        61 L
```

FF01 prefix:

```text
AA 93 25 14 00 00 88 00 00 00 14 01 8C 00 00 00 00 00 3D
```

---

## Level 2 – stopped

App:

```text
Voltage:           13.6 V
Current:           0.00 A
Water temperature: 14.0 °C
Water pressure:    1.91 bar
Flow:              0.0 L/min
Total flow:        61 L
```

FF01 prefix:

```text
AA 93 45 14 00 00 88 00 00 00 16 01 8C 00 00 00 00 00 3D
```

---

## Level 3 – stopped

App:

```text
Voltage:           13.6 V
Current:           0.00 A
Water temperature: 14.0 °C
Water pressure:    1.90 bar
Flow:              0.0 L/min
Total flow:        61 L
```

FF01 prefix:

```text
AA 93 65 14 00 00 87 00 00 00 15 01 8C 00 00 00 00 00 3D
```

The complete raw captures are stored separately in the `captures/` directory.

---

# OFF behaviour

The ISP15 was switched OFF using the official Carawater app.

Immediately afterwards BLE Scanner initially displayed:

```text
00 00 00 00 00 00 00 00 00 30
```

However, a subsequent manual read of FF01 produced no displayed value.

Therefore the short value above is **not considered a confirmed OFF-state packet**.

It could represent:

- a transitional response
- cached data
- a temporary controller state
- another protocol message

What can currently be stated with confidence:

> After switching the ISP15 OFF, normal `AA 93 ...` FF01 telemetry was no longer available during the test.

Further testing is required.

---

# Dynamic fields

Earlier captures made while water was flowing showed several fields changing rapidly.

Examples:

```text
AA933514000085001700D400960012...
AA933514000086001400A900960014...
AA933514000084001A00AA00960031...
AA933514000084001800C900960012...
AA933514000085001800030196000F...
AA933514000084001900370196000D...
AA933514000084001A00590196000B...
```

These captures indicate that multiple fields near the beginning of FF01 represent live operating data.

Likely candidates still to decode include:

- motor current
- water pressure
- real-time flow

Controlled tests with the pump running will be required to identify these fields reliably.

---

# Final byte

The final byte of FF01 changes when packet contents change.

Observed examples include:

```text
03
02
01
13
E8
0A
41
73
94
6E
36
58
76
30
```

This may be a:

- checksum
- CRC
- sequence value
- other integrity/status field

The algorithm or meaning is currently unknown.

It should **not yet be described as a checksum with certainty**.

---

# Connection behaviour

During testing:

- The official Carawater app can connect successfully.
- BLE Scanner on iOS can connect successfully.
- The official app and BLE Scanner cannot be used with the ISP15 simultaneously.
- Linux/BlueZ was able to initiate a connection during earlier testing but did not maintain it reliably.

The ISP15 therefore appears to support only one active BLE client connection in the tested setup.

This makes direct observation of the official app's FF02 writes more difficult.

---

# Current findings

## Confirmed

- ISP15 uses Bluetooth Low Energy.
- Custom service is `FF00`.
- FF01 supports Read and Notify.
- FF02 supports Write, Write Without Response and Notify.
- FF01 carries status/telemetry data.
- Normal observed FF01 frames begin with `AA 93`.
- FF01 changes with the operating state.
- Offset 2 changes with pressure level and other device states.
- Pressure levels 1–3 produce reproducibly different offset-2 values under controlled stopped conditions.
- Normal FF01 telemetry disappears when the ISP15 is switched OFF in the tested scenario.

## Strong evidence

- Offset 6 represents supply voltage with scaling `/10`.
- Offset 12 represents water temperature with scaling `/10`.
- Offset 18 represents total water volume.
- Offset 2 is a status/mode bit field.
- Pressure-level information is encoded in offset 2.

## Suspected

- FF02 carries commands from the official app.
- The final FF01 byte may be an integrity/checksum field.

## Unknown

- Exact bit layout of offset 2.
- Motor current field.
- Water pressure field.
- Real-time flow field.
- Daily water volume field.
- Multi-byte format of total water volume.
- ON command.
- OFF command.
- Level 1 command.
- Level 2 command.
- Level 3 command.
- Reset command.
- Final-byte algorithm/meaning.
- Error-code representation.

---

# Next steps

1. Build a read-only BLE test client.
2. Read and log FF01 automatically.
3. Decode the already strongly suspected fields:
   - voltage
   - temperature
   - total water volume
4. Perform controlled running tests to identify:
   - current
   - pressure
   - real-time flow
5. Investigate the individual bits of offset 2.
6. Capture FF02 writes from the official app.
7. Determine the command protocol.
8. Only after commands are understood, test controlled writes.
9. Build a Home Assistant integration.

---

# Safety during reverse engineering

Until the FF02 protocol is understood:

> Do not send guessed or random data to FF02.

Reading FF01 is sufficient for the current analysis and avoids sending unknown commands to the pump controller.

---

# Goal

The long-term goal is local monitoring and control of the Carawater ISP15 without requiring the official mobile application.

Potential integrations include:

- Python BLE client
- Raspberry Pi / Linux
- Home Assistant
- ESPHome

---

# Raw captures

Raw and controlled test data are stored in:

```text
captures/
```

Interpretations belong in this document, while raw observations are kept separately so hypotheses can be checked against the original measurements.

---

# Disclaimer

This is an independent reverse-engineering project and is not affiliated with or endorsed by Carawater.

The documentation is based on observations of personally owned hardware and is intended for research and interoperability.

Information may change as the protocol becomes better understood.

Use at your own risk.
