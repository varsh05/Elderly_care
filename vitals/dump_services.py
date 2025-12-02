import asyncio
from bleak import BleakScanner, BleakClient

WATCH_NAME = "Amazfit T-Rex"


async def main():

    print("\n🔍 Scanning for devices...")
    devices = await BleakScanner.discover()

    target = None
    for d in devices:
        name = d.name or "Unknown"
        print(f"📡 Found: {name} — {d.address}")

        if WATCH_NAME.lower() in name.lower():
            target = d

    if not target:
        print(f"\n❌ {WATCH_NAME} not found.")
        return

    print(f"\n✅ Found watch: {target.name} — {target.address}")
    print("🔗 Connecting...")

    async with BleakClient(target.address) as client:
        print("✅ Connected.")
        print("📜 Loading services...\n")

        # Access services (Bleak loads them automatically on connect)
        services = client.services

        print(f"📦 Total services found: {len(services.services)}\n")

        # Print all services
        for service in services:
            print(f"🔧 SERVICE: {service.uuid}")
            print(f"    ↳ Handle: {service.handle}")

            # Print characteristics inside each service
            for char in service.characteristics:
                props = ",".join(char.properties)
                print(f"      • CHAR: {char.uuid}  [{props}]")

                # Print descriptors (if any)
                for desc in char.descriptors:
                    print(f"          ↳ DESC: {desc.uuid}  (Handle: {desc.handle})")

            print()  # spacing


if __name__ == "__main__":
    asyncio.run(main())
