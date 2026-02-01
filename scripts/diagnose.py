#!/usr/bin/env python3
"""Diagnostic script to test SDK and API connection."""

import os

import httpx

from nostradamus_ioto_sdk import NostradamusClient

print("=" * 70)
print("NOSTRADAMUS IOTO SDK - DIAGNOSTIC TOOL")
print("=" * 70)
print()

# Check credentials
api_key = os.getenv("NOSTRADAMUS_API_KEY")
username = os.getenv("NOSTRADAMUS_USERNAME")
password = os.getenv("NOSTRADAMUS_PASSWORD")

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
url = "https://nostradamus-ioto.issel.ee.auth.gr/api/v1/organization/nostradamus"

if api_key:
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

    # Try to get organization
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
    print()
    print("You can now use the SDK:")
    print("  .venv/bin/python test_client.py")

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
