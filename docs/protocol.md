# Carawater ISP15 – BLE-Protokoll

Diese Datei dokumentiert den aktuellen Stand des Reverse Engineerings
des Bluetooth-Low-Energy-Protokolls der Carawater ISP15.

Der Schwerpunkt liegt zunächst auf der rein lesenden Telemetrie über FF01.

> **Wichtig:** Einige Felder und Skalierungen sind noch nicht vollständig
> bestätigt. Vermutungen werden ausdrücklich als solche gekennzeichnet.

---

## BLE-Gerät

Beobachteter Gerätename:

```text
ISP_42_539c
```

Die vom Betriebssystem angezeigte Geräte-ID ist plattformabhängig.

Unter Linux wurde beispielsweise folgende BLE-Adresse beobachtet:

```text
9C:53:BF:10:5E:E7
```

Unter Apple-Systemen wird stattdessen eine CoreBluetooth-UUID verwendet.
Diese kann sich zwischen macOS und iOS unterscheiden.

Eine Integration sollte das Gerät deshalb bevorzugt über den
BLE-Gerätenamen finden und keine Apple-CoreBluetooth-UUID fest eintragen.

---

# GATT-Struktur

## Device Information Service

UUID:

```text
0000180A-0000-1000-8000-00805F9B34FB
```

Beobachtete Characteristics:

| UUID | Bedeutung | Eigenschaft |
|---|---|---|
| 2A24 | Model Number String | Read |
| 2A25 | Serial Number String | Read |
| 2A27 | Hardware Revision String | Read |
| 2A28 | Software Revision String | Read |
| 2A29 | Manufacturer Name String | Read |

---

## Carawater Custom Service

Service UUID:

```text
0000FF00-0000-1000-8000-00805F9B34FB
```

### FF01 – Telemetrie

UUID:

```text
0000FF01-0000-1000-8000-00805F9B34FB
```

Eigenschaften:

```text
Read
Notify
```

FF01 liefert die laufenden Status- und Messdaten des ISP15.

Ein direkter GATT-Read lieferte bei den bisherigen Tests keine Nutzdaten.

Nach Aktivierung von Notifications werden dagegen automatisch ungefähr
alle zwei Sekunden Telemetrieframes übertragen.

Für den Empfang der Telemetrie ist kein vorheriger Schreibzugriff auf
FF02 erforderlich.

---

### FF02 – Steuerung

UUID:

```text
0000FF02-0000-1000-8000-00805F9B34FB
```

Eigenschaften:

```text
Notify
Write
Write Without Response
```

FF02 ist sehr wahrscheinlich für Steuerbefehle vorgesehen.

Mögliche Befehle sind unter anderem:

- Anlage EIN/AUS
- Konstantdruck Stufe 1
- Konstantdruck Stufe 2
- Konstantdruck Stufe 3
- Reset

Das Befehlsformat ist derzeit noch nicht bekannt.

**Bis das Format verstanden ist, werden keine geratenen Schreibbefehle
an FF02 gesendet.**

---

# FF01-Telemetrieframe

Normale FF01-Telemetrieframes beginnen mit:

```text
AA 93
```

Die bisher beobachteten normalen Telemetrieframes besitzen eine feste
Länge von:

```text
150 Byte
```

Beispiel:

```text
AA 93 21 14 00 00 83 00 00 00 82 01 96 00 00 00 0F 00 53 ...
```

---

# Bekannte Felder

Der aktuelle Stand der Dekodierung:

| Offset | Länge | Bedeutung | Skalierung / Format | Stand |
|---:|---:|---|---|---|
| 0 | 1 | Header | `0xAA` | bestätigt |
| 1 | 1 | Header | `0x93` | bestätigt |
| 2 | 1 | Status- und Modus-Flags | Bitfeld | teilweise dekodiert |
| 6 | 1 | Versorgungsspannung | RAW / 10 V | bestätigt |
| 8 | 1 | Stromaufnahme | Skalierung noch offen | sehr wahrscheinlich |
| 10–11 | 2 | Wasserdruck | Little Endian, Skalierung noch offen | sehr wahrscheinlich |
| 12 | 1 | Wassertemperatur | RAW / 10 °C | bestätigt |
| 14 | 1 | Echtzeit-Durchfluss | Skalierung noch offen | sehr wahrscheinlich |
| 16 | 1 | Tagesmenge | Liter | bestätigt |
| 18 | 1 | Gesamtmenge | Liter bei bisher beobachteten Werten | bestätigt |
| 149 | 1 | Prüfsumme | additive 8-Bit-Prüfsumme | bestätigt |

Die Bedeutung der übrigen Bytes ist noch nicht vollständig geklärt.

---

# Versorgungsspannung

Offset:

```text
6
```

Beispiele:

```text
0x88 = 136 → 13,6 V
0x83 = 131 → 13,1 V
0x81 = 129 → 12,9 V
0x7D = 125 → 12,5 V
0x7C = 124 → 12,4 V
```

Berechnung:

```python
voltage = frame[6] / 10.0
```

Status:

**Bestätigt.**

---

# Wassertemperatur

Offset:

```text
12
```

Beispiele:

```text
0x8C = 140 → 14,0 °C
0x96 = 150 → 15,0 °C
0xAA = 170 → 17,0 °C
0xD2 = 210 → 21,0 °C
```

Berechnung:

```python
water_temperature = frame[12] / 10.0
```

Status:

**Bestätigt.**

---

# Stromaufnahme

Offset:

```text
8
```

Beobachtungen:

```text
Pumpe aus:
RAW 0 → App 0,00 A

Frühere kontrollierte Messung:
RAW 21–22 → App 2,00 A

Frühere Messung:
RAW 23–24 → App ungefähr 2,30 A
```

Am 22.10.2026 wurden weitere kontrollierte Messungen durchgeführt.

Unter anderem wurden bei laufender Pumpe beobachtet:

```text
RAW 28–29 → App ungefähr 2,4–2,5 A
RAW 26    → App ungefähr 2,4 A
```

Die Zuordnung von Offset 8 zur Stromaufnahme ist damit sehr
wahrscheinlich.

Die bisherige einfache Arbeitshypothese

```python
current_A = frame[8] / 10.0
```

passt nicht exakt zu allen beobachteten Referenzwerten und gilt daher
weiterhin nicht als bestätigt.

Weitere kontrollierte Messpunkte sind erforderlich, um die exakte
Skalierung zu bestimmen.

---

# Wasserdruck

Offsets:

```text
10–11
```

Der Wert wird als 16-Bit-Zahl in Little-Endian-Reihenfolge übertragen:

```python
pressure_raw = int.from_bytes(
    frame[10:12],
    byteorder="little",
    signed=False
)
```

Die Little-Endian-Dekodierung wurde durch mehrere Messungen bestätigt.

Beispiele:

```text
3C 01 → 0x013C → RAW 316
E0 00 → 0x00E0 → RAW 224
DB 00 → 0x00DB → RAW 219
DD 00 → 0x00DD → RAW 221
D1 00 → 0x00D1 → RAW 209
06 01 → 0x0106 → RAW 262
0A 01 → 0x010A → RAW 266
67 01 → 0x0167 → RAW 359
```

Frühere Referenzpunkte:

```text
RAW ≈ 386      → App 2,67 bar
RAW ≈ 184–185  → App 1,21 bar
```

Weitere Messungen vom 22.10.2026:

```text
Stufe 3, Pumpe läuft:
RAW ≈ 262–266 → App ungefähr 1,84 bar

Stufe 3, Pumpe gestoppt:
RAW ≈ 359 → App ungefähr 2,47 bar
```

Die bisherige Arbeitshypothese

```text
Druck [bar] ≈ RAW × 0,00723 - 0,12
```

erklärt nicht alle beobachteten Referenzpunkte ausreichend genau.

Die Zuordnung der Offsets 10–11 zum Wasserdruck sowie das
Little-Endian-Format gelten als sehr gut belegt.

Die endgültige Umrechnung von RAW nach bar ist jedoch noch offen.

---

# Echtzeit-Durchfluss

Offset:

```text
14
```

Beobachtungen:

```text
Wasser aus:
RAW 0 → App 0,0 L/min

Frühere kontrollierte Messung:
RAW 19 → App 2,0 L/min

Frühere Messung:
RAW 16–17 → App ungefähr 1,8 L/min
```

Weitere kontrollierte Messungen vom 22.10.2026:

```text
Stufe 3, App 1,5 L/min:
RAW 28
RAW 30
RAW 29
```

Damit ist die Zuordnung von Offset 14 zum Echtzeit-Durchfluss weiterhin
sehr wahrscheinlich.

Die bisherige einfache Arbeitshypothese

```python
flow_lpm = frame[14] / 10.0
```

passt jedoch nicht zu den neuen kontrollierten Messwerten und gilt
daher ausdrücklich nicht als bestätigt.

Die endgültige Skalierung muss mit weiteren Referenzmessungen bestimmt
werden.

---

# Tagesmenge

Offset:

```text
16
```

Während kontrollierter Wasserentnahmen wurde bereits beobachtet:

```text
RAW 16 → App 16 L
RAW 17 → App 17 L
```

Am 22.10.2026 wurde zusätzlich ein gezielter Reset der
Verbrauchszähler über die offizielle Carawater-App durchgeführt.

Unmittelbar vor dem Reset:

```text
Offset 16 = 17 → 17 L Tagesmenge
```

Unmittelbar nach dem Reset:

```text
Offset 16 = 0 → 0 L Tagesmenge
```

Die offizielle App setzte gleichzeitig ebenfalls die Tagesmenge auf
0 Liter zurück.

Bei späteren kontrollierten Wasserentnahmen wurde außerdem der
erwartete Anstieg des Feldes beobachtet:

```text
7 → 8
```

Aktuelle Interpretation:

```python
daily_water_l = frame[16]
```

Status:

**Bestätigt für die bisher beobachteten Werte.**

---

# Gesamtmenge

Offset:

```text
18
```

Bisher beobachtete Beispiele:

```text
0x3D = 61 → 61 L
0x40 = 64 → 64 L
0x53 = 83 → 83 L
0x54 = 84 → 84 L
```

Am 22.10.2026 wurde ein gezielter Reset der Verbrauchszähler über
die offizielle Carawater-App durchgeführt.

Unmittelbar vor dem Reset:

```text
Offset 18 = 84 → 84 L Gesamtmenge
```

Unmittelbar nach dem Reset:

```text
Offset 18 = 0 → 0 L Gesamtmenge
```

Die offizielle App zeigte nach dem Reset ebenfalls 0 Liter
Gesamtmenge an.

Bei späteren kontrollierten Wasserentnahmen wurde außerdem der
erwartete Anstieg des Feldes beobachtet:

```text
7 → 8
```

Aktuelle Interpretation:

```python
total_water_l = frame[18]
```

Status:

**Bestätigt für die bisher beobachteten Werte bis 84 Liter.**

Noch ungeklärt ist, wie Gesamtmengen oberhalb von 255 Litern
übertragen werden. Daher ist zwar die Zuordnung von Offset 18 zum
Gesamtmengenzähler bestätigt, das vollständige Datenformat des
Zählers aber noch nicht bekannt.

---

# Weitere Verbrauchs- und Statistikfelder

Beim gezielten Reset der Verbrauchszähler wurden neben Offset 16 und
Offset 18 auch mehrere bislang unbekannte Felder im hinteren Bereich
des 150-Byte-FF01-Frames auf `0x00` zurückgesetzt.

Dies ist ein deutlicher Hinweis darauf, dass dort weitere
Verbrauchs-, Statistik- oder Zählerdaten gespeichert werden.

Bei kontrollierten Wasserentnahmen am 22.10.2026 wurden außerdem
Veränderungen im hinteren Bereich des Frames beobachtet.

Unter anderem:

```text
Offset 119:
60 → 70
70 → 80
```

Diese Änderungen traten im Zusammenhang mit Wasserentnahmen und
Änderungen der bekannten Literzähler auf.

Bei einer weiteren Messung wurde außerdem eine Änderung an Offset 111
beobachtet:

```text
Offset 111:
60 → 70
```

Die genaue Bedeutung dieser Felder ist derzeit unbekannt.

Insbesondere wird noch nicht angenommen, dass Offset 111 oder 119
direkt eine bestimmte Verbrauchsgröße darstellen.

Die Beobachtungen werden zunächst nur als mögliche zusätzliche
Verbrauchs-, Statistik- oder Zählerfelder dokumentiert.

Der vollständige RAW-Capture unmittelbar nach dem Reset befindet sich
unter:

```text
captures/raw/2026-10-22-after-counter-reset.csv
```

---

# Status-Byte

Offset:

```text
2
```

Das Status-Byte enthält mehrere Status- und Modusinformationen.

Am 22.10.2026 wurden alle sechs Kombinationen aus Konstantdruckstufe
1–3 und Pumpenstatus gestoppt/läuft kontrolliert getestet.

Dabei wurden folgende Werte beobachtet:

| Konstantdruck | Pumpe gestoppt | Pumpe läuft |
|---|---:|---:|
| Stufe 1 | `0x21` | `0x31` |
| Stufe 2 | `0x41` | `0x51` |
| Stufe 3 | `0x61` | `0x71` |

Damit können Konstantdruckstufe und Pumpenstatus unabhängig
voneinander aus dem Status-Byte dekodiert werden.

---

## Pumpenstatus

Der Pumpenstatus wird durch Bit `0x10` dargestellt.

Beispiele:

```text
0x21 → Stufe 1, Pumpe gestoppt
0x31 → Stufe 1, Pumpe läuft

0x41 → Stufe 2, Pumpe gestoppt
0x51 → Stufe 2, Pumpe läuft

0x61 → Stufe 3, Pumpe gestoppt
0x71 → Stufe 3, Pumpe läuft
```

Dekodierung:

```python
pump_running = bool(frame[2] & 0x10)
```

Status:

**Bestätigt durch kontrollierte Messungen aller drei Konstantdruckstufen.**

---

## Konstantdruckstufe

Die Konstantdruckstufe wird durch die Bits der Maske `0x60`
im Status-Byte dargestellt.

Beobachtete Zuordnung:

```text
0x20 → Stufe 1
0x40 → Stufe 2
0x60 → Stufe 3
```

Dekodierung:

```python
mode_bits = frame[2] & 0x60

if mode_bits == 0x20:
    pressure_level = 1
elif mode_bits == 0x40:
    pressure_level = 2
elif mode_bits == 0x60:
    pressure_level = 3
else:
    pressure_level = None
```

Für die bisher bekannten Werte ist auch folgende kompakte Dekodierung
möglich:

```python
pressure_level = (frame[2] & 0x60) >> 5
```

Die kontrollierten Tests ergaben:

```text
Stufe 1:
0x21 gestoppt
0x31 läuft

Stufe 2:
0x41 gestoppt
0x51 läuft

Stufe 3:
0x61 gestoppt
0x71 läuft
```

Status:

**Bestätigt.**

---

## Weitere Status-Bits

Bei allen sechs kontrollierten Testzuständen war zusätzlich Bit
`0x01` gesetzt.

Seine Bedeutung ist derzeit noch unbekannt.

In früheren Messungen wurden außerdem Statuswerte wie

```text
0x25
0x45
0x65
```

beobachtet.

Gegenüber den heute kontrolliert beobachteten Werten

```text
0x21
0x41
0x61
```

ist dort zusätzlich Bit `0x04` gesetzt.

Die Bedeutung von Bit `0x04` ist noch nicht geklärt und darf nicht
mit der Konstantdruckstufe verwechselt werden.

Damit ist derzeit folgende Bitbelegung bekannt:

```text
0x60 → Konstantdruckstufe
0x10 → Pumpe läuft
0x04 → unbekannt
0x01 → unbekannt
```

Die vollständige Bedeutung des Status-Bytes ist damit noch nicht
geklärt.

---

# Prüfsumme

Byte 149 ist bei allen bisher untersuchten normalen 150-Byte-Frames
eine additive 8-Bit-Prüfsumme.

Berechnung:

```python
calculated_checksum = sum(frame[:149]) & 0xFF
```

Vergleich:

```python
checksum_ok = calculated_checksum == frame[149]
```

Diese Berechnung wurde über zahlreiche unterschiedliche Frames
erfolgreich bestätigt.

Status:

**Bestätigt.**

---

# Verhalten bei ausgeschalteter Anlage

Bei einem Test wurde die Anlage über die offizielle App ausgeschaltet.

Danach verschwanden die normalen `AA 93`-Telemetrieframes.

Einmal wurde ein kurzer Wert beobachtet:

```text
00 00 00 00 00 00 00 00 00 30
```

Bei anschließendem manuellen Read von FF01 wurden keine Nutzdaten
zurückgegeben.

Der kurze Wert wird ausdrücklich **nicht** als bestätigter
AUS-Frame interpretiert.

Gesichert ist derzeit lediglich:

> Bei ausgeschalteter Anlage war während dieses Tests die normale
> 150-Byte-FF01-Telemetrie nicht mehr verfügbar.

---

# Empfohlener Ablauf für einen Client

Für einen rein lesenden Client ist derzeit folgender Ablauf ausreichend:

```text
1. Nach BLE-Gerätename ISP_42_539c suchen
2. Verbindung herstellen
3. FF01 Notifications abonnieren
4. Auf 150-Byte-Frames warten
5. Header AA 93 prüfen
6. Prüfsumme kontrollieren
7. bekannte Felder dekodieren
```

Ein Schreibzugriff auf FF02 ist für die Telemetrie nicht erforderlich.

---

# Beispiel – Prüfen und Dekodieren

```python
def decode_frame(frame):
    if len(frame) != 150:
        return None

    if frame[0] != 0xAA or frame[1] != 0x93:
        return None

    checksum = sum(frame[:149]) & 0xFF

    if checksum != frame[149]:
        return None

    status = frame[2]

    mode_bits = status & 0x60

    pressure_level = {
        0x20: 1,
        0x40: 2,
        0x60: 3,
    }.get(mode_bits)

    return {
        "pressure_level": pressure_level,
        "pump_running": bool(status & 0x10),
        "voltage_v": frame[6] / 10.0,
        "current_raw": frame[8],
        "pressure_raw": int.from_bytes(
            frame[10:12],
            byteorder="little",
            signed=False
        ),
        "water_temperature_c": frame[12] / 10.0,
        "flow_raw": frame[14],
        "daily_water_l": frame[16],
        "total_water_l": frame[18],
    }
```

Strom, Druck und Durchfluss werden im Beispiel bewusst noch als
Rohwerte ausgegeben, solange ihre Skalierung nicht endgültig
bestätigt ist.

---

# Aktueller Stand

## Bestätigt

- Custom Service FF00
- FF01 liefert Telemetrie per Notify
- FF01-Telemetrieframe hat 150 Byte
- Header `AA 93`
- Versorgungsspannung
- Wassertemperatur
- additive 8-Bit-Prüfsumme
- Telemetrie funktioniert ohne FF02-Schreibzugriff
- Offset 16 = Tagesmenge für die bisher beobachteten Werte
- Offset 18 = Gesamtmenge für die bisher beobachteten Werte
- Reset über die Hersteller-App setzt beide Verbrauchszähler zurück
- Status-Bit `0x10` = Pumpe läuft
- Status-Maske `0x60` = Konstantdruckstufe
- `0x20` = Konstantdruck Stufe 1
- `0x40` = Konstantdruck Stufe 2
- `0x60` = Konstantdruck Stufe 3
- alle sechs Kombinationen aus Stufe 1–3 und Pumpe gestoppt/läuft wurden kontrolliert beobachtet

## Sehr wahrscheinlich

- Offset 8 = Stromaufnahme
- Offset 10–11 = Wasserdruck
- Offset 14 = Echtzeit-Durchfluss

## Noch offen

- endgültige Skalierung der Stromaufnahme
- endgültige Skalierung des Wasserdrucks
- endgültige Skalierung des Echtzeit-Durchflusses
- Format der Gesamtmenge oberhalb von 255 L
- vollständige Bitbelegung des Status-Bytes
- Bedeutung von Status-Bit `0x01`
- Bedeutung von Status-Bit `0x04`
- Fehlerstatus / Fehlercodes
- Bedeutung der übrigen FF01-Felder
- Bedeutung der beobachteten Felder um Offset 111 und 119
- Aufbau der FF02-Kommandos
- EIN/AUS-Befehl
- Auswahl Stufe 1/2/3
- Reset-Befehl

---

# Sicherheitsregel für weitere Tests

Bis das FF02-Befehlsformat verstanden ist:

**Keine geratenen oder experimentell konstruierten Schreibbefehle
an FF02 senden.**

Die weitere Analyse bleibt zunächst auf lesende BLE-Kommunikation
und kontrollierte Messungen beschränkt.