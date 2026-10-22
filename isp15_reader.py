import asyncio
from datetime import datetime

from bleak import BleakClient, BleakScanner

DEVICE_NAME = "ISP_42_539c"
FF01 = "0000ff01-0000-1000-8000-00805f9b34fb"

previous_frame = None


def show_changes(data):
    global previous_frame

    if previous_frame is None:
        print("Änderungen:         erster Frame")
        previous_frame = bytes(data)
        return

    changes = []

    for offset, (old, new) in enumerate(zip(previous_frame, data)):
        if old != new:
            changes.append(
                f"Offset {offset}: 0x{old:02X} ({old}) -> 0x{new:02X} ({new})"
            )

    if changes:
        print("Änderungen:")
        for change in changes:
            print(f"  {change}")
    else:
        print("Änderungen:         keine")

    previous_frame = bytes(data)


def decode_frame(data):
    if len(data) != 150:
        print(f"Unbekannte Frame-Länge: {len(data)} Bytes")
        print(data.hex().upper())
        return

    if data[0] != 0xAA or data[1] != 0x93:
        print("Unbekannter Frame:")
        print(data.hex().upper())
        return

    # Bereits bekannte Werte
    status = data[2]
    voltage = data[6] / 10.0
    water_temperature = data[12] / 10.0
    daily_water = data[16]
    total_water = data[18]

    # Kandidaten aus unseren Messungen
    current_raw = data[8]

    pressure_raw = int.from_bytes(
        data[10:12],
        byteorder="little",
        signed=False
    )

    flow_raw = data[14]

    # Prüfsumme
    received_checksum = data[149]
    calculated_checksum = sum(data[:149]) & 0xFF
    checksum_ok = received_checksum == calculated_checksum

    now = datetime.now().strftime("%H:%M:%S")

    print()
    print(f"Carawater ISP15   {now}")
    print("-" * 46)
    print(f"Spannung:          {voltage:.1f} V")
    print(f"Wassertemperatur:  {water_temperature:.1f} °C")
    print(f"Tagesmenge:        {daily_water} L")
    print(f"Gesamtmenge:       {total_water} L")
    print()

    print("Rohwerte:")
    print(f"  Strom RAW:       {current_raw}")
    print(f"  Druck RAW:       {pressure_raw}")
    print(f"  Durchfluss RAW:  {flow_raw}")
    print()

    print(f"Status-Byte:       0x{status:02X}")

    if status & 0x10:
        print("Pumpenstatus:      läuft")
    else:
        print("Pumpenstatus:      gestoppt")

    if checksum_ok:
        print(f"Prüfsumme:         0x{received_checksum:02X} ✓")
    else:
        print(
            f"Prüfsumme:         0x{received_checksum:02X} ✗ "
            f"(erwartet 0x{calculated_checksum:02X})"
        )

    print()

    show_changes(data)

    print()
    print(f"RAW: {data.hex().upper()}")


def notification_handler(sender, data):
    decode_frame(data)


async def main():
    print(f"Suche nach {DEVICE_NAME} ...")

    device = await BleakScanner.find_device_by_name(
        DEVICE_NAME,
        timeout=10.0
    )

    if device is None:
        print("ISP15 nicht gefunden.")
        return

    print(f"Gefunden: {device.name}")
    print("Verbinde ...")

    async with BleakClient(device) as client:
        print("Verbunden.")
        print("Abonniere FF01 ...")
        print("Beenden mit Ctrl+C.")
        print()

        await client.start_notify(FF01, notification_handler)

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        print("ISP15 Reader beendet.")