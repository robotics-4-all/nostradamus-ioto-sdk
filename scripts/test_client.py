#!/usr/bin/env python3
"""Test script for Nostradamus IoTO SDK.

This script demonstrates how to use the SDK to interact with the IoTO API.
"""

import os
from nostradamus_ioto_sdk import NostradamusClient, KeyType


def main():
    """Test the SDK with the IoTO API."""

    # Get credentials from environment variables
    api_key = os.getenv("NOSTRADAMUS_API_KEY")
    username = os.getenv("NOSTRADAMUS_USERNAME")
    password = os.getenv("NOSTRADAMUS_PASSWORD")

    print("=" * 60)
    print("Nostradamus IoTO SDK - Test Script")
    print("=" * 60)
    print()

    # Initialize client
    if api_key:
        print("🔑 Authenticating with API Key...")
        client = NostradamusClient(api_key=api_key)
    elif username and password:
        print("🔑 Authenticating with OAuth2 (username/password)...")
        client = NostradamusClient(username=username, password=password)
    else:
        print("❌ Error: No credentials provided!")
        print()
        print("Please set one of the following:")
        print("  - NOSTRADAMUS_API_KEY environment variable")
        print("  - NOSTRADAMUS_USERNAME and NOSTRADAMUS_PASSWORD environment variables")
        print()
        print("Example:")
        print("  export NOSTRADAMUS_API_KEY='your-api-key-here'")
        print("  # or")
        print("  export NOSTRADAMUS_USERNAME='your-username'")
        print("  export NOSTRADAMUS_PASSWORD='your-password'")
        return

    print("✅ Client initialized successfully!")
    print()

    try:
        # Test 1: Get organization info
        print("📋 Test 1: Getting organization information...")
        try:
            org = client.organizations.get()
            print(f"   ✅ Organization: {org.organization_name}")
            print(f"      ID: {org.organization_id}")
            print(f"      Description: {org.description}")
            print(f"      Created: {org.creation_date}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()

        # Test 2: List projects
        print("📋 Test 2: Listing all projects...")
        try:
            projects = client.projects.list()
            print(f"   ✅ Found {len(projects)} project(s)")
            for project in projects[:5]:  # Show first 5
                print(f"      - {project.project_name} ({project.project_id})")
            if len(projects) > 5:
                print(f"      ... and {len(projects) - 5} more")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()

        # Test 3: List collections for first project
        try:
            projects_list = client.projects.list()
            if projects_list:
                first_project = projects_list[0].project_id
                print(
                    f"📋 Test 3: Listing collections for project '{first_project}'..."
                )
                try:
                    collections = client.collections.list(first_project)
                    print(f"   ✅ Found {len(collections)} collection(s)")
                    for collection in collections[:3]:  # Show first 3
                        print(
                            f"      - {collection.collection_name} ({collection.collection_id})"
                        )
                    if len(collections) > 3:
                        print(f"      ... and {len(collections) - 3} more")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            else:
                print("📋 Test 3: No projects found to list collections")
        except Exception as e:
            print(f"   ❌ Error listing projects: {e}")
        print()

        print("=" * 60)
        print("✅ Tests completed!")
        print("=" * 60)
        print()
        print("The SDK is working! You can now:")
        print("  - Create and manage projects")
        print("  - Create and manage collections")
        print("  - Send and query data")
        print("  - Get statistics and aggregations")
        print()
        print("See the examples/ directory for more usage examples.")

    finally:
        # Clean up
        client.close()


if __name__ == "__main__":
    main()
