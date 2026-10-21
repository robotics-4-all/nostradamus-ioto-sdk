"""Basic usage examples for Nostradamus IoTO SDK.

This example demonstrates the basic operations you can perform with the SDK.
"""

import os

from _load_env import load_dotenv

from nostradamus_ioto_sdk import NostradamusClient

load_dotenv()


def main():
    """Run basic SDK examples."""
    # Get API key from environment variable
    api_key = os.getenv("NOSTRADAMUS_API_KEY")
    if not api_key:
        print("Error: Please set NOSTRADAMUS_API_KEY environment variable")
        return

    # Create client (automatically manages connection)
    with NostradamusClient(api_key=api_key) as client:
        print("=" * 50)
        print("Nostradamus IoTO SDK - Basic Usage Examples")
        print("=" * 50)

        # 1. Get organization info
        print("\n1. Getting organization information...")
        org = client.organizations.get()
        print(f"   Organization ID: {org.organization_id}")
        print(f"   Organization Name: {org.organization_name}")

        # 2. List all projects
        print("\n2. Listing all projects...")
        projects = client.projects.list()
        print(f"   Found {len(projects)} projects")
        for project in projects:
            print(f"   - {project.project_name} (ID: {project.project_id})")

        # 3. Create a new project
        print("\n3. Creating a new project...")
        new_project = client.projects.create(
            name="Example Project",
            description="Created via SDK example script",
        )
        print(
            f"   Created project: {new_project.project_name} (ID: {new_project.project_id})"
        )

        # 4. List collections in the new project
        print(f"\n4. Listing collections in project {new_project.project_id}...")
        collections = client.collections.list(new_project.project_id)
        print(f"   Found {len(collections)} collections")

        # 5. Create a new collection
        print("\n5. Creating a new collection...")
        new_collection = client.collections.create(
            project_id=new_project.project_id,
            name="Sensor Data",
            description="Temperature and humidity readings",
            collection_schema={
                "temperature": "float",
                "humidity": "float",
                "location": "string",
            },
        )
        print(f"   Created collection: {new_collection.collection_name}")

        # 6. Send data to the collection
        print("\n6. Sending data to collection...")
        data_point = {
            "temperature": 25.5,
            "humidity": 60.0,
            "location": "Room A",
        }
        client.data.send(
            new_project.project_id, new_collection.collection_id, data_point
        )
        print(f"   Sent data: {data_point}")

        # 7. Send batch data
        print("\n7. Sending batch data...")
        batch_data = [
            {"temperature": 26.0, "humidity": 58.0},
            {"temperature": 25.8, "humidity": 59.0},
            {"temperature": 25.3, "humidity": 61.0},
        ]
        client.data.send(
            new_project.project_id, new_collection.collection_id, batch_data
        )
        print(f"   Sent {len(batch_data)} data points")

        # 8. Query data
        print("\n8. Querying data from collection...")
        retrieved_data = client.data.get(
            new_project.project_id, new_collection.collection_id, limit=5
        )
        print(
            f"   Retrieved "
            f"{len(retrieved_data) if isinstance(retrieved_data, list) else 1}"
            f" data points"
        )

        # 9. Update project
        print("\n9. Updating project...")
        updated_project = client.projects.update(
            new_project.project_id, description="Updated via SDK example script"
        )
        print(f"   Updated project: {updated_project.project_name}")

        # 10. Clean up - Delete collection and project
        print("\n10. Cleaning up...")
        client.collections.delete(new_project.project_id, new_collection.collection_id)
        print(f"   Deleted collection: {new_collection.collection_name}")

        client.projects.delete(new_project.project_id)
        print(f"   Deleted project: {new_project.project_name}")

        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("=" * 50)


if __name__ == "__main__":
    main()
