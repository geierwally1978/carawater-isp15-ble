# Carawater ISP15 BLE Protocol

> Reverse-engineering notes for the Bluetooth Low Energy protocol used by the Carawater ISP15 water pump.

## Project status

🚧 **Work in progress**

This protocol is currently being reverse engineered.

The information in this document is based on BLE observations and comparisons with values displayed by the official Carawater app.

Unless explicitly marked as **confirmed**, protocol fields should be considered preliminary.

No write commands have been tested against the pump yet.

---

# Device

Tested device:

| Property | Value |
|---|---|
| Device | Carawater ISP15 |
| BLE name | `ISP_42_539c` |
| BLE type | Bluetooth Low Energy |
| Pairing | Not required |
| Bonding | Not required |

The device exposes the standard Device Information Service and one custom BLE service.

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

### FF01 – status/data

UUID:

```text
0000FF01-0000-1000-8000-00805F9B34FB
```

Properties:

```text
READ
NOTIFY
```

Current assumption:

**FF01 carries status and measurement data from the ISP15 to the BLE client.**

This is strongly supported by changing values observed while the pump was running.

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

Current assumption:

**FF02 is used by the app to send commands/configuration to the ISP15.**

This is not yet confirmed because write traffic from the official app has not yet been captured.

---

# Status packets

Reads from FF01 return a comparatively long binary packet.

Observed packets start with:

```text
AA 93
```

Example while the pump was stopped:

```text
AA93251400008A000000F800960000000000390000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003601040100000000000000000000000000000000000000000000000003
```

Another observed stopped-state packet:

```text
AA932514000088000000640196000000000039000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000360104010000000000000000000000000000000000000000000000006E
```

---

# Known app values

The official Carawater app displays at least the following live information:

- Supply voltage (V)
- Current (A)
- Water temperature (°C)
- Water pressure (bar)
- Real-time flow (L/min)
- Daily water volume (L)
- Total water volume (L)
- Pump running/stopped
- Error status
- Constant-pressure mode
  - Level 1
  - Level 2
  - Level 3

The app also provides:

- ON/OFF
- Reset
- Selection of constant-pressure level 1–3

These functions are expected to correspond to commands sent through FF02.

---

# Constant-pressure levels

The ISP15 provides three selectable constant-pressure modes.

BLE status data was recorded for all three modes.

## Level 1

Observed FF01 packet:

```text
AA935514000086001700E9008C001C0000003B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000A0036010401000000000000000000000000000000000000000000000055
```

Official app showed approximately:

```text
Voltage:     13.2 V
Current:      2.8 A
Temperature: 14.0 °C
Pressure:     1.21 bar
Flow:         4.8 L/min
Mode:         Level 1
```

---

## Level 2

Observed FF01 packet:

```text
AA93451400008A00000047018C00000000003B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000A0036010401000000000000000000000000000000000000000000000075
```

The app confirmed:

```text
Mode: Level 2
```

During a later running measurement the app displayed approximately:

```text
Voltage:     13.2 V
Current:      2.5 A
Temperature: 14.0 °C
Pressure:     2.00 bar
Flow:         1.4 L/min
```

---

## Level 3

Observed FF01 packet:

```text
AA93651400008A00000047018C00000000003B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000A0036010401000000000000000000000000000000000000000000000095
```

The app confirmed:

```text
Mode: Level 3
```

During a later running measurement the app displayed approximately:

```text
Voltage:     13.2 V
Current:      2.9 A
Temperature: 14.0 °C
Pressure:     1.79 bar
Flow:         3.3 L/min
```

---

# Interesting packet differences

The packets recorded for the three constant-pressure modes contain a very interesting difference near the beginning.

Observed prefixes:

```text
Level 1:
AA 93 55 14 ...

Level 2:
AA 93 45 14 ...

Level 3:
AA 93 65 14 ...
```

This suggests that byte(s) near this position may contain mode/status flags.

Current observation:

| Mode | Observed byte |
|---|---:|
| Level 1 | `0x55` |
| Level 2 | `0x45` |
| Level 3 | `0x65` |

⚠️ **Not yet confirmed**

The value may contain multiple bit flags rather than being a simple numeric representation of the selected pressure level.

More controlled captures are required.

---

# Running vs stopped

A change between stopped and running operation can also be seen near the beginning of the packet.

Examples:

Stopped:

```text
AA 93 25 14 ...
```

Running examples:

```text
AA 93 35 14 ...
AA 93 55 14 ...
```

This suggests that byte 2 (zero-based) contains several status bits.

Possible information encoded here may include:

- pump running/stopped
- selected constant-pressure mode
- additional state flags

This remains under investigation.

---

# Dynamic measurements

A sequence recorded while water was flowing showed several fields changing rapidly.

Example:

```text
AA933514000085001700D400960012...
AA933514000086001400A900960014...
AA933514000084001A00AA00960031...
AA933514000084001800C900960012...
AA933514000085001800030196000F...
AA933514000084001900370196000D...
AA933514000084001A00590196000B...
```

This is useful because it strongly indicates that the first approximately 20 bytes contain the live measurements displayed by the app.

Likely candidates include:

- voltage
- current
- temperature
- pressure
- flow

The exact byte positions and scaling factors are still being determined.

---

# Packet ending

The last byte changes together with packet contents.

Examples:

```text
...03
...02
...01
...13
...E8
...0A
...41
...73
...94
...6E
```

This strongly suggests that the final byte may be a checksum or CRC.

⚠️ The checksum algorithm has not yet been identified.

Determining this will be important before generating commands for FF02.

---

# Connection behaviour

The ISP15 appears to allow only one active BLE client connection.

Observed behaviour:

- The official Carawater app can maintain a stable connection.
- A BLE scanner can also maintain a stable connection.
- The official app and BLE scanner cannot interact with the device simultaneously.
- Linux/BlueZ was able to initiate a connection but disconnected shortly afterwards during initial testing.

Therefore capturing app-generated FF02 commands requires a different approach than simply connecting a second BLE client.

---

# Current findings

## Confirmed

- ISP15 uses Bluetooth Low Energy.
- Custom service UUID is `FF00`.
- `FF01` supports Read + Notify.
- `FF02` supports Write + Write Without Response + Notify.
- FF01 contains live device/status information.
- FF01 packets start with `AA 93` in all observations so far.
- Packet contents change when the pump runs.
- Packet contents change between pressure levels 1, 2 and 3.
- The official app can select pressure levels 1–3.
- Only one BLE client appears to be usable at a time.

## Probable

- FF02 carries control commands.
- Byte 2 contains several status/mode flags.
- The final byte is a checksum/CRC.
- Several live sensor values are contained in the first part of FF01.

## Unknown

- Exact FF02 command format.
- ON command.
- OFF command.
- Level 1 command.
- Level 2 command.
- Level 3 command.
- Reset command.
- Exact field offsets for all measurements.
- Scaling factors.
- Checksum/CRC algorithm.
- Error-code representation.

---

# Next steps

The next reverse-engineering steps are:

1. Capture writes sent by the official app to FF02.
2. Identify commands for:
   - ON
   - OFF
   - Level 1
   - Level 2
   - Level 3
   - Reset
3. Compare controlled FF01 captures against known app values.
4. Determine byte offsets and scaling factors for:
   - voltage
   - current
   - temperature
   - pressure
   - flow
   - daily volume
   - total volume
5. Determine the checksum/CRC algorithm.
6. Build a small test client.
7. Integrate the protocol with Home Assistant.

---

# Goal

The long-term goal of this project is local control and monitoring of the Carawater ISP15 without requiring the official mobile application.

Possible future integrations include:

- Python BLE library
- Raspberry Pi BLE client
- Home Assistant integration
- ESPHome BLE client

---

# Disclaimer

This project is an independent reverse-engineering effort and is not affiliated with or endorsed by Carawater.

Use the information at your own risk.

The protocol documentation may contain errors while reverse engineering is still in progress.
