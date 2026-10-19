# Pressure Level Captures

Date: 2026-10-19  
Device: Carawater ISP15  
BLE characteristic: FF01

## Purpose

Compare FF01 status packets after selecting the three constant-pressure levels in the official Carawater app.

Because the official app and BLE Scanner could not be connected to the ISP15 at the same time, the procedure was:

1. Connect with the official Carawater app.
2. Select the desired pressure level.
3. Disconnect the official app.
4. Connect using BLE Scanner.
5. Read the FF01 characteristic.

Therefore, these captures show the ISP15 state **after** selecting a pressure level. They do not contain the FF02 command used by the official app to change the level.

---

## Pressure Level 1

Source: BLE Scanner

```text
AA93451400008A00000047018C00000000003B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000A0036010401000000000000000000000000000000000000000000000075
```

Additional observed state:

```text
AA93251400008A00000047018C00000000003B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000A0036010401000000000000000000000000000000000000000000000055
```

Notes:

- Pressure level 1 had previously been selected in the official app.
- Two different FF01 states were observed.
- The difference must not yet be interpreted as the pressure-level value itself.

---

## Pressure Level 2

Source: BLE Scanner

```text
AA935514000086001700E9008C001C0000003B000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000A0036010401000000000000000000000000000000000000000000000055
```

Notes:

- Pressure level 2 had previously been selected in the official app.
- Pump/water was active during this observation.

---

## Pressure Level 3

Source: BLE Scanner

```text
AA93651400008900000060018C00000001003D000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000A000A00360104010000000000000000000000000000000000000000000000BA
```

Notes:

- Pressure level 3 had previously been selected in the official app.

---

## Initial observations

The beginning of the packets differs between the captures:

```text
Level 1:
AA 93 45 14 ...
AA 93 25 14 ...

Level 2:
AA 93 55 14 ...

Level 3:
AA 93 65 14 ...
```

The third byte clearly changes between several observed operating states.

However, it is currently **not confirmed** that this byte directly represents the selected pressure level.

It may instead be a bit field containing multiple state flags.

Further controlled captures are required.

---

## Open questions

- Which byte(s) represent the selected pressure level?
- Which bit represents pump running/stopped?
- Does the selected pressure level remain encoded when the pump is stopped?
- Which fields represent voltage, current, pressure and flow?
- Is the final byte a checksum?
