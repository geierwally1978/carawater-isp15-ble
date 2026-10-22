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
| 8 | 1 | Stromaufnahme | vermutlich RAW / 10 A | sehr wahrscheinlich |
| 10–11 | 2 | Wasserdruck | Little Endian, Skalierung noch vorläufig | sehr wahrscheinlich |
| 12 | 1 | Wassertemperatur | RAW / 10 °C | bestätigt |
| 14 | 1 | Echtzeit-Durchfluss | vermutlich RAW / 10 L/min | sehr wahrscheinlich |
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

Kontrollierter Betriebspunkt:
RAW 21–22 → App 2,00 A

Frühere Messung:
RAW 23–24 → App ungefähr 2,30 A
```

Aktuelle Arbeitshypothese:

```python
current_A = frame[8] / 10.0
```

Die Zuordnung von Offset 8 zur Stromaufnahme ist sehr wahrscheinlich.

Die exakte Skalierung `/ 10` benötigt noch weitere kontrollierte
Messpunkte, bevor sie als bestätigt betrachtet wird.

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

Hochwertige Referenzpunkte:

```text
RAW ≈ 386      → App 2,67 bar
RAW ≈ 184–185  → App 1,21 bar
```

Daraus ergibt sich derzeit als Arbeitshypothese:

```text
Druck [bar] ≈ RAW × 0,00723 - 0,12
```

Diese Formel ist **noch nicht bestätigt**.

Weitere kontrollierte Referenzpunkte sind erforderlich.

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

Kontrollierter Betriebspunkt:
RAW 19 → App 2,0 L/min

Frühere Messung:
RAW 16–17 → App ungefähr 1,8 L/min
```

Aktuelle Arbeitshypothese:

```python
flow_lpm = frame[14] / 10.0
```

Die Zuordnung von Offset 14 zum Echtzeit-Durchfluss ist sehr
wahrscheinlich.

Die Skalierung `/ 10` wird vorerst noch als Arbeitshypothese behandelt.

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

Die genaue Bedeutung dieser Felder ist derzeit noch unbekannt.

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

Dieses Byte enthält mehrere Status- und Modusinformationen.

Beobachtete Werte sind unter anderem:

```text
0x20
0x21
0x25
0x31
0x45
0x65
```

Es handelt sich daher nicht um einen einfachen numerischen Statuswert,
sondern sehr wahrscheinlich um ein Bitfeld beziehungsweise eine
Kombination mehrerer Zustände.

---

## Pumpenstatus

Bei wiederholten kontrollierten Tests wurde beobachtet:

```text
0x21 = Pumpe gestoppt
0x31 = Pumpe läuft
```

Der Unterschied beträgt:

```text
0x10
```

Aktuelle Interpretation:

```python
pump_running = bool(frame[2] & 0x10)
```

Damit kennzeichnet Bit `0x10` sehr wahrscheinlich den laufenden
Pumpenbetrieb.

Status:

**Stark bestätigt durch wiederholte Messungen.**

---

## Konstantdruckstufe

Bei gestoppter Pumpe wurden kontrolliert folgende Werte beobachtet:

```text
Stufe 1 → 0x25
Stufe 2 → 0x45
Stufe 3 → 0x65
```

Die Differenz zwischen den Druckstufen beträgt jeweils:

```text
0x20
```

Damit ist klar, dass Informationen zur gewählten Konstantdruckstufe
im Status-Byte enthalten sind.

Allerdings wurde bei aktivierter Stufe 1 ebenfalls `0x20` beziehungsweise
`0x21` beobachtet.

Die Druckstufe kann deshalb derzeit noch nicht zuverlässig allein durch
eine einfache Zuordnung des vollständigen Status-Bytes bestimmt werden.

Die genaue Bitbelegung muss weiter untersucht werden.

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

    return {
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

Strom, Druck und Durchfluss werden im Beispiel bewusst teilweise noch
als Rohwerte ausgegeben, solange ihre Skalierung nicht endgültig
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

## Sehr wahrscheinlich

- Offset 8 = Stromaufnahme
- Offset 10–11 = Wasserdruck
- Offset 14 = Echtzeit-Durchfluss
- Status-Bit `0x10` = Pumpe läuft

## Noch offen

- endgültige Skalierung der Stromaufnahme
- endgültige Skalierung des Wasserdrucks
- endgültige Skalierung des Echtzeit-Durchflusses
- Format der Gesamtmenge oberhalb von 255 L
- vollständige Bitbelegung des Status-Bytes
- genaue Kodierung der Konstantdruckstufen
- Fehlerstatus / Fehlercodes
- Bedeutung der übrigen FF01-Felder
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
