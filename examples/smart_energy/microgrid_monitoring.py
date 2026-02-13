#!/usr/bin/env python3
"""
Nostradamus IoTO SDK - Microgrid Monitoring Example

Demonstrates renewable energy microgrid monitoring (solar/wind/battery):
1. Create a collection with schema
2. Generate and send asset data with realistic day/night patterns
3. Query data with energy-specific filters
4. Get statistics
5. Delete specific data
6. Clean up collection
"""

import math
import os
import random
import time
from datetime import datetime, timedelta

from nostradamus_ioto_sdk import NostradamusClient
from nostradamus_ioto_sdk.exceptions import APIError


def generate_microgrid_data(num_readings=48):
    """Generate microgrid asset data with realistic energy patterns.

    Args:
        num_readings: Readings per asset (30-min intervals)

    Returns:
        List of sensor readings
    """
    data = []
    base_time = datetime.now() - timedelta(hours=24)
    assets = [
        "SOLAR_ARRAY_01",
        "SOLAR_ARRAY_02",
        "WIND_TURBINE_01",
        "BATTERY_BANK_01",
    ]

    for asset_id in assets:
        is_solar = asset_id.startswith("SOLAR")
        is_wind = asset_id.startswith("WIND")
        is_battery = asset_id.startswith("BATTERY")
        cumulative_kwh = 0.0
        battery_soc = 70.0

        for i in range(num_readings):
            timestamp = base_time + timedelta(minutes=30 * i)
            hour = timestamp.hour + timestamp.minute / 60.0

            has_fault = random.random() < 0.02

            if is_solar:
                solar_angle = (
                    max(0, math.sin(math.pi * (hour - 6) / 12))
                    if 6 <= hour <= 18
                    else 0.0
                )
                irradiance = solar_angle * 900 + random.uniform(-80, 80)
                irradiance = max(0, min(1000, irradiance))
                power = irradiance / 1000 * 50 * random.uniform(0.85, 1.0)
                power = round(max(0, min(50, power)), 2)
                voltage = 350 + power * 5 + random.uniform(-10, 10)
                voltage = round(min(600, max(300, voltage)), 1)
                temp = 20 + power * 1.0 + random.uniform(-3, 5)
                efficiency = round(random.uniform(15, 22), 1) if power > 0 else 0.0
            elif is_wind:
                irradiance = 0
                wind_speed = abs(random.gauss(8, 4) + random.uniform(-2, 2))
                wind_speed = round(min(25, max(0, wind_speed)), 1)
                if wind_speed < 3:
                    power = 0
                elif wind_speed > 20:
                    power = 0
                else:
                    power = (wind_speed / 15) ** 3 * 100
                    power = round(
                        min(100, max(0, power)) * random.uniform(0.8, 1.0),
                        2,
                    )
                voltage = round(380 + random.uniform(-5, 40), 1)
                temp = 25 + power * 0.3 + random.uniform(-5, 10)
                efficiency = round(random.uniform(25, 45), 1) if power > 0 else 0.0
            else:
                irradiance = 0
                wind_speed = 0
                solar_angle = (
                    max(0, math.sin(math.pi * (hour - 6) / 12))
                    if 6 <= hour <= 18
                    else 0.0
                )
                if solar_angle > 0.3:
                    power = round(random.uniform(5, 30), 2)
                    battery_soc = min(100, battery_soc + power * 0.3)
                else:
                    power = round(-random.uniform(5, 25), 2)
                    battery_soc = max(20, battery_soc + power * 0.3)
                voltage = round(
                    48 + (battery_soc - 50) * 0.16 + random.uniform(-0.5, 0.5),
                    1,
                )
                temp = 25 + abs(power) * 0.5 + random.uniform(-3, 5)
                efficiency = round(random.uniform(85, 98), 1)

            current = round(abs(power) * 1000 / max(voltage, 1), 1)
            cumulative_kwh += abs(power) * 0.5

            reading = {
                "key": asset_id,
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                "power_output_kw": power,
                "energy_cumulative_kwh": round(cumulative_kwh, 1),
                "voltage_v": voltage,
                "current_a": current,
                "temperature_c": round(min(75, max(15, temp)), 1),
                "efficiency_pct": efficiency,
                "grid_frequency_hz": round(50.0 + random.uniform(-0.2, 0.2), 2),
                "status": 0 if has_fault else 1,
            }

            if is_solar:
                reading["solar_irradiance_wm2"] = round(irradiance, 0)
            if is_wind:
                reading["wind_speed_ms"] = wind_speed
            if is_battery:
                reading["battery_soc_pct"] = round(battery_soc, 1)

            data.append(reading)

    return data


def main():
    """Run the microgrid monitoring example."""
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

    print("⚡ Nostradamus IoTO SDK - Microgrid Monitoring Example")
    print("=" * 60)

    # Step 1: Create Collection
    print("\n📦 Step 1: Creating microgrid assets collection...")
    collection_id = None

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            collection = master_client.collections.create(
                project_id=project_id,
                name="microgrid_assets",
                description="Solar/wind/battery microgrid data",
                tags=["energy", "microgrid", "renewable"],
                collection_schema={
                    "key": "SOLAR_ARRAY_01",
                    "timestamp": "2025-06-17T10:30:00Z",
                    "power_output_kw": 35.5,
                    "energy_cumulative_kwh": 150.0,
                    "voltage_v": 480.0,
                    "current_a": 73.9,
                    "temperature_c": 45.0,
                    "efficiency_pct": 19.5,
                    "solar_irradiance_wm2": 850.0,
                    "wind_speed_ms": 0.0,
                    "battery_soc_pct": 0.0,
                    "grid_frequency_hz": 50.01,
                    "status": 1,
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
                    if coll.collection_name == "microgrid_assets":
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
    print("\n📤 Step 2: Generating microgrid data...")
    print("   4 assets × 48 readings (30-min intervals)...")

    grid_data = generate_microgrid_data(num_readings=48)
    print(f"   Generated {len(grid_data)} readings")

    with NostradamusClient(api_key=write_key) as write_client:
        try:
            write_client.data.send(
                project_id=project_id,
                collection_id=collection_id,
                data=grid_data,
            )
            print(f"✅ Sent {len(grid_data)} records")
        except APIError as e:
            print(f"❌ Failed to send: {e}")

    # Step 3: Query Data
    print("\n📥 Step 3: Querying with energy-specific filters...")

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

        print("\n   3.2: Filter by SOLAR_ARRAY_01...")
        try:
            solar_filter = [
                {
                    "property_name": "key",
                    "operator": "eq",
                    "property_value": "SOLAR_ARRAY_01",
                }
            ]
            solar_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=solar_filter,
            )
            print(f"   ✅ {len(solar_data)} solar array readings")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.3: 🔋 Low battery SOC (< 30%)...")
        try:
            batt_filter = [
                {
                    "property_name": "battery_soc_pct",
                    "operator": "lt",
                    "property_value": 30,
                }
            ]
            low_batt = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=batt_filter,
            )
            print(f"   ✅ Found {len(low_batt)} low SOC readings")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.4: ⚠️ Fault events (status == 0)...")
        try:
            fault_filter = [
                {
                    "property_name": "status",
                    "operator": "eq",
                    "property_value": 0,
                }
            ]
            faults = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=fault_filter,
            )
            print(f"   ✅ Found {len(faults)} fault events")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.5: ☀️ Peak solar (irradiance > 700 AND power > 35kW)...")
        try:
            peak_filter = [
                {
                    "property_name": "solar_irradiance_wm2",
                    "operator": "gt",
                    "property_value": 700,
                },
                {
                    "property_name": "power_output_kw",
                    "operator": "gt",
                    "property_value": 35,
                },
            ]
            peak = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=peak_filter,
            )
            print(f"   ✅ Found {len(peak)} peak production events")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.6: Power output ranking (desc)...")
        try:
            ranked = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                attributes=["key", "power_output_kw"],
                order_by='{"field": "power_output_kw", "order": "desc"}',
                limit=5,
            )
            if isinstance(ranked, list) and ranked:
                top = ranked[0]
                print(f"   ✅ Peak: {top.get('power_output_kw')}kW ({top.get('key')})")
        except APIError as e:
            print(f"   ❌ {e}")

    # Step 4: Statistics
    print("\n📈 Step 4: Getting statistics...")

    with NostradamusClient(api_key=read_key) as read_client:
        for label, attr, op in [
            ("Avg power output", "power_output_kw", "avg"),
            ("Max temperature", "temperature_c", "max"),
            ("Min battery SOC", "battery_soc_pct", "min"),
            ("Distinct assets", "key", "distinct"),
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
    print("   Removing first 12h for SOLAR_ARRAY_01...")

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            result = master_client.data.delete(
                project_id=project_id,
                collection_id=collection_id,
                key="SOLAR_ARRAY_01",
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
    print("✨ Microgrid monitoring example completed!")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
