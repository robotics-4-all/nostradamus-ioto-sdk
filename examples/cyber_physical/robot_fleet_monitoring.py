#!/usr/bin/env python3
"""
Nostradamus IoTO SDK - Robot Fleet Monitoring Example

Demonstrates warehouse robot fleet monitoring with sensor fusion:
1. Create a collection with schema
2. Generate and send robot telemetry data
3. Query data with operational filters
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

ROBOT_PROFILES = {
    "AGV_001": {"type": "agv", "max_vel": 3.0, "max_payload": 500},
    "AGV_002": {"type": "agv", "max_vel": 3.0, "max_payload": 500},
    "ARM_001": {"type": "robotic_arm", "max_vel": 1.0, "max_payload": 25},
    "ARM_002": {"type": "robotic_arm", "max_vel": 1.0, "max_payload": 25},
    "DRONE_001": {"type": "inspection_drone", "max_vel": 5.0, "max_payload": 5},
}

TASK_PREFIXES = {
    "agv": "MOVE",
    "robotic_arm": "PICK",
    "inspection_drone": "INSPECT",
}


def generate_robot_data(num_readings=24):
    """Generate warehouse robot fleet telemetry data.

    Args:
        num_readings: Hourly readings per robot over 24h

    Returns:
        List of sensor readings
    """
    data = []
    base_time = datetime.now() - timedelta(hours=24)

    for robot_id, profile in ROBOT_PROFILES.items():
        rtype = profile["type"]
        max_vel = profile["max_vel"]
        max_payload = profile["max_payload"]
        battery = 95.0 + random.uniform(-5, 5)
        task_counter = random.randint(1, 50)

        for hour in range(num_readings):
            timestamp = base_time + timedelta(hours=hour)

            is_active = 6 <= timestamp.hour <= 22
            has_error = random.random() < 0.03

            if rtype == "agv":
                pos_x = random.uniform(5, 95)
                pos_y = random.uniform(5, 45)
                pos_z = 0.0
            elif rtype == "robotic_arm":
                pos_x = 20.0 + random.uniform(-2, 2)
                pos_y = 15.0 + random.uniform(-2, 2)
                pos_z = random.uniform(0, 2)
            else:
                pos_x = random.uniform(0, 100)
                pos_y = random.uniform(0, 50)
                pos_z = random.uniform(2, 8)

            velocity = (
                random.uniform(0.5, max_vel) if is_active else random.uniform(0, 0.3)
            )

            battery -= random.uniform(0.5, 2.0)
            if not is_active:
                battery += random.uniform(0.5, 1.5)
            battery = max(20, min(100, battery))

            payload = random.uniform(0, max_payload) if is_active else 0.0

            task_prefix = TASK_PREFIXES[rtype]
            task_counter += 1 if is_active else 0
            task_id = f"{task_prefix}_{task_counter:04d}"

            if has_error:
                task_status = "error"
            elif is_active:
                task_status = random.choice(
                    ["executing", "executing", "completed", "queued"]
                )
            else:
                task_status = "queued"

            motor_temp = 30 + velocity * 10 + random.uniform(-3, 5)

            reading = {
                "key": robot_id,
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                "robot_type": rtype,
                "pos_x_m": round(pos_x, 2),
                "pos_y_m": round(pos_y, 2),
                "pos_z_m": round(pos_z, 2),
                "velocity_ms": round(velocity, 2),
                "orientation_deg": random.randint(0, 359),
                "battery_pct": round(battery, 1),
                "motor_temperature_c": round(min(75, max(25, motor_temp)), 1),
                "payload_kg": round(payload, 1),
                "task_id": task_id,
                "task_status": task_status,
                "obstacle_distance_m": round(random.uniform(0.1, 10.0), 2),
                "lidar_points_count": random.randint(1000, 50000),
                "network_latency_ms": round(random.uniform(5, 100), 1),
                "cpu_usage_pct": round(random.uniform(10, 95), 1),
                "error_code": random.randint(1, 5) if has_error else 0,
            }
            data.append(reading)

    return data


def main():
    """Run the robot fleet monitoring example."""
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

    print("🤖 Nostradamus IoTO SDK - Robot Fleet Monitoring Example")
    print("=" * 60)

    # Step 1: Create Collection
    print("\n📦 Step 1: Creating robot fleet collection...")
    collection_id = None

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            collection = master_client.collections.create(
                project_id=project_id,
                name="robot_fleet",
                description="Warehouse robot fleet telemetry",
                tags=["robots", "warehouse", "cyber-physical"],
                collection_schema={
                    "key": "AGV_001",
                    "timestamp": "2025-06-17T10:30:00Z",
                    "robot_type": "agv",
                    "pos_x_m": 50.0,
                    "pos_y_m": 25.0,
                    "pos_z_m": 0.0,
                    "velocity_ms": 2.1,
                    "orientation_deg": 180,
                    "battery_pct": 85.0,
                    "motor_temperature_c": 42.0,
                    "payload_kg": 250.0,
                    "task_id": "MOVE_0042",
                    "task_status": "executing",
                    "obstacle_distance_m": 3.5,
                    "lidar_points_count": 25000,
                    "network_latency_ms": 15.0,
                    "cpu_usage_pct": 55.0,
                    "error_code": 0,
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
                    if coll.collection_name == "robot_fleet":
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
    print("\n📤 Step 2: Generating robot telemetry data...")
    print("   5 robots × 24 hourly readings...")

    robot_data = generate_robot_data(num_readings=24)
    print(f"   Generated {len(robot_data)} readings")

    with NostradamusClient(api_key=write_key) as write_client:
        try:
            write_client.data.send(
                project_id=project_id,
                collection_id=collection_id,
                data=robot_data,
            )
            print(f"✅ Sent {len(robot_data)} records")
        except APIError as e:
            print(f"❌ Failed to send: {e}")

    # Step 3: Query Data
    print("\n📥 Step 3: Querying with operational filters...")

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

        print("\n   3.2: Filter by AGV_001...")
        try:
            agv_filter = [
                {
                    "property_name": "key",
                    "operator": "eq",
                    "property_value": "AGV_001",
                }
            ]
            agv_data = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=agv_filter,
            )
            print(f"   ✅ {len(agv_data)} records for AGV_001")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.3: ⚠️ Error states (error_code != 0)...")
        try:
            error_filter = [
                {
                    "property_name": "error_code",
                    "operator": "gt",
                    "property_value": 0,
                }
            ]
            errors = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=error_filter,
            )
            print(f"   ✅ Found {len(errors)} error events")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.4: 🔋 Low battery (< 30%)...")
        try:
            batt_filter = [
                {
                    "property_name": "battery_pct",
                    "operator": "lt",
                    "property_value": 30,
                }
            ]
            low_batt = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=batt_filter,
            )
            print(f"   ✅ Found {len(low_batt)} low battery readings")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.5: 🖥️ Performance bottleneck (CPU > 80 AND latency > 50ms)...")
        try:
            perf_filter = [
                {
                    "property_name": "cpu_usage_pct",
                    "operator": "gt",
                    "property_value": 80,
                },
                {
                    "property_name": "network_latency_ms",
                    "operator": "gt",
                    "property_value": 50,
                },
            ]
            bottlenecks = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=perf_filter,
            )
            print(f"   ✅ Found {len(bottlenecks)} bottleneck events")
        except APIError as e:
            print(f"   ❌ {e}")

        print("\n   3.6: Battery ranking (most depleted)...")
        try:
            ranked = read_client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                attributes=["key", "battery_pct", "robot_type"],
                order_by='{"field": "battery_pct", "order": "asc"}',
                limit=5,
            )
            if isinstance(ranked, list) and ranked:
                top = ranked[0]
                print(f"   ✅ Lowest: {top.get('battery_pct')}% ({top.get('key')})")
        except APIError as e:
            print(f"   ❌ {e}")

    # Step 4: Statistics
    print("\n📈 Step 4: Getting statistics...")

    with NostradamusClient(api_key=read_key) as read_client:
        for label, attr, op in [
            ("Avg battery", "battery_pct", "avg"),
            ("Max motor temp", "motor_temperature_c", "max"),
            ("Min obstacle dist", "obstacle_distance_m", "min"),
            ("Distinct robots", "key", "distinct"),
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
    print("   Removing first 12h for AGV_001...")

    with NostradamusClient(api_key=master_key) as master_client:
        try:
            result = master_client.data.delete(
                project_id=project_id,
                collection_id=collection_id,
                key="AGV_001",
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
    print("✨ Robot fleet monitoring example completed!")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
