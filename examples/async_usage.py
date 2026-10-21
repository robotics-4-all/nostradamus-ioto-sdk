"""Async usage examples for Nostradamus IoTO SDK.

This example demonstrates how to use the async client for concurrent operations.
"""

import asyncio
import os

from _load_env import load_dotenv

from nostradamus_ioto_sdk import AsyncNostradamusClient

load_dotenv()


async def main():
    """Run async SDK examples."""
    # Get API key from environment variable
    api_key = os.getenv("NOSTRADAMUS_API_KEY")
    if not api_key:
        print("Error: Please set NOSTRADAMUS_API_KEY environment variable")
        return

    # Create async client
    async with AsyncNostradamusClient(api_key=api_key) as client:
        print("=" * 50)
        print("Nostradamus IoTO SDK - Async Usage Examples")
        print("=" * 50)

        # Example 1: Concurrent fetching of org and projects
        print("\n1. Fetching organization and projects concurrently...")
        org_task = client.organizations.aget()
        projects_task = client.projects.alist()

        # Wait for both to complete
        org, projects = await asyncio.gather(org_task, projects_task)

        print(f"   Organization: {org.organization_name}")
        print(f"   Projects: {len(projects)} found")

        # Example 2: Create project and wait
        print("\n2. Creating a new project...")
        project = await client.projects.acreate(
            name="Async Example Project", description="Created with async client"
        )
        print(f"   Created: {project.project_name}")

        # Example 3: Create multiple collections concurrently
        print("\n3. Creating multiple collections concurrently...")
        collection_tasks = [
            client.collections.acreate(
                project.project_id,
                name=f"Collection {i}",
                description=f"Collection {i} desc",
                collection_schema={"temperature": "float", "sensor_id": "string"},
            )
            for i in range(1, 4)
        ]

        collections = await asyncio.gather(*collection_tasks)
        print(f"   Created {len(collections)} collections")
        for coll in collections:
            print(f"   - {coll.collection_name}")

        # Example 4: Send data to multiple collections concurrently
        print("\n4. Sending data to multiple collections...")
        data_tasks = [
            client.data.asend(
                project.project_id,
                coll.collection_id,
                {"temperature": 20.0 + i, "sensor_id": f"sensor-{i}"},
            )
            for i, coll in enumerate(collections)
        ]

        await asyncio.gather(*data_tasks)
        print(f"   Sent data to {len(collections)} collections")

        # Example 5: Query data from multiple collections concurrently
        print("\n5. Querying data from collections...")
        query_tasks = [
            client.data.aget(project.project_id, coll.collection_id, limit=10)
            for coll in collections
        ]

        results = await asyncio.gather(*query_tasks)
        print(f"   Retrieved data from {len(results)} collections")

        # Example 6: Cleanup - Delete all collections and project
        print("\n6. Cleaning up...")
        delete_tasks = [
            client.collections.adelete(project.project_id, coll.collection_id)
            for coll in collections
        ]

        await asyncio.gather(*delete_tasks)
        print(f"   Deleted {len(collections)} collections")

        await client.projects.adelete(project.project_id)
        print(f"   Deleted project: {project.project_name}")

        print("\n" + "=" * 50)
        print("All async examples completed successfully!")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
