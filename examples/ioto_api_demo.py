#!/usr/bin/env python3
"""
Nostradamus IoTO SDK - API Demonstration Example

This is the SDK equivalent of the Colab notebook
"Nostradamus_IoTO_API_example_demonstration.ipynb" that was
used as an introduction for partners.

It demonstrates the exact same workflow:
1. Create a soil sensors collection with schema
2. Generate and send soil sensor data (3 sensors × 24 readings)
3. Query data with various filters and ordering
4. Get statistics (avg, max, min, distinct)
5. Delete specific data by key and time range
6. Clean up collection

Environment Variables Required:
    NOSTRADAMUS_PROJECT_ID  - Your project UUID
    NOSTRADAMUS_MASTER_KEY  - Master API key (full access)
    NOSTRADAMUS_WRITE_KEY   - Write API key
    NOSTRADAMUS_READ_KEY    - Read API key

Usage:
    export NOSTRADAMUS_PROJECT_ID="your-project-id"
    export NOSTRADAMUS_MASTER_KEY="your-master-key"
    export NOSTRADAMUS_WRITE_KEY="your-write-key"
    export NOSTRADAMUS_READ_KEY="your-read-key"
    python examples/ioto_api_demo.py
"""

import os
import random
from datetime import datetime, timedelta

from nostradamus_ioto_sdk import NostradamusClient
from nostradamus_ioto_sdk.exceptions import APIError

# ─── Configuration ───────────────────────────────────────────
PROJECT_ID = os.getenv("NOSTRADAMUS_PROJECT_ID")
MASTER_KEY = os.getenv("NOSTRADAMUS_MASTER_KEY")
WRITE_KEY = os.getenv("NOSTRADAMUS_WRITE_KEY")
READ_KEY = os.getenv("NOSTRADAMUS_READ_KEY")

if not all([PROJECT_ID, MASTER_KEY, WRITE_KEY, READ_KEY]):
    print("❌ Error: Missing required environment variables!")
    print()
    print("Please set:")
    print('  export NOSTRADAMUS_PROJECT_ID="your-project-id"')
    print('  export NOSTRADAMUS_MASTER_KEY="your-master-key"')
    print('  export NOSTRADAMUS_WRITE_KEY="your-write-key"')
    print('  export NOSTRADAMUS_READ_KEY="your-read-key"')
    exit(1)

print("🌱 Nostradamus IoTO SDK - Soil Data Example")
print("=" * 60)


# ═════════════════════════════════════════════════════════════
# Step 1: Create Soil Collection
# ═════════════════════════════════════════════════════════════

print("\n📦 Step 1: Create Soil Collection")
print("-" * 40)

collection_id = None

with NostradamusClient(api_key=MASTER_KEY) as master_client:
    try:
        collection = master_client.collections.create(
            project_id=PROJECT_ID,
            name="sensors",
            description="Soil monitoring data",
            tags=["soil", "agriculture", "sensors"],
            collection_schema={
                "key": "SOIL_001",
                "timestamp": "2025-06-17T10:30:00Z",
                "soil_moisture": 45.2,
                "ph_level": 6.8,
                "temperature": 18.5,
                "nitrogen": 45.0,
                "phosphorus": 12.5,
                "potassium": 180.0,
                "battery_level": 87.3,
            },
        )
        collection_id = collection.collection_id
        print("✅ Collection created successfully!")
        print(collection)

    except APIError as e:
        if e.status_code == 409:
            print("⚠️  Collection 'sensors' already exists, finding it...")
            collections = master_client.collections.list(PROJECT_ID)
            for coll in collections:
                if coll.collection_name == "sensors":
                    collection_id = coll.collection_id
                    print(f"✅ Found existing collection: {collection_id}")
                    break
            if not collection_id:
                print("❌ Could not find existing 'sensors' collection")
                exit(1)
        else:
            print(f"Failed to create collection: {e}")
            exit(1)


# ═════════════════════════════════════════════════════════════
# Step 2: Generate and Send Soil Data
# ═════════════════════════════════════════════════════════════

print("\n📤 Step 2: Generate and Send Data")
print("-" * 40)


def generate_soil_data(num_sensors=3, num_readings=24):
    """Generate soil sensor data."""
    data = []
    base_time = datetime.now() - timedelta(hours=24)

    for sensor_num in range(1, num_sensors + 1):
        sensor_id = f"SOIL_{sensor_num:03d}"

        for hour in range(num_readings):
            timestamp = base_time + timedelta(hours=hour)

            reading = {
                "key": sensor_id,
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                "soil_moisture": round(random.uniform(30, 60), 1),
                "ph_level": round(random.uniform(6.0, 7.5), 1),
                "temperature": round(random.uniform(15, 25), 1),
                "nitrogen": round(random.uniform(30, 60), 1),
                "phosphorus": round(random.uniform(8, 20), 1),
                "potassium": round(random.uniform(120, 220), 1),
                "battery_level": round(random.uniform(70, 100), 1),
            }
            data.append(reading)

    return data


soil_data = generate_soil_data(num_sensors=3, num_readings=24)

with NostradamusClient(api_key=WRITE_KEY) as write_client:
    try:
        write_client.data.send(
            project_id=PROJECT_ID,
            collection_id=collection_id,
            data=soil_data,
        )
        print(f"✅ Sent {len(soil_data)} records")
    except APIError as e:
        print(f"Failed to send data: {e}")


# ═════════════════════════════════════════════════════════════
# Step 3: Query Data with Filters
# ═════════════════════════════════════════════════════════════

print("\n📥 Step 3: Query Data")
print("-" * 40)

with NostradamusClient(api_key=READ_KEY) as read_client:
    # Get all data
    print("\n📥 Getting all data...")
    all_data = read_client.data.get(
        project_id=PROJECT_ID,
        collection_id=collection_id,
    )
    print(all_data)

    # Get limited data
    print("\n📥 Getting limited data (14 records)...")
    limit_data = read_client.data.get(
        project_id=PROJECT_ID,
        collection_id=collection_id,
        limit=14,
    )
    print(limit_data)

    # Get ordered data with specific attributes
    print("\n📥 Getting temperature data ordered descending...")
    order_data = read_client.data.get(
        project_id=PROJECT_ID,
        collection_id=collection_id,
        attributes=["key", "temperature"],
        order_by='{"field": "temperature", "order": "desc"}',
    )
    print(order_data)

    # Filter by specific sensor
    print("\n🔍 Filter by sensor SOIL_001...")
    sensor_filter = [
        {
            "property_name": "key",
            "operator": "eq",
            "property_value": "SOIL_001",
        }
    ]
    sensor_data = read_client.data.get(
        project_id=PROJECT_ID,
        collection_id=collection_id,
        filters=sensor_filter,
    )
    print(sensor_data)

    # Get high moisture readings
    print("\n💧 Filter for high moisture (>45%)...")
    moisture_filter = [
        {
            "property_name": "soil_moisture",
            "operator": "gt",
            "property_value": 45,
        }
    ]
    high_moisture = read_client.data.get(
        project_id=PROJECT_ID,
        collection_id=collection_id,
        filters=moisture_filter,
    )
    print(high_moisture)

    # Complex filter - low moisture AND low battery
    print("\n⚠️ Filter for low moisture AND low battery...")
    complex_filter = [
        {
            "property_name": "soil_moisture",
            "operator": "lt",
            "property_value": 35,
        },
        {
            "property_name": "battery_level",
            "operator": "lt",
            "property_value": 80,
        },
    ]
    alert_data = read_client.data.get(
        project_id=PROJECT_ID,
        collection_id=collection_id,
        filters=complex_filter,
    )
    print(alert_data)


# ═════════════════════════════════════════════════════════════
# Step 4: Get Statistics
# ═════════════════════════════════════════════════════════════

print("\n📈 Step 4: Get Statistics")
print("-" * 40)

with NostradamusClient(api_key=READ_KEY) as read_client:
    # Average moisture
    print("\n📈 Average soil moisture...")
    try:
        avg_moisture = read_client.data.statistics(
            project_id=PROJECT_ID,
            collection_id=collection_id,
            attribute="soil_moisture",
            operation="avg",
        )
        print(f"✅ avg for soil_moisture: {avg_moisture}")
    except APIError as e:
        print(f"Failed to get statistics: {e}")

    # Maximum temperature
    print("\n📈 Maximum temperature...")
    try:
        max_temp = read_client.data.statistics(
            project_id=PROJECT_ID,
            collection_id=collection_id,
            attribute="temperature",
            operation="max",
        )
        print(f"✅ max for temperature: {max_temp}")
    except APIError as e:
        print(f"Failed to get statistics: {e}")

    # Minimum battery level (filtered by SOIL_001)
    print("\n📈 Minimum battery level (SOIL_001)...")
    try:
        min_battery = read_client.data.statistics(
            project_id=PROJECT_ID,
            collection_id=collection_id,
            attribute="battery_level",
            operation="min",
        )
        print(f"✅ min for battery_level: {min_battery}")
    except APIError as e:
        print(f"Failed to get statistics: {e}")

    # Distinct sensor keys
    print("\n📈 Distinct sensor keys...")
    try:
        distinct_keys = read_client.data.statistics(
            project_id=PROJECT_ID,
            collection_id=collection_id,
            attribute="key",
            operation="distinct",
        )
        print(f"✅ distinct for key: {distinct_keys}")
    except APIError as e:
        print(f"Failed to get statistics: {e}")


# ═════════════════════════════════════════════════════════════
# Step 5: Delete Specific Data
# ═════════════════════════════════════════════════════════════

print("\n🗑️  Step 5: Delete Data")
print("-" * 40)

with NostradamusClient(api_key=MASTER_KEY) as master_client:
    # Show data before deletion
    print("\n📥 SOIL_001 data before deletion:")
    before = master_client.data.get(
        project_id=PROJECT_ID,
        collection_id=collection_id,
        attributes=["key", "timestamp"],
        order_by='{"field": "timestamp", "order": "asc"}',
        filters=[
            {
                "property_name": "key",
                "operator": "eq",
                "property_value": "SOIL_001",
            }
        ],
    )
    print(before)

    # Delete SOIL_001 data for first 12 hours
    from_time = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    to_time = (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"\n🗑️  Deleting SOIL_001 from {from_time} to {to_time}...")
    try:
        result = master_client.data.delete(
            project_id=PROJECT_ID,
            collection_id=collection_id,
            key="SOIL_001",
            timestamp_from=from_time,
            timestamp_to=to_time,
        )
        print(f"✅ Data deleted successfully: {result.get('message', 'OK')}")
    except APIError as e:
        print(f"Failed to delete data: {e}")

    # Show data after deletion
    print("\n📥 SOIL_001 data after deletion:")
    after = master_client.data.get(
        project_id=PROJECT_ID,
        collection_id=collection_id,
        attributes=["key", "timestamp"],
        order_by='{"field": "timestamp", "order": "asc"}',
        filters=[
            {
                "property_name": "key",
                "operator": "eq",
                "property_value": "SOIL_001",
            }
        ],
    )
    print(after)


# ═════════════════════════════════════════════════════════════
# Step 6: Cleanup
# ═════════════════════════════════════════════════════════════

print("\n🧹 Step 6: Cleanup")
print("-" * 40)

with NostradamusClient(api_key=MASTER_KEY) as master_client:
    try:
        master_client.collections.delete(
            project_id=PROJECT_ID,
            collection_id=collection_id,
        )
        print("✅ Collection 'sensors' deleted successfully!")
    except APIError as e:
        print(f"Failed to delete collection: {e}")

print("\n" + "=" * 60)
print("✨ Demo complete!")
print("=" * 60)
