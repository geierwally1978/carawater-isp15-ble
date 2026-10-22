# Carawater ISP15 BLE

Reverse Engineering und Dokumentation des Bluetooth-Low-Energy-Protokolls
der **Carawater ISP15 Druckwasserpumpe**.

Ziel des Projekts ist es, die ISP15 unabhängig von der Hersteller-App lokal
auslesen und später steuern zu können.

Ein langfristiges Ziel ist eine lokale Integration in **Home Assistant**.

> **Projektstatus:** Reverse Engineering läuft.  
> Die Telemetrie über FF01 ist bereits in großen Teilen verstanden.
> Das Steuerprotokoll über FF02 ist noch nicht dekodiert.

---

## Ziele

Das Projekt soll unter anderem folgende Funktionen ermöglichen:

- lokale BLE-Kommunikation mit der ISP15
- Auslesen der Live-Telemetrie
- Dekodierung der Messwerte
- Erkennen des Pumpenstatus
- Auslesen der gewählten Konstantdruckstufe
- lokale Steuerung ohne Hersteller-App
- spätere Integration in Home Assistant

Die Analyse erfolgt schrittweise anhand kontrollierter Messungen und
aufgezeichneter BLE-Frames.

---

## Aktueller Stand

### Telemetrie

Die ISP15 stellt über die BLE-Charakteristik **FF01** regelmäßig
Telemetriedaten bereit.

Normale Frames:

```text
Header: AA 93
Länge:  150 Byte
```

FF01 muss lediglich per **Notify** abonniert werden.

Ein vorheriger Schreibzugriff auf FF02 ist für den Empfang der
Telemetrie nicht erforderlich.

### Bereits identifizierte Werte

| Wert | Stand |
|---|---|
| Versorgungsspannung | ✅ bestätigt |
| Wassertemperatur | ✅ bestätigt |
| Prüfsumme | ✅ bestätigt |
| Pumpenstatus | 🟢 stark bestätigt |
| Stromaufnahme | 🟡 Feld identifiziert, Skalierung noch in Prüfung |
| Wasserdruck | 🟡 Feld identifiziert, Skalierung noch in Prüfung |
| Echtzeit-Durchfluss | 🟡 Feld identifiziert, Skalierung noch in Prüfung |
| Tagesmenge | 🟢 sehr wahrscheinlich |
| Gesamtmenge | 🟢 sehr wahrscheinlich |
| Konstantdruckstufe | 🟡 teilweise dekodiert |
| Fehlerstatus | 🔴 noch offen |
| Steuerbefehle FF02 | 🔴 noch offen |

Details befinden sich in:

```text
docs/protocol.md
```

---

## BLE-Schnittstelle

Beobachteter Gerätename:

```text
ISP_42_539c
```

### Custom Service

```text
0000FF00-0000-1000-8000-00805F9B34FB
```

### FF01 – Telemetrie

```text
0000FF01-0000-1000-8000-00805F9B34FB
```

Eigenschaften:

```text
Read
Notify
```

### FF02 – Steuerung

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

Das genaue Befehlsformat ist derzeit noch unbekannt.

---

## Aktuell bekannte FF01-Felder

| Offset | Bedeutung | Aktueller Stand |
|---:|---|---|
| 0 | Header `0xAA` | bestätigt |
| 1 | Header `0x93` | bestätigt |
| 2 | Status / Modus | teilweise dekodiert |
| 6 | Versorgungsspannung | bestätigt |
| 8 | Stromaufnahme | sehr wahrscheinlich |
| 10–11 | Wasserdruck | sehr wahrscheinlich |
| 12 | Wassertemperatur | bestätigt |
| 14 | Echtzeit-Durchfluss | sehr wahrscheinlich |
| 16 | Tagesmenge | sehr wahrscheinlich |
| 18 | Gesamtmenge | sehr wahrscheinlich |
| 149 | Prüfsumme | bestätigt |

Beispielsweise werden Spannung und Temperatur direkt mit Faktor 10
übertragen:

```text
RAW 131 → 13,1 V
RAW 210 → 21,0 °C
```

Die Prüfsumme ist eine additive 8-Bit-Prüfsumme:

```python
checksum = sum(frame[:149]) & 0xFF
```

---

## Pumpenstatus

Bei kontrollierten Tests wurden unter anderem folgende Statuswerte
beobachtet:

```text
0x21 = Pumpe gestoppt
0x31 = Pumpe läuft
```

Daraus ergibt sich:

```python
pump_running = bool(status_byte & 0x10)
```

Bit `0x10` kennzeichnet damit sehr wahrscheinlich den laufenden
Pumpenbetrieb.

---

## Erste Skalierungsergebnisse

Bei kontrollierten Messungen konnten unter anderem folgende
App-/BLE-Zuordnungen ermittelt werden.

### Strom

```text
RAW 0      → 0,00 A
RAW 21–22  → 2,00 A
RAW 23–24  → ungefähr 2,30 A
```

Aktuelle Arbeitshypothese:

```text
Strom [A] ≈ RAW / 10
```

### Echtzeit-Durchfluss

```text
RAW 0      → 0,0 L/min
RAW 19     → 2,0 L/min
RAW 16–17  → ungefähr 1,8 L/min
```

Aktuelle Arbeitshypothese:

```text
Durchfluss [L/min] ≈ RAW / 10
```

### Wasserdruck

Zwei besonders gute Referenzpunkte:

```text
RAW ≈ 386      → 2,67 bar
RAW ≈ 184–185  → 1,21 bar
```

Aktuelle Arbeitshypothese:

```text
Druck [bar] ≈ RAW × 0,00723 - 0,12
```

Diese Skalierungen sind noch nicht endgültig bestätigt.

---

## Repository-Struktur

```text
carawater-isp15-ble/
├── README.md
├── captures/
│   ├── README.md
│   ├── 2026-10-19-pressure-levels.md
│   ├── 2026-10-21-controlled-tests.md
│   └── 2026-10-22-scaling-tests.md
└── docs/
    └── protocol.md
```

### `docs/protocol.md`

Enthält den aktuellen technischen Stand des dekodierten BLE-Protokolls.

### `captures/`

Enthält die Rohdaten und kontrollierten Messreihen, auf denen die
Protokollanalyse basiert.

Die Trennung ist bewusst gewählt:

**Captures = Messdaten und Belege**  
**Protocol = daraus abgeleitete technische Erkenntnisse**

---

## Testumgebung

Für die bisherigen Tests wurden unter anderem verwendet:

- offizielle Carawater-App
- BLE Scanner auf iOS
- Python
- Bleak
- macOS
- Linux

Die aktuelle Python-Testumgebung:

```text
Python 3.13
Bleak 3.0.2
```

Unter macOS wurde bestätigt, dass FF01 nach dem Abonnieren von
Notifications selbstständig ungefähr alle zwei Sekunden einen
150-Byte-Telemetrieframe liefert.

---

## Apple CoreBluetooth

Unter macOS und iOS wird für BLE-Geräte keine klassische MAC-Adresse
verwendet, sondern eine CoreBluetooth-UUID.

Diese UUID kann sich zwischen Geräten beziehungsweise Apple-Systemen
unterscheiden.

Eine Anwendung sollte daher nicht auf eine fest eingetragene
CoreBluetooth-UUID angewiesen sein.

Der bisherige Python-Testclient sucht stattdessen nach:

```text
ISP_42_539c
```

---

## Sicherheit

Das Format der Steuerbefehle über FF02 ist derzeit nicht bekannt.

Daher gilt für dieses Projekt momentan:

> **Keine geratenen oder experimentell konstruierten Schreibbefehle an FF02.**

Die Analyse konzentriert sich zunächst auf die lesende Telemetrie.

Steuerbefehle werden erst untersucht, wenn ihr Aufbau anhand belastbarer
Daten nachvollzogen werden kann.

---

## Nächste Schritte

Geplant sind:

1. Skalierung der Stromaufnahme weiter bestätigen
2. Skalierung des Echtzeit-Durchflusses weiter bestätigen
3. Druckskalierung mit zusätzlichen Referenzpunkten prüfen
4. Gesamtmengenzähler oberhalb von 255 Litern untersuchen
5. Status-Byte vollständig dekodieren
6. Konstantdruckstufen vollständig dekodieren
7. Fehlerstatus untersuchen
8. FF02-Kommandostruktur analysieren
9. EIN/AUS, Stufe 1/2/3 und Reset verstehen
10. lokalen ISP15-Client entwickeln
11. Home-Assistant-Integration vorbereiten

---

## Mitarbeit

Weitere Messungen, BLE-Captures oder Informationen zum ISP15-Protokoll
sind willkommen.

Besonders hilfreich wären:

- dokumentierte FF01-Felder
- Skalierungsfaktoren
- Informationen zur Bitbelegung des Status-Bytes
- FF02-Befehlsformat
- Aufzeichnungen der Kommunikation der offiziellen App
- Informationen zu Prüfsummen oder weiteren Frame-Typen

Bitte bei Messdaten möglichst immer die gleichzeitig beziehungsweise
unmittelbar davor oder danach in der offiziellen App angezeigten Werte
mit dokumentieren.

---

## Haftungsausschluss

Dieses Projekt ist ein unabhängiges Reverse-Engineering-Projekt und
steht in keiner Verbindung zum Hersteller der Carawater ISP15.

Alle Informationen basieren auf eigenen Beobachtungen und Messungen.

Die Nutzung der hier veröffentlichten Informationen erfolgt auf
eigene Verantwortung.
