#!/usr/bin/env python3
"""
Nostradamus IoTO SDK - Air Quality Monitoring Example

Demonstrates urban air quality sensor network monitoring:
1. Create a collection with schema
2. Generate and send station data with pollution profiles
3. Query data with environment-specific filters
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

STATION_PROFILES = {
    "AQ_STATION_DOWNTOWN": {
        "pm25": (15, 60),
        "pm10": (20, 80),
        "no2": (20, 70),
        "o3": (15, 50),
        "co": (0.5, 3.0),
        "so2": (3, 15),
    },
    "AQ_STATION_INDUSTRIAL": {
        "pm25": (30, 120),
        "pm10": (50, 180),
        "no2": (15, 60),
        "o3": (10, 40),
        "co": (0.5, 2.5),
        "so2": (10, 40),
    },
    "AQ_STATION_PARK": {
        "pm25": (5, 30),
        "pm10": (10, 40),
        "no2": (5, 25),
        "o3": (20, 70),
        "co": (0.1, 1.0),
        "so2": (1, 8),
    },
    "AQ_STATION_HIGHWAY": {
        "pm25": (20, 80),
        "pm10": (30, 100),
        "no2": (40, 120),
        "o3": (10, 45),
        "co": (1.0, 5.0),
        "so2": (2, 12),
    },
}


def generate_air_quality_data(num_readings=48):
    """Generate air quality sensor data with station-specific profiles.

    Args:
        num_readings: Readings per station (30-min intervals)

    Returns:
        List of sensor readings
    """
    data = []
    base_time = datetime.now() - timedelta(hours=24)

    for station_id, profile in STATION_PROFILES.items():
        for i in range(num_readings):
            timestamp = base_time + timedelta(minutes=30 * i)
            hour = timestamp.hour

            is_rush = hour in (7, 8, 9, 17, 18, 19)
            traffic_factor = 1.3 if is_rush else 1.0

            pm25 = random.uniform(*profile["pm25"]) * traffic_factor
            pm10 = random.uniform(*profile["pm10"]) * traffic_factor
            no2 = random.uniform(*profile["no2"]) * traffic_factor
            o3 = random.uniform(*profile["o3"])
            co = random.uniform(*profile["co"]) * traffic_factor
            so2 = random.uniform(*profile["so2"])

            temp = 15 + 10 * max(0, 1 - abs(hour - 14) / 8.0)
            temp += random.uniform(-3, 3)

            aqi = max(
                pm25 / 55 * 100,
                pm10 / 150 * 100,
                no2 / 100 * 100,
                o3 / 70 * 100,
            )

            reading = {
                "key": station_id,
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                "pm25_ugm3": round(min(150, pm25), 1),
                "pm10_ugm3": round(min(200, pm10), 1),
                "no2_ppb": round(min(120, no2), 1),
                "o3_ppb": round(min(80, o3), 1),
                "co_ppm": round(min(5.0, co), 2),
                "so2_ppb": round(min(40, so2), 1),
                "temperature_c": round(min(35, max(5, temp)), 1),
                "humidity_pct": round(random.uniform(30, 90), 1),
                "wind_speed_ms": round(random.uniform(0, 15), 1),
                "aqi_index": round(min(200, max(20, aqi)), 0),
                "battery_pct": round(
                    100 - (i / num_readings) * 25 + random.uniform(-3, 3),
                    1,
                ),
            }
            data.append(reading)

    return data


def main():
    """Run the air quality monitoring example."""
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

    print("🏙️ Nostradamus IoTO SDK - Air Quality Monitoring Example")
    print("=" * 60)

    # Step 1: Create Collection
    print("\n📦 Step 1: Creating air quality stations collection...")
    collection_id = None

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            collection = master_client.collections.create(
                project_id=project_id,
                name="air_quality_stations",
                description="Urban air quality monitoring network",
                tags=["air-quality", "smart-city", "environment"],
                collection_schema={
                    "key": "AQ_STATION_DOWNTOWN",
                    "timestamp": "2025-06-17T10:30:00Z",
                    "pm25_ugm3": 25.3,
                    "pm10_ugm3": 45.0,
                    "no2_ppb": 35.2,
                    "o3_ppb": 42.0,
                    "co_ppm": 1.5,
                    "so2_ppb": 8.0,
                    "temperature_c": 22.0,
                    "humidity_pct": 55.0,
                    "wind_speed_ms": 3.5,
                    "aqi_index": 65.0,
                    "battery_pct": 92.0,
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
                    if coll.collection_name == "air_quality_stations":
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
    print("\n📤 Step 2: Generating air quality data...")
    print("   4 stations × 48 readings (30-min intervals)...")

    aq_data = generate_air_quality_data(num_readings=48)
    print(f"   Generated {len(aq_data)} readings")

    with NostradamusClient(api_key=write_key) as write_client:
        try:
            write_client.data.send(
                project_id=project_id,
                collection_id=collection_id,
                data=aq_data,
            )
            print(f"✅ Sent {len(aq_data)} records")
        except APIError as e:
            print(f"❌ Failed to send: {e}")

    # Step 3: Query Data
    print("\n📥 Step 3: Querying with environment filters...")

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

        print("\n   3.2: Filter by industrial station...")
        try:
            station_filter = [
                {
                    "property_name": "key",
                    "operator": "eq",
                    "property_value": "AQ_STATION_INDUSTRIAL",
                }
            ]
            station_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=station_filter,
            )
            print(f"   ✅ {len(station_data)} industrial readings")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.3: ⚠️ Unhealthy air (PM2.5 > 55 µg/m³)...")
        try:
            pm_filter = [
                {
                    "property_name": "pm25_ugm3",
                    "operator": "gt",
                    "property_value": 55,
                }
            ]
            unhealthy = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=pm_filter,
            )
            print(f"   ✅ Found {len(unhealthy)} unhealthy readings")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.4: 🌤️ Ozone alerts (O3 > 60 ppb)...")
        try:
            ozone_filter = [
                {
                    "property_name": "o3_ppb",
                    "operator": "gt",
                    "property_value": 60,
                }
            ]
            ozone_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=ozone_filter,
            )
            print(f"   ✅ Found {len(ozone_data)} ozone alerts")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.5: 🌫️ Stagnation events (PM10 > 80 AND wind < 3)...")
        try:
            stagnation_filter = [
                {
                    "property_name": "pm10_ugm3",
                    "operator": "gt",
                    "property_value": 80,
                },
                {
                    "property_name": "wind_speed_ms",
                    "operator": "lt",
                    "property_value": 3,
                },
            ]
            stagnation = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=stagnation_filter,
            )
            print(f"   ✅ Found {len(stagnation)} stagnation events")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.6: AQI ranking (worst first)...")
        try:
            ranked = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                attributes=["key", "aqi_index", "pm25_ugm3"],
                order_by='{"field": "aqi_index", "order": "desc"}',
                limit=5,
            )
            if isinstance(ranked, list) and ranked:
                top = ranked[0]
                print(f"   ✅ Worst AQI: {top.get('aqi_index')} ({top.get('key')})")
        except APIError as e:
            print(f"   ❌ {e}")

    # Step 4: Statistics
    print("\n📈 Step 4: Getting statistics...")

    with NostradamusClient(api_key=read_key) as read_client:
        for label, attr, op in [
            ("Average PM2.5", "pm25_ugm3", "avg"),
            ("Maximum AQI", "aqi_index", "max"),
            ("Minimum wind speed", "wind_speed_ms", "min"),
            ("Distinct stations", "key", "distinct"),
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
    print("   Removing first 12h for AQ_STATION_DOWNTOWN...")

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            result = master_client.data.delete(
                project_id=project_id,
                collection_id=collection_id,
                key="AQ_STATION_DOWNTOWN",
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
    print("✨ Air quality monitoring example completed!")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
