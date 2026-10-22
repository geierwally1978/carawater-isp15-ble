# ISP15 BLE – Tests zur Skalierung vom 22.10.2026

Kontrollierte Messungen zur Zuordnung der in der offiziellen Carawater-App
angezeigten Werte zu den Rohwerten der BLE-Charakteristik FF01.

## Testaufbau

- Gerät: Carawater ISP15
- BLE-Gerätename: `ISP_42_539c`
- Konstantdruckstufe: Stufe 1
- Telemetrie-Charakteristik: FF01
- Länge eines FF01-Frames: 150 Byte
- Die offizielle Carawater-App und Python/Bleak können nicht gleichzeitig
  mit dem ISP15 verbunden sein.
- Die App-Werte und BLE-Werte mussten deshalb nacheinander erfasst werden.
- Beim letzten kontrollierten Test wurde die Stellung des Wasserhahns
  zwischen App- und BLE-Messung nicht verändert.

---

## Test 1 – Anlage im Stillstand

### BLE-Messung

Zeit: ca. 09:51 Uhr

Wasserhahn geschlossen, Pumpe gestoppt.

Gemessene Werte:

- Spannung: 13,1 V
- Wassertemperatur: 15,0 °C
- Tagesmenge: 15 L
- Gesamtmenge: 83 L
- Status-Byte: `0x21`
- Strom RAW: `0`
- Druck RAW: `385–388`
- Durchfluss RAW: `0`

Beispiel-Frame:

```text
AA9321140000830000008201960000000F00530000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001400460028000000000000000000000000000000000000000000000000000000000096003200000014000A00360104010000000000000000000000000000000014
```

### Referenz aus der Carawater-App

Kurz danach wurde bei weiterhin geschlossenem Wasserhahn in der App gemessen:

- Wasserdruck: **2,67 bar**

Damit ergibt sich als sehr guter Referenzpunkt:

```text
Druck RAW ≈ 386
App-Druck = 2,67 bar
```

---

## Test 2 – Wasserhahn ungefähr halb geöffnet

Referenz aus der Carawater-App:

- Spannung: 12,8 V
- Strom: 2,30 A
- Wassertemperatur: 15,0 °C
- Wasserdruck: 1,46 bar
- Echtzeit-Durchfluss: 1,8 L/min
- Tagesmenge: 11 L
- Gesamtmenge: 79 L
- Status: Läuft
- Konstantdruck: Stufe 1

Beim späteren BLE-Test mit ungefähr halb geöffnetem Wasserhahn wurden
im stabilen Bereich ungefähr folgende Werte gemessen:

- Strom RAW: `23–24`
- Druck RAW: `227–244`
- Durchfluss RAW: `16–17`
- Status-Byte: `0x31`

Da die Stellung des Wasserhahns zwischen App- und BLE-Messung nicht
mechanisch fixiert war, sind diese Werte nur als ungefähre Referenz
zu betrachten.

---

## Test 3 – Wasserhahn vollständig geöffnet

Referenz aus der Carawater-App:

- Spannung: 12,7 V
- Strom: 2,50 A
- Wassertemperatur: 15,0 °C
- Wasserdruck: 1,20 bar
- Echtzeit-Durchfluss: 3,9 L/min
- Tagesmenge: 12 L
- Gesamtmenge: 80 L
- Status: Läuft
- Konstantdruck: Stufe 1

Beim späteren BLE-Test wurden im stabilen Bereich ungefähr folgende
Werte gemessen:

- Strom RAW: `28–30`
- Druck RAW: `177–183`
- Durchfluss RAW: `46–51`
- Status-Byte: `0x31`

Auch hier war die Stellung des Wasserhahns zwischen App- und
BLE-Messung nicht exakt reproduzierbar.

Der Test eignet sich deshalb gut zur Identifikation der Felder,
aber nur eingeschränkt zur Bestimmung der exakten Skalierung.

---

## Test 4 – Kontrollierter Betriebspunkt bei 2,0 L/min

Dies ist bisher der beste direkte Vergleich zwischen App und BLE.

Der Wasserhahn wurde zunächst mit der offiziellen Carawater-App
eingestellt. Anschließend wurde die App getrennt, ohne die Stellung
des Wasserhahns zu verändern.

Direkt danach wurde der Python/Bleak-Reader verbunden.

### Werte der Carawater-App

Zeit: ca. 14:22 Uhr

- Status: Läuft
- Konstantdruck: Stufe 1
- Spannung: **12,9 V**
- Strom: **2,00 A**
- Wassertemperatur: **21,0 °C**
- Wasserdruck: **1,21 bar**
- Echtzeit-Durchfluss: **2,0 L/min**
- Tagesmenge: **16 L**
- Gesamtmenge: **84 L**

### BLE-Werte

Nach kurzer Stabilisierung:

```text
Spannung:           12,9 V
Wassertemperatur:   21,0 °C
Tagesmenge:         16–17 L
Gesamtmenge:        84 L

Strom RAW:          21–22
Druck RAW:          184–185
Durchfluss RAW:     19

Status-Byte:        0x31
Pumpenstatus:       läuft
```

Repräsentativer stabiler Frame:

```text
AA933114000081001500B800D200130011005400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000014004600280000000000000000000A00000000000000000000000000000000000000AA003200000014000A003601040100000000000000000000000000000000DC
```

Damit ergeben sich unsere derzeit besten direkten Zuordnungen:

```text
Strom RAW 21–22      → 2,00 A
Druck RAW 184–185    → 1,21 bar
Durchfluss RAW 19    → 2,0 L/min
```

---

## Aktuelle Zuordnung der FF01-Felder

Der vordere Bereich des FF01-Telemetrieframes lässt sich inzwischen
folgendermaßen interpretieren:

| Offset | Bedeutung | Stand |
|---|---|---|
| 0 | Header `0xAA` | bestätigt |
| 1 | Header `0x93` | bestätigt |
| 2 | Status- und Modus-Flags | teilweise dekodiert |
| 6 | Versorgungsspannung × 10 | bestätigt |
| 8 | Strom RAW | sehr wahrscheinlich |
| 10–11 | Druck RAW, Little Endian | sehr wahrscheinlich |
| 12 | Wassertemperatur × 10 | bestätigt |
| 14 | Echtzeit-Durchfluss RAW | sehr wahrscheinlich |
| 16 | Tagesmenge in Litern | sehr wahrscheinlich |
| 18 | Gesamtmenge in Litern | sehr wahrscheinlich |
| 149 | additive 8-Bit-Prüfsumme | bestätigt |

Die Prüfsumme wird berechnet mit:

```python
checksum = sum(frame[:149]) & 0xFF
```

---

## Pumpenstatus

Wiederholte kontrollierte Messungen zeigen:

```text
0x21 = Pumpe gestoppt
0x31 = Pumpe läuft
```

Der Unterschied ist Bit `0x10`.

Aktuelle Interpretation:

```python
pump_running = bool(status_byte & 0x10)
```

Damit ist sehr wahrscheinlich:

**Bit `0x10` im Status-Byte kennzeichnet den laufenden Pumpenbetrieb.**

---

## Vorläufige Skalierung – Strom

Der Rohwert befindet sich an Offset 8.

Bisher beobachtet:

```text
RAW 0      → 0,00 A
RAW 21–22  → 2,00 A
RAW 23–24  → ungefähr 2,30 A
```

Eine Skalierung in der Größenordnung von:

```text
Strom [A] ≈ RAW / 10
```

ist plausibel.

Sie wird vorerst noch nicht als endgültig bestätigt betrachtet.

---

## Vorläufige Skalierung – Echtzeit-Durchfluss

Der Rohwert befindet sich an Offset 14.

Der beste kontrollierte Referenzpunkt ist:

```text
RAW 19 → 2,0 L/min
```

Beim früheren Test mit ungefähr halb geöffnetem Wasserhahn wurde beobachtet:

```text
RAW 16–17 → App 1,8 L/min
```

Damit ist eine Skalierung in der Größenordnung von:

```text
Durchfluss [L/min] ≈ RAW / 10
```

plausibel.

Der frühere Test mit vollständig geöffnetem Wasserhahn passt nicht sauber
zu dieser einfachen Skalierung. Da die Wasserhahnstellung zwischen
App- und BLE-Messung damals nicht exakt beibehalten wurde, wird dieser
Messpunkt nicht zur Bestimmung der Skalierung verwendet.

Weitere kontrollierte Messpunkte sind erforderlich.

---

## Vorläufige Skalierung – Wasserdruck

Der Druck wird als 16-Bit-Wert in Little-Endian-Reihenfolge an
Offset 10–11 übertragen.

Zwei besonders gute Referenzpunkte sind:

```text
RAW ≈ 386      → 2,67 bar
RAW ≈ 184–185  → 1,21 bar
```

Aus diesen beiden Punkten ergibt sich derzeit näherungsweise:

```text
Druck [bar] ≈ RAW × 0,00723 - 0,12
```

Diese Formel ist zunächst nur eine Arbeitshypothese.

Für eine belastbare Bestätigung sind weitere kontrollierte
Referenzpunkte erforderlich.

---

## Test 5 – Reset der Verbrauchszähler

Die offizielle Carawater-App bietet eine Reset-Funktion für die
Verbrauchszähler.

Vor dem Reset wurden über FF01 folgende Werte empfangen:

```text
Tagesmenge:   17 L
Gesamtmenge:  84 L
```

Die entsprechenden Felder waren:

```text
Offset 16 = 17
Offset 18 = 84
```

Der Reset wurde anschließend über die offizielle Carawater-App
ausgeführt.

Dabei wurden **Tagesmenge und Gesamtmenge gemeinsam zurückgesetzt**.

Nach dem Reset zeigte der FF01-Reader:

```text
Tagesmenge:   0 L
Gesamtmenge:  0 L
```

Entsprechend wurden im Frame beobachtet:

```text
Offset 16 = 0
Offset 18 = 0
```

Damit wird die bisherige Zuordnung weiter bestätigt:

```text
Offset 16 = Tagesmenge
Offset 18 = Gesamtmenge
```

### Weitere Veränderungen im Frame

Der Reset veränderte nicht nur Offset 16 und 18.

Vor dem Reset enthielt der hintere Bereich des 150-Byte-Frames
mehrere weitere Werte.

Nach dem Reset waren große Teile dieses Bereichs auf `0x00` gesetzt.

Dies ist ein deutlicher Hinweis darauf, dass im bislang nicht
dekodierten hinteren Bereich des FF01-Frames weitere Verbrauchs-,
Statistik- oder Zählerdaten gespeichert werden.

Die genaue Bedeutung dieser Felder ist noch unbekannt.

### RAW-Capture

Die Messung unmittelbar nach dem Reset wurde als CSV gespeichert:

```text
captures/raw/2026-10-22-after-counter-reset.csv
```

Der Capture enthält vollständige 150-Byte-Frames inklusive Zeitstempel,
dekodierten bekannten Feldern und geprüfter Checksumme.

Beispiel unmittelbar nach dem Reset:

```text
Status:             0x21
Pumpenstatus:       gestoppt
Spannung:           13,6–13,7 V
Wassertemperatur:   18,0 °C
Strom RAW:          0
Druck RAW:          377–379
Durchfluss RAW:     0
Tagesmenge:         0 L
Gesamtmenge:        0 L
Checksumme:         gültig
```

### Bewertung

Die Zuordnung von Offset 16 und Offset 18 ist durch den gezielten
Reset nun deutlich besser abgesichert.

Noch ungeklärt bleibt insbesondere:

- welche weiteren Felder durch den Reset gelöscht werden
- welche Statistikwerte dort gespeichert sind
- ob Tages- und Gesamtmenge intern noch mit höherer Auflösung geführt werden
- wie Gesamtmengen oberhalb von 255 Litern dargestellt werden
- welcher BLE-Befehl von der offiziellen App für den Reset verwendet wird

## Zwischenstand

FF01 enthält inzwischen sehr wahrscheinlich alle wichtigen
Live-Telemetriedaten für eine spätere lokale Integration:

- Pumpenstatus
- Versorgungsspannung
- Stromaufnahme
- Wassertemperatur
- Wasserdruck
- Echtzeit-Durchfluss
- Tagesmenge
- Gesamtmenge

Für den Empfang dieser Daten sind keine Schreibzugriffe auf FF02
erforderlich.

Die Untersuchung der Steuerbefehle über FF02 erfolgt getrennt von
der zunächst rein lesenden Telemetrieanalyse.

Bis das Befehlsformat verstanden ist, werden keine geratenen
Schreibbefehle an FF02 gesendet.
