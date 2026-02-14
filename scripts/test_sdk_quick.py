#!/usr/bin/env python3
"""
Quick SDK Test Script

Test the complete workflow:
1. Create collection → 2. Send data → 3. Query data → 4. Delete collection

Set environment variables before running:
    export NOSTRADAMUS_PROJECT_ID="your-project-id"
    export NOSTRADAMUS_MASTER_KEY="your-master-key"
    export NOSTRADAMUS_WRITE_KEY="your-write-key"
    export NOSTRADAMUS_READ_KEY="your-read-key"

Then run:
    python test_sdk_quick.py
"""

import os
import sys
import time
from datetime import datetime

from nostradamus_ioto_sdk import NostradamusClient
from nostradamus_ioto_sdk.exceptions import APIError


def check_env_vars():
    """Check required environment variables."""
    # Defaults are provided, so we don't need to check
    # Just return True and let the script use defaults if env vars not set
    return True


def main():
    """Run quick SDK test."""

    print("🧪 Nostradamus IoTO SDK - Quick Test")
    print("=" * 60)

    # Check environment variables
    if not check_env_vars():
        sys.exit(1)

    project_id = os.getenv("NOSTRADAMUS_PROJECT_ID")
    master_key = os.getenv("NOSTRADAMUS_MASTER_KEY")
    write_key = os.getenv("NOSTRADAMUS_WRITE_KEY")
    read_key = os.getenv("NOSTRADAMUS_READ_KEY")

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
        sys.exit(1)

    collection_id = None
    total_start = time.time()

    try:
        # =============================================================
        # Step 1: Create Collection
        # =============================================================

        print("\n[1/4] Creating test collection...")
        step_start = time.time()

        with NostradamusClient(api_key=master_key) as client:
            collection = client.collections.create(
                project_id=project_id,
                name=f"sdk_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description="SDK quick test collection",
                tags=["test", "sdk"],
                collection_schema={
                    "key": "SENSOR_001",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "temperature": 25.5,
                    "humidity": 60.0,
                },
            )

            collection_id = collection.collection_id
            print(f"✅ Collection created: {collection.collection_name}")
            print(f"   ID: {collection_id}")

        step_duration = time.time() - step_start
        print(f"   ⏱️  Time: {step_duration:.2f}s")

        # =============================================================
        # Step 2: Send Data
        # =============================================================

        print("\n[2/4] Sending test data...")
        step_start = time.time()

        test_data = [
            {
                "key": "SENSOR_001",
                "timestamp": datetime.now().isoformat(),
                "temperature": 25.5,
                "humidity": 60.0,
            },
            {
                "key": "SENSOR_002",
                "timestamp": datetime.now().isoformat(),
                "temperature": 26.3,
                "humidity": 58.5,
            },
            {
                "key": "SENSOR_003",
                "timestamp": datetime.now().isoformat(),
                "temperature": 24.8,
                "humidity": 62.1,
            },
        ]

        with NostradamusClient(api_key=write_key) as client:
            client.data.send(
                project_id=project_id, collection_id=collection_id, data=test_data
            )
            print(f"✅ Sent {len(test_data)} data records")

        step_duration = time.time() - step_start
        print(f"   ⏱️  Time: {step_duration:.2f}s")

        # =============================================================
        # Step 3: Query Data
        # =============================================================

        print("\n[3/4] Querying data...")
        step_start = time.time()

        with NostradamusClient(api_key=read_key) as client:
            # 3.1: Get all data
            all_data = client.data.get(
                project_id=project_id, collection_id=collection_id
            )
            print(f"✅ Retrieved {len(all_data)} total records")

            # 3.2: Get filtered data
            filtered_data = client.data.get(
                project_id=project_id,
                collection_id=collection_id,
                filters=[
                    {
                        "property_name": "key",
                        "operator": "eq",
                        "property_value": "SENSOR_001",
                    }
                ],
            )
            print(f"✅ Retrieved {len(filtered_data)} filtered records (SENSOR_001)")

            # 3.3: Get statistics
            try:
                avg_temp = client.data.statistics(
                    project_id=project_id,
                    collection_id=collection_id,
                    attribute="temperature",
                    operation="avg",
                )
                print(f"✅ Average temperature: {avg_temp}")
            except Exception as e:
                print(f"⚠️  Statistics not available: {e}")

        step_duration = time.time() - step_start
        print(f"   ⏱️  Time: {step_duration:.2f}s")

        # =============================================================
        # Step 4: Delete Collection
        # =============================================================

        print("\n[4/4] Deleting test collection...")
        step_start = time.time()

        with NostradamusClient(api_key=master_key) as client:
            client.collections.delete(
                project_id=project_id, collection_id=collection_id
            )
            print("✅ Collection deleted")

        step_duration = time.time() - step_start
        print(f"   ⏱️  Time: {step_duration:.2f}s")

        total_duration = time.time() - total_start
        print("\n" + "=" * 60)
        print("✨ All tests passed successfully!")
        print(f"⏱️  Total time: {total_duration:.2f}s")
        print("=" * 60)

        return 0

    except APIError as e:
        print(f"\n❌ API Error: {e}")

        # Cleanup: Try to delete collection if it was created
        if collection_id:
            print("\n🧹 Attempting cleanup...")
            try:
                with NostradamusClient(api_key=master_key) as client:
                    client.collections.delete(project_id, collection_id)
                    print("✅ Cleanup successful")
            except Exception as cleanup_err:
                print(
                    f"⚠️  Cleanup failed - you may need to manually delete the collection: {cleanup_err}"
                )

        return 1

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
