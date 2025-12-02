import asyncio
from bleak import BleakClient

DEVICE_ADDRESS = "DB:F5:D9:2C:1C:BE"
HR_MEASUREMENT = "00002a37-0000-1000-8000-00805f9b34fb"

def hr_handler(sender, data):
    """Parse BLE Heart Rate packet."""
    flags = data[0]
    hr_value = data[1]  # Works for 8-bit HR format
    print(f"❤️ Heart Rate: {hr_value} BPM")

async def main():
    print(f"🔗 Connecting to {DEVICE_ADDRESS} ...")
    async with BleakClient(DEVICE_ADDRESS) as client:
        print("✅ Connected!")

        print("📶 Subscribing to HR notifications...")
        await client.start_notify(HR_MEASUREMENT, hr_handler)

        print("🕒 Reading HR for 60 seconds... Keep T-Rex HR screen open.")
        await asyncio.sleep(60)

        print("🛑 Done reading Heart rate...")
        if client.is_connected:
            await client.stop_notify(HR_MEASUREMENT)

        print("✔️ Done.")

asyncio.run(main())
