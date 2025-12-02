import asyncio
import sqlite3
from bleak import BleakClient, BleakScanner
from datetime import datetime

WATCH_NAME = "Amazfit"
HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

DB_NAME = "heart.db"

# -----------------------------------------------------------
# Create table
# -----------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS heart_rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_real REAL,
            ts_iso TEXT,
            bpm INTEGER
        )
    """)
    conn.commit()
    conn.close()


# -----------------------------------------------------------
# Correct HR Parser (handles Amazfit packets)
# -----------------------------------------------------------
def parse_hr(data: bytearray):
    if not data:
        return None

    flags = data[0]
    hr_format = flags & 0x01  # Bit 0 → HR format

    if hr_format == 0:  
        # 8-bit HR → BPM = next byte
        return data[1]
    else:
        # 16-bit HR
        return int.from_bytes(data[1:3], byteorder="little")


# -----------------------------------------------------------
# Save HR to DB
# -----------------------------------------------------------
def save_hr_to_db(bpm):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    ts_real = datetime.now().timestamp()
    ts_iso = datetime.now().isoformat(timespec='seconds')

    cur.execute("INSERT INTO heart_rate (ts_real, ts_iso, bpm) VALUES (?, ?, ?)",
                (ts_real, ts_iso, bpm))
    conn.commit()
    conn.close()


# -----------------------------------------------------------
# Notification handler
# -----------------------------------------------------------
def hr_handler(sender, data):
    bpm = parse_hr(data)
    if bpm is not None:
        print(f"❤️ HR: {bpm} BPM  |  Saved to DB")
        save_hr_to_db(bpm)
    else:
        print("⚠ Received data, but No BPM field:", data)


# -----------------------------------------------------------
# Main Loop
# -----------------------------------------------------------
async def main():
    print("🔍 Scanning for Watch...")

    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and "amazfit" in d.name.lower()
    )

    if not device:
        print("❌ Watch not found. Turn Bluetooth ON & open HR screen.")
        return

    print(f"✔ Found: {device.name} ({device.address})")
    print("🔗 Connecting...")

    async with BleakClient(device) as client:
        if not client.is_connected:
            print("❌ Failed to connect.")
            return

        print("✅ Connected!")
        print("📡 Subscribing to Heart Rate notifications...")

        await client.start_notify(HR_UUID, hr_handler)

        print("🔥 Receiving HR... Open Heart Rate screen on watch.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await client.stop_notify(HR_UUID)
            print("\n🛑 Stopped.")


# -----------------------------------------------------------
# Run
# -----------------------------------------------------------
if __name__ == "__main__":
    init_db()
    asyncio.run(main())
