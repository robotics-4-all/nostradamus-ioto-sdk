"""Data ingestion example for IoT sensors.

This example shows how to efficiently send sensor data to the IoTO platform.
"""

import os
import random
import time
from datetime import datetime

from nostradamus_ioto_sdk import NostradamusClient


def generate_sensor_reading(sensor_id: str) -> dict:
    """Generate a simulated sensor reading.

    Args:
        sensor_id: Sensor identifier

    Returns:
        Dictionary with sensor data
    """
    return {
        "sensor_id": sensor_id,
        "temperature": round(20 + random.uniform(-5, 10), 2),
        "humidity": round(50 + random.uniform(-20, 30), 2),
        "pressure": round(1013 + random.uniform(-10, 10), 2),
        "timestamp": datetime.utcnow().isoformat(),
    }


def main():
    """Run data ingestion example."""
    api_key = os.getenv("NOSTRADAMUS_API_KEY")
    if not api_key:
        print("Error: Please set NOSTRADAMUS_API_KEY environment variable")
        return

    with NostradamusClient(api_key=api_key) as client:
        print("=" * 60)
        print("IoT Data Ingestion Example")
        print("=" * 60)

        # Setup: Create project and collection
        print("\n[Setup] Creating project and collection...")
        project = client.projects.create(
            name="IoT Sensor Network", description="Network of environmental sensors"
        )
        print(f"Created project: {project.name}")

        collection = client.collections.create(
            project.id,
            name="Environmental Data",
            description="Temperature, humidity, and pressure readings",
        )
        print(f"Created collection: {collection.name}")

        # Simulate multiple sensors
        sensor_ids = ["sensor-001", "sensor-002", "sensor-003", "sensor-004"]

        # Example 1: Send individual readings
        print(
            f"\n[Example 1] Sending individual readings from {len(sensor_ids)} sensors..."
        )
        for sensor_id in sensor_ids:
            reading = generate_sensor_reading(sensor_id)
            client.data.send(project.id, collection.id, reading)
            print(f"  Sent reading from {sensor_id}: {reading['temperature']}°C")
            time.sleep(0.1)  # Small delay to simulate real-time

        # Example 2: Batch sending (more efficient)
        print("\n[Example 2] Batch sending multiple readings...")
        batch_size = 10
        batch = []

        for _ in range(batch_size):
            sensor_id = random.choice(sensor_ids)
            reading = generate_sensor_reading(sensor_id)
            batch.append(reading)

        client.data.send(project.id, collection.id, batch)
        print(f"  Sent batch of {len(batch)} readings")

        # Example 3: Continuous ingestion simulation
        print("\n[Example 3] Simulating continuous data ingestion...")
        print("  Collecting data for 5 seconds...")
        start_time = time.time()
        readings_sent = 0
        batch_buffer = []

        while time.time() - start_time < 5:
            # Generate reading from random sensor
            sensor_id = random.choice(sensor_ids)
            reading = generate_sensor_reading(sensor_id)
            batch_buffer.append(reading)

            # Send batch if interval reached
            if len(batch_buffer) >= 5:  # Or use time-based batching
                client.data.send(project.id, collection.id, batch_buffer)
                readings_sent += len(batch_buffer)
                print(
                    f"  Sent batch of {len(batch_buffer)} readings (total: {readings_sent})"
                )
                batch_buffer = []

            time.sleep(0.5)  # Simulate sensor reading interval

        # Send remaining readings
        if batch_buffer:
            client.data.send(project.id, collection.id, batch_buffer)
            readings_sent += len(batch_buffer)
            print(f"  Sent final batch of {len(batch_buffer)} readings")

        print(f"\n  Total readings sent: {readings_sent}")

        # Query recent data
        print("\n[Query] Retrieving recent data...")
        recent_data = client.data.get(project.id, collection.id, limit=10)
        print(
            f"  Retrieved {len(recent_data) if isinstance(recent_data, list) else 1} recent readings"
        )

        # Get statistics
        print("\n[Statistics] Getting data statistics...")
        try:
            stats = client.data.statistics(
                project.id,
                collection.id,
                field="temperature",
                operation="avg",
            )
            print(f"  Average temperature: {stats}")
        except Exception as e:
            print(f"  Statistics not available: {e}")

        # Cleanup
        print("\n[Cleanup] Removing test data...")
        client.collections.delete(project.id, collection.id)
        client.projects.delete(project.id)
        print("  Cleanup complete")

        print("\n" + "=" * 60)
        print("Data ingestion example completed!")
        print("=" * 60)


if __name__ == "__main__":
    main()
