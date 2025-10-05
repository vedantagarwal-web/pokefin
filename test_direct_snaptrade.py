#!/usr/bin/env python3
"""
Test Direct SnapTrade API Calls
Bypass SDK and test direct HTTP requests
"""

import asyncio
import aiohttp
import json
import os

# Set environment variables for testing
os.environ["SNAPTRADE_CLIENT_ID"] = "ORTHOGONAL-TEST-QBIVI"
os.environ["SNAPTRADE_CONSUMER_KEY"] = "vhWibfnB90jttzrqeLENrKiuvkTY7PDOuQ4gvEylpJVJtQwARq"

async def test_direct_snaptrade():
    """Test SnapTrade API with direct HTTP requests"""
    print("🧪 Testing Direct SnapTrade API Calls...")
    
    client_id = os.environ["SNAPTRADE_CLIENT_ID"]
    consumer_key = os.environ["SNAPTRADE_CONSUMER_KEY"]
    
    print(f"Client ID: {client_id}")
    print(f"Consumer Key: {consumer_key[:20]}...")
    
    base_url = "https://api.snaptrade.com/api/v1"
    headers = {
        "Authorization": f"Bearer {consumer_key}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Register user with client_id in query params
    print("\n1. Testing user registration...")
    register_url = f"{base_url}/snapTrade/registerUser"
    params = {
        "clientId": client_id
    }
    
    register_data = {
        "userId": "test_user_direct_123"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                register_url, 
                headers=headers, 
                params=params,
                json=register_data
            ) as response:
                print(f"Status: {response.status}")
                response_text = await response.text()
                print(f"Response: {response_text}")
                
                if response.status == 200:
                    result = await response.json()
                    user_id = result.get("userId")
                    user_secret = result.get("userSecret")
                    print(f"✅ User registered: {user_id}")
                    
                    # Test 2: Get login redirect URI
                    print("\n2. Testing login redirect URI...")
                    login_url = f"{base_url}/snapTrade/listUserAccountOrders"
                    login_params = {
                        "clientId": client_id,
                        "userId": user_id,
                        "userSecret": user_secret
                    }
                    
                    async with session.get(
                        login_url,
                        headers=headers,
                        params=login_params
                    ) as login_response:
                        print(f"Login Status: {login_response.status}")
                        login_text = await login_response.text()
                        print(f"Login Response: {login_text}")
                        
                        if login_response.status == 200:
                            print("✅ Login redirect successful")
                        else:
                            print("❌ Login redirect failed")
                    
                else:
                    print("❌ User registration failed")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_snaptrade())
