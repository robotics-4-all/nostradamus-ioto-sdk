#!/usr/bin/env python3
"""
Nostradamus IoTO SDK - Greenhouse Automation Example

Demonstrates greenhouse climate control monitoring with actuator feedback:
1. Create a collection with schema
2. Generate and send greenhouse sensor data
3. Query data with climate-specific filters
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


def generate_greenhouse_data(num_zones=3, num_readings=48):
    """Generate greenhouse climate and actuator data.

    Args:
        num_zones: Number of greenhouse zones
        num_readings: Readings per zone (30-min intervals over 24h)

    Returns:
        List of sensor readings
    """
    data = []
    base_time = datetime.now() - timedelta(hours=24)
    zone_ids = ["GH_01_ZONE_A", "GH_01_ZONE_B", "GH_02_ZONE_A"]

    for zone_idx in range(min(num_zones, len(zone_ids))):
        zone_id = zone_ids[zone_idx]
        temp_base = 22.0 + zone_idx * 2.0

        for i in range(num_readings):
            timestamp = base_time + timedelta(minutes=30 * i)
            hour = timestamp.hour

            is_daytime = 6 <= hour <= 20
            solar_factor = max(0, 1.0 - abs(hour - 13) / 7.0)

            air_temp = temp_base + solar_factor * 12.0
            air_temp += random.uniform(-2, 2)
            air_temp = round(min(42, max(18, air_temp)), 1)

            humidity = 70.0 - solar_factor * 20.0
            humidity += random.uniform(-5, 5)
            humidity = round(min(95, max(40, humidity)), 1)

            co2 = 400 + random.uniform(-50, 600)
            if is_daytime:
                co2 -= 100 * solar_factor
            co2 = round(min(1200, max(350, co2)), 0)

            par = solar_factor * 600 + random.uniform(-50, 100)
            par = round(max(0, min(800, par)), 0)

            moisture = 50.0 + random.uniform(-20, 15)
            ec = round(random.uniform(0.5, 4.0), 2)
            ph = round(random.uniform(5.5, 7.0), 1)

            vpd = round(random.uniform(0.4, 2.5), 2)

            vent = 0.0
            if air_temp > 28:
                vent = min(100, (air_temp - 28) * 15)
            vent = round(vent + random.uniform(-5, 5), 0)
            vent = max(0, min(100, vent))

            heating = 1 if air_temp < 20 else 0
            irrigation = 1 if moisture < 35 else 0
            fogger = 1 if humidity < 50 and is_daytime else 0

            reading = {
                "key": zone_id,
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                "air_temperature_c": air_temp,
                "relative_humidity_pct": humidity,
                "co2_ppm": co2,
                "par_light_umol": par,
                "substrate_moisture_pct": round(moisture, 1),
                "substrate_ec_ms": ec,
                "substrate_ph": ph,
                "vpd_kpa": vpd,
                "vent_position_pct": vent,
                "heating_active": heating,
                "irrigation_active": irrigation,
                "fogger_active": fogger,
            }
            data.append(reading)

    return data


def main():
    """Run the greenhouse automation example."""
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

    print("🌿 Nostradamus IoTO SDK - Greenhouse Automation Example")
    print("=" * 60)

    # Step 1: Create Collection
    print("\n📦 Step 1: Creating greenhouse sensors collection...")
    collection_id = None

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            collection = master_client.collections.create(
                project_id=project_id,
                name="greenhouse_sensors",
                description="Greenhouse climate and actuator data",
                tags=["greenhouse", "climate", "automation"],
                collection_schema={
                    "key": "GH_01_ZONE_A",
                    "timestamp": "2025-06-17T10:30:00Z",
                    "air_temperature_c": 28.5,
                    "relative_humidity_pct": 65.0,
                    "co2_ppm": 800.0,
                    "par_light_umol": 450.0,
                    "substrate_moisture_pct": 55.0,
                    "substrate_ec_ms": 2.1,
                    "substrate_ph": 6.2,
                    "vpd_kpa": 1.2,
                    "vent_position_pct": 40.0,
                    "heating_active": 0,
                    "irrigation_active": 1,
                    "fogger_active": 0,
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
                    if coll.collection_name == "greenhouse_sensors":
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
    print("\n📤 Step 2: Generating greenhouse sensor data...")
    print("   3 zones × 48 readings (30-min intervals)...")

    greenhouse_data = generate_greenhouse_data(num_zones=3, num_readings=48)
    print(f"   Generated {len(greenhouse_data)} readings")

    with NostradamusClient(api_key=write_key) as write_client:
        try:
            write_client.data.send(
                project_id=project_id,
                collection_id=collection_id,
                data=greenhouse_data,
            )
            print(f"✅ Sent {len(greenhouse_data)} records")
        except APIError as e:
            print(f"❌ Failed to send: {e}")

    # Step 3: Query Data
    print("\n📥 Step 3: Querying with climate-specific filters...")

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

        print("\n   3.2: 🌡️ Heat stress (temp > 35 AND vent < 50%)...")
        try:
            heat_filter = [
                {
                    "property_name": "air_temperature_c",
                    "operator": "gt",
                    "property_value": 35,
                },
                {
                    "property_name": "vent_position_pct",
                    "operator": "lt",
                    "property_value": 50,
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

        print("\n   3.3: 🫧 Low CO2 needing enrichment (< 400 ppm)...")
        try:
            co2_filter = [
                {
                    "property_name": "co2_ppm",
                    "operator": "lt",
                    "property_value": 400,
                },
            ]
            co2_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=co2_filter,
            )
            print(f"   ✅ Found {len(co2_data)} low CO2 readings")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.4: 💧 Irrigation events...")
        try:
            irrig_filter = [
                {
                    "property_name": "irrigation_active",
                    "operator": "eq",
                    "property_value": 1,
                },
            ]
            irrig_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=irrig_filter,
            )
            print(f"   ✅ Found {len(irrig_data)} irrigation events")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.5: VPD ordered descending...")
        try:
            vpd_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                attributes=["key", "vpd_kpa", "air_temperature_c"],
                order_by='{"field": "vpd_kpa", "order": "desc"}',
                limit=5,
            )
            if isinstance(vpd_data, list) and vpd_data:
                print(f"   ✅ Highest VPD: {vpd_data[0].get('vpd_kpa')}")
        except APIError as e:
            print(f"   ❌ {e}")

    # Step 4: Statistics
    print("\n📈 Step 4: Getting statistics...")

    with NostradamusClient(api_key=read_key) as read_client:
        for label, attr, op in [
            ("Average air temperature", "air_temperature_c", "avg"),
            ("Maximum CO2", "co2_ppm", "max"),
            ("Minimum substrate moisture", "substrate_moisture_pct", "min"),
            ("Distinct zones", "key", "distinct"),
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
    print("   Removing first 12h for GH_01_ZONE_A...")

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            result = master_client.data.delete(
                project_id=project_id,
                collection_id=collection_id,
                key="GH_01_ZONE_A",
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
    print("✨ Greenhouse automation example completed!")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
