# Carawater ISP15 BLE

Reverse engineering and open documentation of the Bluetooth Low Energy protocol used by the **Carawater ISP15** water pump.

> 🚧 **Work in progress**
>
> The protocol is currently being reverse engineered.  
> Reading status data is already possible, while control commands are still under investigation.

## 🎯 Project goal

The goal is to understand and document the BLE protocol of the Carawater ISP15 in order to enable **local monitoring and control without the official mobile app**.

Possible future integrations:

- Home Assistant
- ESPHome
- Raspberry Pi / Linux
- Python BLE clients

The main target for this project is a **Home Assistant integration**.

---

## 🔵 BLE interface

The ISP15 exposes the following custom BLE service:

```text
Service
FF00

Status / data
FF01 – READ, NOTIFY

Commands
FF02 – WRITE, WRITE_NO_RESPONSE, NOTIFY
```

Full UUIDs:

```text
0000FF00-0000-1000-8000-00805F9B34FB
0000FF01-0000-1000-8000-00805F9B34FB
0000FF02-0000-1000-8000-00805F9B34FB
```

Observed status packets currently start with:

```text
AA 93
```

---

## 🔍 What has been discovered?

Current reverse-engineering progress:

| Feature | Status |
|---|---|
| BLE service discovery | ✅ Confirmed |
| Status characteristic FF01 | ✅ Confirmed |
| Command characteristic FF02 | ✅ Confirmed |
| Reading status packets | ✅ Working |
| Pump running/stopped detection | 🧪 Under investigation |
| Pressure level detection | 🧪 Under investigation |
| Voltage | 🧪 Decoding in progress |
| Current | 🧪 Decoding in progress |
| Water temperature | 🧪 Decoding in progress |
| Water pressure | 🧪 Decoding in progress |
| Water flow | 🧪 Decoding in progress |
| Daily water volume | ❓ Unknown |
| Total water volume | ❓ Unknown |
| ON/OFF command | ❓ Unknown |
| Pressure level 1 command | ❓ Unknown |
| Pressure level 2 command | ❓ Unknown |
| Pressure level 3 command | ❓ Unknown |
| Reset command | ❓ Unknown |
| Checksum / CRC | 🧪 Under investigation |

---

## 📊 Available data

The official Carawater application displays several values that appear to be transmitted through FF01:

- Supply voltage
- Current
- Water temperature
- Water pressure
- Real-time water flow
- Daily water volume
- Total water volume
- Pump running/stopped
- Error status
- Constant-pressure level 1–3

Controlled BLE captures have already been recorded for different operating states and pressure levels.

---

## 📖 Protocol documentation

Detailed reverse-engineering notes, packet examples and current findings are available here:

➡️ [BLE protocol documentation](docs/protocol.md)

The documentation distinguishes between:

- **Confirmed** observations
- **Probable** interpretations
- **Unknown** protocol fields

This is important because the protocol is still being analysed.

---

## 🧪 Test device

Current development and testing is performed with:

```text
Device:   Carawater ISP15
BLE name: ISP_42_539c
```

The BLE name may differ between individual ISP15 units.

---

## 🛠️ Planned next steps

The next major goal is capturing and decoding commands sent by the official application to **FF02**.

Especially:

```text
ON
OFF
Pressure Level 1
Pressure Level 2
Pressure Level 3
Reset
```

After the command protocol is understood, the plan is to create a small BLE client and eventually integrate the ISP15 into Home Assistant.

---

## 🤝 Contributions

Additional captures and information from other ISP15 owners are welcome.

Useful contributions include:

- BLE captures
- FF01 status packets
- FF02 command packets
- observations from different ISP15 firmware versions
- decoded packet fields
- checksum / CRC analysis

Please include the corresponding pump state and values displayed by the official app whenever possible.

---

## ⚠️ Disclaimer

This is an independent community reverse-engineering project.

It is **not affiliated with, supported by, or endorsed by Carawater**.

All information is provided for research and interoperability purposes and may contain errors while reverse engineering is still in progress.

Use at your own risk.
