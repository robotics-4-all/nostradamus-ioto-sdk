#!/usr/bin/env python3
"""Diagnostic script to test SDK and API connection."""

import os
from pathlib import Path

import httpx

from nostradamus_ioto_sdk import NostradamusClient


def _load_dotenv():
    """Load .env file from project root into os.environ (without overwriting)."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key not in os.environ:
                os.environ[key] = value


_load_dotenv()

print("=" * 70)
print("NOSTRADAMUS IOTO SDK - DIAGNOSTIC TOOL")
print("=" * 70)
print()

# Check credentials
api_key = os.getenv("NOSTRADAMUS_API_KEY") or os.getenv("NOSTRADAMUS_MASTER_KEY")
username = os.getenv("NOSTRADAMUS_USERNAME")
password = os.getenv("NOSTRADAMUS_PASSWORD")
project_id = os.getenv("NOSTRADAMUS_PROJECT_ID")

print("1️⃣  Checking Credentials...")
if api_key:
    print(
        f"   ✅ API Key found: {api_key[:15]}...{api_key[-5:]}"
        if len(api_key) > 20
        else f"   ✅ API Key found: {api_key}"
    )
elif username and password:
    print("   ✅ OAuth2 credentials found")
    print(f"      Username: {username}")
else:
    print("   ❌ No credentials found!")
    print()
    print("   Set your credentials:")
    print("   export NOSTRADAMUS_API_KEY='your-api-key'")
    print("   # OR")
    print("   export NOSTRADAMUS_USERNAME='your-username'")
    print("   export NOSTRADAMUS_PASSWORD='your-password'")
    exit(1)

print()
print("2️⃣  Testing Raw API Connection...")

base_url = "https://nostradamus-ioto.issel.ee.auth.gr"
if api_key:
    if project_id:
        url = f"{base_url}/api/v1/projects/{project_id}/collections"
    else:
        url = f"{base_url}/api/v1/organization/nostradamus"
    headers = {"X-API-Key": api_key}
    print("   Making GET request to:")
    print(f"   {url}")
    print(f"   With header: X-API-Key: {api_key[:10]}...")

    try:
        with httpx.Client() as client:
            response = client.get(url, headers=headers, timeout=30.0)
            print(f"   Response: {response.status_code}")

            if response.status_code == 200:
                print("   ✅ SUCCESS! API key is valid!")
                data = response.json()
                if project_id:
                    count = len(data) if isinstance(data, list) else "unknown"
                    print(f"   Collections found: {count}")
                else:
                    print(f"   Organization: {data.get('organization_name', 'N/A')}")
            elif response.status_code == 401:
                print("   ❌ AUTHENTICATION FAILED!")
                print(f"   Response: {response.text}")
                print()
                print("   This means:")
                print("   - Your API key might be invalid or expired")
                print("   - You might need to use OAuth2 instead")
                print(
                    "   - Check your credentials at: https://nostradamus-ioto.issel.ee.auth.gr"
                )
            else:
                print(f"   ⚠️  Unexpected response: {response.status_code}")
                print(f"   Body: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        print("   Check your internet connection and the API URL")

elif username and password:
    print("   Testing OAuth2 login...")
    print("   POST to: https://nostradamus-ioto.issel.ee.auth.gr/api/v1/token")

    try:
        with httpx.Client() as client:
            response = client.post(
                "https://nostradamus-ioto.issel.ee.auth.gr/api/v1/token",
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0,
            )
            print(f"   Response: {response.status_code}")

            if response.status_code == 200:
                print("   ✅ SUCCESS! OAuth2 login successful!")
                data = response.json()
                token = data.get("access_token", "")
                print(f"   Got access token: {token[:20]}...")
            else:
                print("   ❌ AUTHENTICATION FAILED!")
                print(f"   Response: {response.text}")
                print()
                print("   Check your username and password")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")

print()
print("3️⃣  Testing SDK...")
try:
    if api_key:
        client = NostradamusClient(api_key=api_key)
    else:
        client = NostradamusClient(username=username, password=password)

    print("   SDK client created successfully")

    if project_id:
        print(f"   Listing collections for project {project_id[:8]}...")
        collections = client.collections.list(project_id)
        print("   ✅ SUCCESS!")
        print(f"   Collections found: {len(collections)}")
        for col in collections[:5]:
            print(f"     - {col.collection_name}")
        if len(collections) > 5:
            print(f"     ... and {len(collections) - 5} more")
    else:
        print("   Attempting to get organization info...")
        org = client.organizations.get()
        print("   ✅ SUCCESS!")
        print(f"   Organization: {org.organization_name}")
        print(f"   ID: {org.organization_id}")

    client.close()

    print()
    print("=" * 70)
    print("✅ ALL TESTS PASSED! SDK IS WORKING CORRECTLY!")
    print("=" * 70)

except Exception as e:
    print(f"   ❌ SDK Error: {e}")
    print()
    print("=" * 70)
    print("⚠️  SDK TEST FAILED")
    print("=" * 70)
    print()
    print("Possible issues:")
    print("1. Your API key might be invalid")
    print("2. Your OAuth2 credentials might be wrong")
    print("3. The API might be down")
    print()
    print("Please:")
    print("- Verify your credentials")
    print("- Check the API documentation")
    print("- Contact support if the issue persists")
