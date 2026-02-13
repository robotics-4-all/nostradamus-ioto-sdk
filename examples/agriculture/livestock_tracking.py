#!/usr/bin/env python3
"""
Nostradamus IoTO SDK - Livestock Tracking Example

Demonstrates cattle health monitoring and GPS tracking:
1. Create a collection with schema
2. Generate and send livestock sensor data
3. Query data with health-specific filters
4. Get statistics
5. Delete specific data
6. Clean up collection
"""

import os
import random
import time
from datetime import datetime, timedelta

from nostradamus_ioto_sdk import NostradamusClient
from nostradamus_ioto_sdk.exceptions import APIError


def generate_livestock_data(num_animals=5, num_readings=24):
    """Generate livestock health and location data.

    Args:
        num_animals: Number of cattle to simulate
        num_readings: Hourly readings per animal over 24h

    Returns:
        List of sensor readings
    """
    data = []
    base_time = datetime.now() - timedelta(hours=24)

    for animal_num in range(1, num_animals + 1):
        animal_id = f"CATTLE_{animal_num:03d}"
        base_lat = 40.003 + animal_num * 0.001
        base_lon = 22.004 + animal_num * 0.001

        for hour in range(num_readings):
            timestamp = base_time + timedelta(hours=hour)
            h = timestamp.hour

            is_resting = h < 6 or h > 21
            ambient_temp = 15 + 10 * max(0, 1.0 - abs(h - 14) / 8.0)
            ambient_temp += random.uniform(-3, 3)
            ambient_temp = round(min(35, max(5, ambient_temp)), 1)

            body_temp = 38.5 + random.uniform(-0.5, 1.0)
            if ambient_temp > 30:
                body_temp += 0.5
            body_temp = round(min(41.0, max(37.5, body_temp)), 1)

            activity = random.randint(0, 3) if is_resting else random.randint(3, 10)
            heart_rate = 50 + activity * 5 + random.randint(-5, 10)
            heart_rate = min(100, max(40, heart_rate))

            rumination = (
                random.randint(20, 50) if not is_resting else random.randint(30, 60)
            )
            if activity > 7:
                rumination = random.randint(0, 15)
            rumination = min(60, max(0, rumination))

            steps = activity * 40 + random.randint(-20, 50)
            steps = max(0, min(500, steps))

            lat = base_lat + random.uniform(-0.002, 0.002)
            lon = base_lon + random.uniform(-0.002, 0.002)

            reading = {
                "key": animal_id,
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "body_temperature_c": body_temp,
                "heart_rate_bpm": heart_rate,
                "activity_level": activity,
                "rumination_min": rumination,
                "steps_count": steps,
                "ambient_temperature_c": ambient_temp,
                "battery_pct": round(
                    100 - (hour / num_readings) * 40 + random.uniform(-5, 5),
                    1,
                ),
            }
            data.append(reading)

    return data


def main():
    """Run the livestock tracking example."""
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

    print("🐄 Nostradamus IoTO SDK - Livestock Tracking Example")
    print("=" * 60)

    # Step 1: Create Collection
    print("\n📦 Step 1: Creating livestock sensors collection...")
    collection_id = None

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            collection = master_client.collections.create(
                project_id=project_id,
                name="livestock_sensors",
                description="Cattle health and GPS tracking data",
                tags=["livestock", "cattle", "health", "gps"],
                collection_schema={
                    "key": "CATTLE_001",
                    "timestamp": "2025-06-17T10:30:00Z",
                    "latitude": 40.005,
                    "longitude": 22.005,
                    "body_temperature_c": 38.5,
                    "heart_rate_bpm": 60,
                    "activity_level": 5,
                    "rumination_min": 35,
                    "steps_count": 200,
                    "ambient_temperature_c": 22.0,
                    "battery_pct": 85.0,
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
                    if coll.collection_name == "livestock_sensors":
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
    print("\n📤 Step 2: Generating livestock sensor data...")
    print("   5 animals × 24 hourly readings...")

    livestock_data = generate_livestock_data(num_animals=5, num_readings=24)
    print(f"   Generated {len(livestock_data)} readings")

    with NostradamusClient(api_key=write_key) as write_client:
        try:
            write_client.data.send(
                project_id=project_id,
                collection_id=collection_id,
                data=livestock_data,
            )
            print(f"✅ Sent {len(livestock_data)} records")
        except APIError as e:
            print(f"❌ Failed to send: {e}")

    # Step 3: Query Data
    print("\n📥 Step 3: Querying with health-specific filters...")

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

        print("\n   3.2: Filter by CATTLE_001...")
        try:
            animal_filter = [
                {
                    "property_name": "key",
                    "operator": "eq",
                    "property_value": "CATTLE_001",
                }
            ]
            animal_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=animal_filter,
            )
            print(f"   ✅ {len(animal_data)} records for CATTLE_001")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.3: 🌡️ Fever detection (body temp > 39.5°C)...")
        try:
            fever_filter = [
                {
                    "property_name": "body_temperature_c",
                    "operator": "gt",
                    "property_value": 39.5,
                }
            ]
            fever_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=fever_filter,
            )
            print(f"   ✅ Found {len(fever_data)} fever readings")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.4: ⚠️ Illness risk (activity < 2 AND rumination < 10)...")
        try:
            illness_filter = [
                {
                    "property_name": "activity_level",
                    "operator": "lt",
                    "property_value": 2,
                },
                {
                    "property_name": "rumination_min",
                    "operator": "lt",
                    "property_value": 10,
                },
            ]
            illness_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=illness_filter,
            )
            print(f"   ✅ Found {len(illness_data)} illness risk readings")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.5: 🔥 Heat stress (ambient > 30 AND heart rate > 80)...")
        try:
            heat_filter = [
                {
                    "property_name": "ambient_temperature_c",
                    "operator": "gt",
                    "property_value": 30,
                },
                {
                    "property_name": "heart_rate_bpm",
                    "operator": "gt",
                    "property_value": 80,
                },
            ]
            heat_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=heat_filter,
            )
            print(f"   ✅ Found {len(heat_data)} heat stress events")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.6: Body temperature ranking (desc)...")
        try:
            ranked = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                attributes=["key", "body_temperature_c"],
                order_by='{"field": "body_temperature_c", "order": "desc"}',
                limit=5,
            )
            if isinstance(ranked, list) and ranked:
                top = ranked[0]
                print(
                    f"   ✅ Highest: {top.get('body_temperature_c')}°C"
                    f" ({top.get('key')})"
                )
        except APIError as e:
            print(f"   ❌ {e}")

    # Step 4: Statistics
    print("\n📈 Step 4: Getting statistics...")

    with NostradamusClient(api_key=read_key) as read_client:
        for label, attr, op in [
            ("Avg body temperature", "body_temperature_c", "avg"),
            ("Max heart rate", "heart_rate_bpm", "max"),
            ("Min rumination", "rumination_min", "min"),
            ("Distinct animals", "key", "distinct"),
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
    print("   Removing first 12h for CATTLE_001...")

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            result = master_client.data.delete(
                project_id=project_id,
                collection_id=collection_id,
                key="CATTLE_001",
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
    print("✨ Livestock tracking example completed!")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
