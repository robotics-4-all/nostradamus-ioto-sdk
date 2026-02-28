#!/usr/bin/env python3
"""
Nostradamus IoTO SDK - Soil Monitoring Example

This example demonstrates the complete workflow:
1. Create a collection with schema
2. Generate and send sensor data
3. Query data with various filters
4. Get statistics
5. Delete specific data
6. Clean up collection

This matches the nostradamus_ioto_api_example_demonstration.py but uses the SDK.
"""

import os
import random
import time
from datetime import datetime, timedelta

from nostradamus_ioto_sdk import NostradamusClient
from nostradamus_ioto_sdk.exceptions import APIError


def generate_soil_data(num_sensors=3, num_readings=24):
    """Generate soil sensor data.

    Args:
        num_sensors: Number of soil sensors to simulate
        num_readings: Number of readings per sensor

    Returns:
        List of sensor readings
    """
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


def main():
    """Run the soil monitoring example."""

    total_start = time.time()

    # Get credentials from environment variables
    project_id = os.getenv("NOSTRADAMUS_PROJECT_ID")
    master_key = os.getenv("NOSTRADAMUS_MASTER_KEY")
    write_key = os.getenv("NOSTRADAMUS_WRITE_KEY")
    read_key = os.getenv("NOSTRADAMUS_READ_KEY")

    # Validate credentials
    if not all([project_id, master_key, write_key, read_key]):
        print("❌ Error: Missing required environment variables!")
        print()
        print("Please set the following environment variables:")
        print("  - NOSTRADAMUS_PROJECT_ID")
        print("  - NOSTRADAMUS_MASTER_KEY")
        print("  - NOSTRADAMUS_WRITE_KEY")
        print("  - NOSTRADAMUS_READ_KEY")
        print()
        print("Example:")
        print("  export NOSTRADAMUS_PROJECT_ID='your-project-id'")
        print("  export NOSTRADAMUS_MASTER_KEY='your-master-key'")
        print("  export NOSTRADAMUS_WRITE_KEY='your-write-key'")
        print("  export NOSTRADAMUS_READ_KEY='your-read-key'")
        print()
        return

    print("🌱 Nostradamus IoTO SDK - Soil Monitoring Example")
    print("=" * 60)

    # ===================================================================
    # Step 1: Create Collection with Schema
    # ===================================================================

    print("\n📦 Step 1: Creating soil sensors collection...")

    collection_id = None
    with NostradamusClient(api_key=master_key) as master_client:
        try:
            collection = master_client.collections.create(
                project_id=project_id,
                name="sensors",
                description="Soil monitoring data",
                tags=["soil", "agriculture", "sensors"],
                collection_schema={
                    "key": "SOIL_001",  # Identifying key
                    "timestamp": "2025-06-17T10:30:00Z",  # Timestamp
                    "soil_moisture": 45.2,  # Soil moisture %
                    "ph_level": 6.8,  # pH level
                    "temperature": 18.5,  # Temperature °C
                    "nitrogen": 45.0,  # Nitrogen ppm
                    "phosphorus": 12.5,  # Phosphorus ppm
                    "potassium": 180.0,  # Potassium ppm
                    "battery_level": 87.3,  # Battery %
                },
            )

            collection_id = collection.collection_id
            print("✅ Collection created successfully!")
            print(f"   Collection ID: {collection_id}")
            print(f"   Name: {collection.collection_name}")
            print(f"   Description: {collection.description}")

        except APIError as e:
            # Check if collection already exists (409 Conflict)
            if e.status_code == 409:
                print("⚠️  Collection 'sensors' already exists, finding it...")
                # List collections and find the one named "sensors"
                collections = master_client.collections.list(project_id)
                for coll in collections:
                    if coll.collection_name == "sensors":
                        collection_id = coll.collection_id
                        print(f"✅ Using existing collection: {coll.collection_name}")
                        print(f"   Collection ID: {collection_id}")
                        break

                if not collection_id:
                    print("❌ Could not find existing 'sensors' collection")
                    return
            else:
                print(f"❌ Failed to create collection: {e}")
                return

        if not collection_id:
            print("❌ No collection available")
            return

    # ===================================================================
    # Step 2: Generate and Send Data
    # ===================================================================

    print("\n📤 Step 2: Generating and sending soil sensor data...")
    print("   Generating data for 3 sensors with 24 readings each...")

    soil_data = generate_soil_data(num_sensors=3, num_readings=24)
    print(f"   Generated {len(soil_data)} total readings")

    with NostradamusClient(api_key=write_key) as write_client:
        try:
            write_client.data.send(
                project_id=project_id, collection_id=collection_id, data=soil_data
            )
            print(f"✅ Sent {len(soil_data)} records successfully!")

        except APIError as e:
            print(f"❌ Failed to send data: {e}")

    # ===================================================================
    # Step 3: Query Data with Various Filters
    # ===================================================================

    print("\n📥 Step 3: Querying data with various filters...")

    with NostradamusClient(api_key=read_key) as read_client:
        # 3.1: Get all data
        print("\n   3.1: Getting all data...")
        try:
            all_data = read_client.data.get(
                project_id=project_id, collection_id=collection_id
            )
            print(f"   ✅ Retrieved {len(all_data)} total records")

        except APIError as e:
            print(f"   ❌ Failed to get data: {e}")

        # 3.2: Get limited data
        print("\n   3.2: Getting limited data (14 records)...")
        try:
            limited_data = read_client.data.get(
                project_id=project_id, collection_id=collection_id, limit=14
            )
            print(f"   ✅ Retrieved {len(limited_data)} records")

        except APIError as e:
            print(f"   ❌ Failed to get limited data: {e}")

        # 3.3: Get ordered data with specific attributes
        print("\n   3.3: Getting temperature data ordered by descending...")
        try:
            ordered_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                attributes=["key", "temperature"],
                order_by='{"field": "temperature", "order": "desc"}',
            )
            if isinstance(ordered_data, list) and ordered_data:
                print(f"   ✅ Retrieved {len(ordered_data)} records")
                if "temperature" in ordered_data[0]:
                    print(f"   Highest temperature: {ordered_data[0]['temperature']}°C")
                    print(f"   Lowest temperature: {ordered_data[-1]['temperature']}°C")
            else:
                print(f"   ✅ Retrieved data: {ordered_data}")

        except APIError as e:
            print(f"   ❌ Failed to get ordered data: {e}")

        # 3.4: Filter by specific sensor (SOIL_001)
        print("\n   3.4: 🔍 Filtering data for sensor SOIL_001...")
        try:
            sensor_filter = [
                {"property_name": "key", "operator": "eq", "property_value": "SOIL_001"}
            ]
            sensor_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=sensor_filter,
            )
            print(f"   ✅ Retrieved {len(sensor_data)} records for SOIL_001")

        except APIError as e:
            print(f"   ❌ Failed to filter by sensor: {e}")

        # 3.5: Filter for high moisture readings
        print("\n   3.5: 💧 Filtering for high moisture (>45%)...")
        try:
            moisture_filter = [
                {
                    "property_name": "soil_moisture",
                    "operator": "gt",
                    "property_value": 45,
                }
            ]
            high_moisture = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=moisture_filter,
            )
            print(f"   ✅ Found {len(high_moisture)} high moisture readings")

        except APIError as e:
            print(f"   ❌ Failed to filter by moisture: {e}")

        # 3.6: Complex filter - low moisture AND low battery
        print("\n   3.6: ⚠️  Filtering for low moisture AND low battery...")
        try:
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
                project_id=project_id,
                collection_id=collection_id,
                filters=complex_filter,
            )
            print(f"   ✅ Found {len(alert_data)} readings needing attention")

        except APIError as e:
            print(f"   ❌ Failed to apply complex filter: {e}")

    # ===================================================================
    # Step 4: Get Statistics
    # ===================================================================

    print("\n📈 Step 4: Getting statistics...")

    with NostradamusClient(api_key=read_key) as read_client:
        # 4.1: Average soil moisture
        print("\n   4.1: Calculating average soil moisture...")
        try:
            avg_moisture = read_client.data.statistics(
                project_id=project_id,
                collection_id=collection_id,
                attribute="soil_moisture",
                operation="avg",
            )
            print(f"   ✅ Average soil moisture: {avg_moisture}")

        except APIError as e:
            print(f"   ❌ Failed to get average: {e}")

        # 4.2: Maximum temperature
        print("\n   4.2: Finding maximum temperature...")
        try:
            max_temp = read_client.data.statistics(
                project_id=project_id,
                collection_id=collection_id,
                attribute="temperature",
                operation="max",
            )
            print(f"   ✅ Maximum temperature: {max_temp}")

        except APIError as e:
            print(f"   ❌ Failed to get maximum: {e}")

        # 4.3: Minimum battery level (all sensors)
        print("\n   4.3: Finding minimum battery level...")
        try:
            min_battery = read_client.data.statistics(
                project_id=project_id,
                collection_id=collection_id,
                attribute="battery_level",
                operation="min",
            )
            print(f"   ✅ Minimum battery level: {min_battery}%")

        except APIError as e:
            print(f"   ❌ Failed to get minimum: {e}")

        # 4.4: Distinct sensor keys
        print("\n   4.4: Getting distinct sensor keys...")
        try:
            distinct_keys = read_client.data.statistics(
                project_id=project_id,
                collection_id=collection_id,
                attribute="key",
                operation="distinct",
            )
            print(f"   ✅ Distinct sensors: {distinct_keys}")

        except APIError as e:
            print(f"   ❌ Failed to get distinct values: {e}")

    # ===================================================================
    # Step 5: Delete Specific Data
    # ===================================================================

    print("\n🗑️  Step 5: Deleting specific data...")

    # Use a time range that matches the generated data (last 24 hours)
    from_time = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")

    print("   Deleting first 12 hours of data for key 'SOIL_001'...")
    print(
        f"   Time range: {from_time[:19]} to "
        f"{(datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%S')}"
    )

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            # First, count records before deletion
            before_data = master_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=[
                    {"property_name": "key", "operator": "eq", "value": "SOIL_001"}
                ],
            )
            print(f"   Records before deletion: {len(before_data)}")

            # Delete first 12 hours of data
            result = master_client.data.delete(
                project_id=project_id,
                collection_id=collection_id,
                key="SOIL_001",
                timestamp_from=from_time,
                timestamp_to=(datetime.now() - timedelta(hours=12)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
            )
            print(f"✅ Data deleted: {result.get('message', 'Success')}")

            # Verify deletion by querying again
            after_data = master_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=[
                    {"property_name": "key", "operator": "eq", "value": "SOIL_001"}
                ],
            )
            print(f"   Records after deletion: {len(after_data)}")
            print(
                f"   Deleted approximately {len(before_data) - len(after_data)} records"
            )

        except APIError as e:
            print(f"❌ Failed to delete data: {e}")

    # ===================================================================
    # Step 6: Cleanup - Delete Collection
    # ===================================================================

    print("\n🧹 Step 6: Cleaning up - deleting collection...")

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            master_client.collections.delete(
                project_id=project_id, collection_id=collection_id
            )
            print("✅ Collection 'sensors' deleted successfully!")

        except APIError as e:
            print(f"❌ Failed to delete collection: {e}")

    total_duration = time.time() - total_start

    print("\n" + "=" * 60)
    print("✨ Soil monitoring example completed successfully!")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
