#!/usr/bin/env python3
"""
Precision farming example for the Nostradamus IoTO SDK.

Demonstrates multi-zone crop monitoring data ingestion, querying,
statistics, and cleanup using sync clients.
"""

import json
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

# --- Configuration ---
COLLECTION_NAME = "precision_farming_data"
ZONES = [
    "ZONE_A_FIELD_01",
    "ZONE_B_FIELD_02",
    "ZONE_C_FIELD_03",
    "ZONE_D_FIELD_04",
]
COLLECTION_SCHEMA = {
    "key": "ZONE_A_FIELD_01",
    "timestamp": "2026-02-13T10:00:00Z",
    "soil_moisture_pct": 45.5,
    "soil_temperature_c": 22.1,
    "ambient_temperature_c": 25.0,
    "ambient_humidity_pct": 65.0,
    "light_intensity_lux": 85000,
    "ndvi": 0.75,
    "leaf_wetness_duration_min": 30,
    "wind_speed_kmh": 15.5,
    "rainfall_mm": 0.0,
    "battery_pct": 95.0,
}


def generate_data(zones, num_readings=24):
    """Generates synthetic precision farming sensor data."""
    data = []
    base_time = datetime.now() - timedelta(hours=num_readings)

    for zone in zones:
        for i in range(num_readings):
            ts = base_time + timedelta(hours=i)

            # Generate realistic random data within specified ranges
            soil_moisture = round(random.uniform(15.0, 65.0), 1)
            soil_temp = round(random.uniform(8.0, 32.0), 1)
            ambient_temp = round(random.uniform(5.0, 38.0), 1)
            ambient_humidity = round(random.uniform(30.0, 85.0), 1)
            light_intensity = random.randint(0, 120000)
            ndvi = round(random.uniform(0.2, 0.9), 2)
            leaf_wetness = random.randint(0, 180)
            wind_speed = round(random.uniform(0.0, 45.0), 1)
            rainfall = round(random.uniform(0.0, 25.0), 1)
            battery = round(random.uniform(60.0, 100.0), 1)

            data.append(
                {
                    "key": zone,
                    "timestamp": ts.isoformat() + "Z",
                    "soil_moisture_pct": soil_moisture,
                    "soil_temperature_c": soil_temp,
                    "ambient_temperature_c": ambient_temp,
                    "ambient_humidity_pct": ambient_humidity,
                    "light_intensity_lux": light_intensity,
                    "ndvi": ndvi,
                    "leaf_wetness_duration_min": leaf_wetness,
                    "wind_speed_kmh": wind_speed,
                    "rainfall_mm": rainfall,
                    "battery_pct": battery,
                }
            )
    return data


def main():
    """Run the precision farming example."""
    total_start = time.time()
    collection_id = None

    # Get credentials
    project_id = os.getenv("NOSTRADAMUS_PROJECT_ID")
    master_key = os.getenv("NOSTRADAMUS_MASTER_KEY")
    write_key = os.getenv("NOSTRADAMUS_WRITE_KEY")
    read_key = os.getenv("NOSTRADAMUS_READ_KEY")

    if not all([project_id, master_key, write_key, read_key]):
        print("❌ Error: Missing one or more required environment variables:")
        print("   NOSTRADAMUS_PROJECT_ID, NOSTRADAMUS_MASTER_KEY,")
        print("   NOSTRADAMUS_WRITE_KEY, NOSTRADAMUS_READ_KEY")
        return

    print(f"🌾 Starting Precision Farming Example for Project: {project_id}")

    # Step 1: Create Collection with Schema (master_key)
    print(f"\n📦 Step 1: Creating collection '{COLLECTION_NAME}'...")
    try:
        with NostradamusClient(api_key=master_key) as master_client:
            collection = master_client.collections.create(
                project_id=project_id,
                name=COLLECTION_NAME,
                description="Multi-zone crop monitoring data.",
                tags=["agriculture", "precision-farming", "sensor"],
                collection_schema=COLLECTION_SCHEMA,
            )
            collection_id = collection.collection_id
            print(f"✅ Collection created with ID: {collection_id}")
    except APIError as e:
        if e.status_code == 409:
            print("⚠️ Collection already exists. Attempting to find ID...")
            try:
                with NostradamusClient(api_key=master_key) as master_client:
                    collections = master_client.collections.list(project_id=project_id)
                    for c in collections:
                        if c.name == COLLECTION_NAME:
                            collection_id = c.collection_id
                            print(f"✅ Found existing collection ID: {collection_id}")
                            break
                    if not collection_id:
                        print("❌ Error: Could not find existing collection.")
                        return
            except APIError as find_e:
                print(f"❌ Error finding existing collection: {find_e}")
                return
        else:
            print(f"❌ Error creating collection: {e}")
            return

    # Step 2: Generate and Send Data (write_key)
    print("\n📤 Step 2: Generating and sending 96 data points...")
    data = generate_data(ZONES)
    try:
        with NostradamusClient(api_key=write_key) as write_client:
            write_client.data.send(
                project_id=project_id,
                collection_id=collection_id,
                data=data,
            )
        print(f"✅ Successfully sent {len(data)} data points.")
    except APIError as e:
        print(f"❌ Error sending data: {e}")
        return

    # Step 3: Query Data (read_key)
    print("\n📥 Step 3: Querying data with agriculture-relevant filters...")
    try:
        with NostradamusClient(api_key=read_key) as read_client:
            # Query 3.1: Filter by specific zone
            zone_filter = [
                {"property_name": "key", "operator": "eq", "property_value": ZONES[0]}
            ]
            results = read_client.data.query(
                project_id=project_id,
                collection_id=collection_id,
                filters=zone_filter,
                limit=5,
            )
            print(f"  - Found {len(results)} readings for {ZONES[0]} (limit 5).")

            # Query 3.2: Drought stress risk (low moisture + high temp)
            drought_filter = [
                {
                    "property_name": "soil_moisture_pct",
                    "operator": "lt",
                    "property_value": 25.0,
                },
                {
                    "property_name": "ambient_temperature_c",
                    "operator": "gt",
                    "property_value": 30.0,
                },
            ]
            results = read_client.data.query(
                project_id=project_id,
                collection_id=collection_id,
                filters=drought_filter,
                limit=10,
            )
            print(f"  - Found {len(results)} potential drought stress readings.")

            # Query 3.3: Disease risk (high leaf wetness + high humidity)
            disease_filter = [
                {
                    "property_name": "leaf_wetness_duration_min",
                    "operator": "gt",
                    "property_value": 120,
                },
                {
                    "property_name": "ambient_humidity_pct",
                    "operator": "gt",
                    "property_value": 80.0,
                },
            ]
            results = read_client.data.query(
                project_id=project_id,
                collection_id=collection_id,
                filters=disease_filter,
                limit=10,
            )
            print(f"  - Found {len(results)} potential disease risk readings.")

            # Query 3.4: Crop health ranking (Order by NDVI descending)
            ndvi_order = json.dumps({"field": "ndvi", "order": "desc"})
            results = read_client.data.query(
                project_id=project_id,
                collection_id=collection_id,
                order_by=ndvi_order,
                limit=3,
            )
            print("  - Top 3 healthiest readings (NDVI):")
            for r in results:
                print(f"    > {r['key']} @ {r['timestamp'][:16]} | NDVI: {r['ndvi']}")

    except APIError as e:
        print(f"❌ Error querying data: {e}")

    # Step 4: Statistics (read_key)
    print("\n📈 Step 4: Calculating key statistics...")
    try:
        with NostradamusClient(api_key=read_key) as read_client:
            # Avg Soil Moisture
            avg_moisture = read_client.data.statistics(
                project_id=project_id,
                collection_id=collection_id,
                attribute="soil_moisture_pct",
                operation="avg",
            )
            print(f"  - Average Soil Moisture: {avg_moisture['value']:.2f}%")

            # Max Ambient Temperature
            max_temp = read_client.data.statistics(
                project_id=project_id,
                collection_id=collection_id,
                attribute="ambient_temperature_c",
                operation="max",
            )
            print(f"  - Maximum Ambient Temp: {max_temp['value']:.1f}°C")

            # Min Battery Percentage
            min_battery = read_client.data.statistics(
                project_id=project_id,
                collection_id=collection_id,
                attribute="battery_pct",
                operation="min",
            )
            print(f"  - Minimum Battery Level: {min_battery['value']:.1f}%")

            # Distinct Zones
            distinct_zones = read_client.data.statistics(
                project_id=project_id,
                collection_id=collection_id,
                attribute="key",
                operation="distinct",
            )
            print(f"  - Distinct Zones Monitored: {distinct_zones['value']}")

    except APIError as e:
        print(f"❌ Error calculating statistics: {e}")

    # Step 5: Delete Specific Data (master_key)
    print("\n🗑️ Step 5: Deleting first 12 hours of data for ZONE_A_FIELD_01...")
    try:
        with NostradamusClient(api_key=master_key) as master_client:
            start_time = datetime.now() - timedelta(hours=24)
            end_time = start_time + timedelta(hours=12)

            delete_filters = [
                {"property_name": "key", "operator": "eq", "property_value": ZONES[0]},
                {
                    "property_name": "timestamp",
                    "operator": "gte",
                    "property_value": start_time.isoformat() + "Z",
                },
                {
                    "property_name": "timestamp",
                    "operator": "lt",
                    "property_value": end_time.isoformat() + "Z",
                },
            ]

            delete_result = master_client.data.delete(
                project_id=project_id,
                collection_id=collection_id,
                filters=delete_filters,
            )
            print(
                f"✅ Delete successful. Records affected: "
                f"{delete_result.get('deleted_count', 'N/A')}"
            )
    except APIError as e:
        print(f"❌ Error deleting data: {e}")

    # Step 6: Cleanup (master_key)
    print(f"\n🧹 Step 6: Cleaning up and deleting collection '{COLLECTION_NAME}'...")
    try:
        if collection_id:
            with NostradamusClient(api_key=master_key) as master_client:
                master_client.collections.delete(
                    project_id=project_id, collection_id=collection_id
                )
            print("✅ Collection deleted successfully.")
    except APIError as e:
        print(f"❌ Error deleting collection: {e}")

    total_duration = time.time() - total_start
    print(f"\n✨ Example finished in {total_duration:.2f} seconds.")


if __name__ == "__main__":
    main()
