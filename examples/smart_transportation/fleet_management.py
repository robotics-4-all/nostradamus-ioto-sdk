#!/usr/bin/env python3
"""
Nostradamus IoTO SDK - Fleet Management Example

Demonstrates vehicle fleet telemetry monitoring:
1. Create a collection with schema
2. Generate and send vehicle telemetry data
3. Query data with fleet-specific filters
4. Get statistics
5. Delete specific data
6. Clean up collection
"""

import os
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _load_env import load_dotenv

from nostradamus_ioto_sdk import NostradamusClient
from nostradamus_ioto_sdk.exceptions import APIError

load_dotenv()

VEHICLE_PROFILES = {
    "TRUCK_001": {"type": "truck", "max_speed": 95, "max_cargo": 20000},
    "VAN_002": {"type": "van", "max_speed": 120, "max_cargo": 3000},
    "BUS_003": {"type": "bus", "max_speed": 100, "max_cargo": 0},
    "TRUCK_004": {"type": "truck", "max_speed": 90, "max_cargo": 18000},
    "VAN_005": {"type": "van", "max_speed": 115, "max_cargo": 2500},
}


def generate_fleet_data(num_readings=24):
    """Generate vehicle fleet telemetry data.

    Args:
        num_readings: Hourly readings per vehicle over 24h

    Returns:
        List of sensor readings
    """
    data = []
    base_time = datetime.now() - timedelta(hours=24)

    for vehicle_id, profile in VEHICLE_PROFILES.items():
        v_type = profile["type"]
        max_speed = profile["max_speed"]
        max_cargo = profile["max_cargo"]
        fuel_level = 85.0 + random.uniform(-15, 15)
        odometer = random.uniform(50000, 200000)
        base_lat = 40.60 + random.uniform(-0.02, 0.02)
        base_lon = 22.93 + random.uniform(-0.02, 0.02)

        for hour in range(num_readings):
            timestamp = base_time + timedelta(hours=hour)
            h = timestamp.hour

            is_driving = 6 <= h <= 22
            if not is_driving:
                speed = 0
            elif v_type == "truck":
                speed = random.randint(30, max_speed)
            elif v_type == "van":
                speed = random.randint(20, max_speed)
            else:
                speed = random.randint(15, max_speed)

            rpm = 600 if speed == 0 else 800 + speed * 30
            rpm = min(4500, rpm + random.randint(-200, 200))

            fuel_rate = 3.0 if speed == 0 else speed * 0.15
            fuel_rate += random.uniform(-1, 2)
            fuel_rate = round(max(3, min(25, fuel_rate)), 1)

            fuel_level -= fuel_rate * 0.05
            fuel_level = max(10, fuel_level)

            engine_temp = 80 + speed * 0.2 + random.uniform(-5, 10)
            engine_temp = round(min(110, max(75, engine_temp)), 1)

            odometer += speed * 0.8
            lat = base_lat + random.uniform(-0.03, 0.03)
            lon = base_lon + random.uniform(-0.03, 0.03)

            cargo = 0
            if v_type == "truck":
                cargo = random.randint(2000, max_cargo)
            elif v_type == "van":
                cargo = random.randint(200, max_cargo)

            harsh = (
                random.choices([0, 1, 2, 3], weights=[0.8, 0.1, 0.05, 0.05])[0]
                if is_driving
                else 0
            )

            idle_time = random.randint(0, 30) if is_driving else 0

            reading = {
                "key": vehicle_id,
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "speed_kmh": speed,
                "heading_deg": random.randint(0, 359),
                "fuel_level_pct": round(fuel_level, 1),
                "fuel_consumption_lph": fuel_rate,
                "engine_rpm": rpm,
                "engine_temperature_c": engine_temp,
                "odometer_km": round(odometer, 1),
                "tire_pressure_bar": round(random.uniform(2.0, 3.8), 1),
                "harsh_braking_count": harsh,
                "idle_time_min": idle_time,
                "cargo_weight_kg": cargo,
                "battery_voltage_v": round(random.uniform(11.5, 14.5), 1),
            }
            data.append(reading)

    return data


def main():
    """Run the fleet management example."""
    total_start = time.time()

    project_id = os.getenv("NOSTRADAMUS_PROJECT_ID")
    master_key = os.getenv("NOSTRADAMUS_MASTER_KEY")
    write_key = os.getenv("NOSTRADAMUS_WRITE_KEY")
    read_key = os.getenv("NOSTRADAMUS_READ_KEY")

    if not all([project_id, master_key, write_key, read_key]):
        print("❌ Error: Missing required environment variables!")
        print()
        print("Please set:")
        print("  NOSTRADAMUS_PROJECT_ID")
        print("  NOSTRADAMUS_MASTER_KEY")
        print("  NOSTRADAMUS_WRITE_KEY")
        print("  NOSTRADAMUS_READ_KEY")
        return

    print("🚛 Nostradamus IoTO SDK - Fleet Management Example")
    print("=" * 60)

    # Step 1: Create Collection
    print("\n📦 Step 1: Creating fleet telemetry collection...")
    collection_id = None

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            collection = master_client.collections.create(
                project_id=project_id,
                name="fleet_telemetry",
                description="Vehicle fleet GPS and diagnostics",
                tags=["fleet", "transportation", "telemetry"],
                collection_schema={
                    "key": "TRUCK_001",
                    "timestamp": "2025-06-17T10:30:00Z",
                    "latitude": 40.60,
                    "longitude": 22.93,
                    "speed_kmh": 65,
                    "heading_deg": 180,
                    "fuel_level_pct": 72.0,
                    "fuel_consumption_lph": 12.5,
                    "engine_rpm": 2200,
                    "engine_temperature_c": 92.0,
                    "odometer_km": 85000.0,
                    "tire_pressure_bar": 3.2,
                    "harsh_braking_count": 0,
                    "idle_time_min": 5,
                    "cargo_weight_kg": 12000,
                    "battery_voltage_v": 13.8,
                },
            )
            collection_id = collection.collection_id
            print(f"✅ Collection created: {collection.collection_name}")
            print(f"   ID: {collection_id}")
        except APIError as e:
            if e.status_code == 409:
                print("⚠️  Collection exists, finding it...")
                collections = master_client.collections.list(project_id)
                for coll in collections:
                    if coll.collection_name == "fleet_telemetry":
                        collection_id = coll.collection_id
                        print(f"✅ Using: {coll.collection_name}")
                        break
                if not collection_id:
                    print("❌ Could not find collection")
                    return
            else:
                print(f"❌ Failed: {e}")
                return

    if not collection_id:
        print("❌ No collection available")
        return

    # Step 2: Generate and Send Data
    print("\n📤 Step 2: Generating fleet telemetry data...")
    print("   5 vehicles × 24 hourly readings...")

    fleet_data = generate_fleet_data(num_readings=24)
    print(f"   Generated {len(fleet_data)} readings")

    with NostradamusClient(api_key=write_key) as write_client:
        try:
            write_client.data.send(
                project_id=project_id,
                collection_id=collection_id,
                data=fleet_data,
            )
            print(f"✅ Sent {len(fleet_data)} records")
        except APIError as e:
            print(f"❌ Failed to send: {e}")

    # Step 3: Query Data
    print("\n📥 Step 3: Querying with fleet-specific filters...")

    with NostradamusClient(api_key=read_key) as read_client:
        print("\n   3.1: Getting all data...")
        try:
            all_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
            )
            print(f"   ✅ Retrieved {len(all_data)} records")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.2: Filter by TRUCK_001...")
        try:
            truck_filter = [
                {
                    "property_name": "key",
                    "operator": "eq",
                    "property_value": "TRUCK_001",
                }
            ]
            truck_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=truck_filter,
            )
            print(f"   ✅ {len(truck_data)} records for TRUCK_001")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.3: 🚨 Speeding events (> 90 km/h)...")
        try:
            speed_filter = [
                {
                    "property_name": "speed_kmh",
                    "operator": "gt",
                    "property_value": 90,
                }
            ]
            speeding = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=speed_filter,
            )
            print(f"   ✅ Found {len(speeding)} speeding events")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.4: 🌡️ Engine overheating (temp > 100°C)...")
        try:
            overheat_filter = [
                {
                    "property_name": "engine_temperature_c",
                    "operator": "gt",
                    "property_value": 100,
                }
            ]
            overheating = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=overheat_filter,
            )
            print(f"   ✅ Found {len(overheating)} overheating events")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.5: ⛽ Low fuel (< 20%)...")
        try:
            fuel_filter = [
                {
                    "property_name": "fuel_level_pct",
                    "operator": "lt",
                    "property_value": 20,
                }
            ]
            low_fuel = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=fuel_filter,
            )
            print(f"   ✅ Found {len(low_fuel)} low fuel readings")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.6: Fuel consumption ranking (worst first)...")
        try:
            ranked = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                attributes=["key", "fuel_consumption_lph"],
                order_by='{"field": "fuel_consumption_lph", "order": "desc"}',
                limit=5,
            )
            if isinstance(ranked, list) and ranked:
                top = ranked[0]
                print(
                    f"   ✅ Worst: {top.get('fuel_consumption_lph')}"
                    f" L/h ({top.get('key')})"
                )
        except APIError as e:
            print(f"   ❌ {e}")

    # Step 4: Statistics
    print("\n📈 Step 4: Getting statistics...")

    with NostradamusClient(api_key=read_key) as read_client:
        for label, attr, op in [
            ("Avg speed", "speed_kmh", "avg"),
            ("Max engine temp", "engine_temperature_c", "max"),
            ("Min fuel level", "fuel_level_pct", "min"),
            ("Distinct vehicles", "key", "distinct"),
        ]:
            try:
                result = read_client.data.statistics(
                    project_id=project_id,
                    collection_id=collection_id,
                    attribute=attr,
                    operation=op,
                )
                print(f"   ✅ {label}: {result}")
            except APIError as e:
                print(f"   ❌ {label}: {e}")

    # Step 5: Delete Specific Data
    print("\n🗑️  Step 5: Deleting data...")
    from_time = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_time = (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
    print("   Removing first 12h for TRUCK_001...")

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            result = master_client.data.delete(
                project_id=project_id,
                collection_id=collection_id,
                key="TRUCK_001",
                timestamp_from=from_time,
                timestamp_to=to_time,
            )
            print(f"✅ Deleted: {result.get('message', 'Success')}")
        except APIError as e:
            print(f"❌ Failed: {e}")

    # Step 6: Cleanup
    print("\n🧹 Step 6: Cleaning up...")

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            master_client.collections.delete(
                project_id=project_id,
                collection_id=collection_id,
            )
            print("✅ Collection deleted")
        except APIError as e:
            print(f"❌ Failed: {e}")

    total_duration = time.time() - total_start
    print("\n" + "=" * 60)
    print("✨ Fleet management example completed!")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
