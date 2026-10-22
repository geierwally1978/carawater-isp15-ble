import asyncio
import csv
from datetime import datetime
from pathlib import Path

from bleak import BleakClient, BleakScanner


DEVICE_NAME = "ISP_42_539c"
FF01 = "0000ff01-0000-1000-8000-00805f9b34fb"

CAPTURE_DIR = Path("captures/raw")

previous_frame = None
capture_file = None
capture_writer = None


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


def create_capture_file():
    global capture_file
    global capture_writer

    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

    print()
    capture_name = input(
        "Name der Messung (Enter = ohne Bezeichnung): "
    ).strip()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if capture_name:
        safe_name = capture_name.lower()

        safe_name = safe_name.replace(" ", "-")
        safe_name = safe_name.replace("ä", "ae")
        safe_name = safe_name.replace("ö", "oe")
        safe_name = safe_name.replace("ü", "ue")
        safe_name = safe_name.replace("ß", "ss")

        safe_name = "".join(
            char for char in safe_name
            if char.isalnum() or char in "-_"
        )

        filename = CAPTURE_DIR / f"{timestamp}_{safe_name}.csv"

    else:
        filename = CAPTURE_DIR / f"{timestamp}_capture.csv"

    capture_file = open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    )

    capture_writer = csv.writer(
        capture_file,
        delimiter=";"
    )

    capture_writer.writerow([
        "timestamp",
        "frame_length",
        "status_hex",
        "pump_running",
        "voltage_v",
        "current_raw",
        "pressure_raw",
        "water_temperature_c",
        "flow_raw",
        "daily_water_l",
        "total_water_l",
        "checksum_received",
        "checksum_calculated",
        "checksum_ok",
        "raw_hex",
    ])

    capture_file.flush()

    print(f"Capture-Datei: {filename}")
    print()


def save_frame(
    data,
    status,
    pump_running,
    voltage,
    current_raw,
    pressure_raw,
    water_temperature,
    flow_raw,
    daily_water,
    total_water,
    received_checksum,
    calculated_checksum,
    checksum_ok,
):
    if capture_writer is None:
        return

    capture_writer.writerow([
        datetime.now().isoformat(timespec="milliseconds"),
        len(data),
        f"0x{status:02X}",
        pump_running,
        f"{voltage:.1f}",
        current_raw,
        pressure_raw,
        f"{water_temperature:.1f}",
        flow_raw,
        daily_water,
        total_water,
        f"0x{received_checksum:02X}",
        f"0x{calculated_checksum:02X}",
        checksum_ok,
        data.hex().upper(),
    ])

    capture_file.flush()


def decode_frame(data):
    if len(data) != 150:
        print(f"Unbekannte Frame-Länge: {len(data)} Bytes")
        print(data.hex().upper())
        return

    if data[0] != 0xAA or data[1] != 0x93:
        print("Unbekannter Frame:")
        print(data.hex().upper())
        return

    status = data[2]

    voltage = data[6] / 10.0
    current_raw = data[8]

    pressure_raw = int.from_bytes(
        data[10:12],
        byteorder="little",
        signed=False
    )

    water_temperature = data[12] / 10.0
    flow_raw = data[14]

    daily_water = data[16]
    total_water = data[18]

    pump_running = bool(status & 0x10)

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

    if pump_running:
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

    save_frame(
        data=data,
        status=status,
        pump_running=pump_running,
        voltage=voltage,
        current_raw=current_raw,
        pressure_raw=pressure_raw,
        water_temperature=water_temperature,
        flow_raw=flow_raw,
        daily_water=daily_water,
        total_water=total_water,
        received_checksum=received_checksum,
        calculated_checksum=calculated_checksum,
        checksum_ok=checksum_ok,
    )


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

        create_capture_file()

        print("Abonniere FF01 ...")
        print("Beenden mit Ctrl+C.")
        print()

        await client.start_notify(
            FF01,
            notification_handler
        )

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print()
        print("ISP15 Reader beendet.")

    finally:
        if capture_file is not None:
            capture_file.close()