#!/usr/bin/env python3
"""
Test Real SnapTrade Integration
Test with actual SnapTrade credentials
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

# Set environment variables for testing
os.environ["SNAPTRADE_CLIENT_ID"] = "ORTHOGONAL-TEST-QBIVI"
os.environ["SNAPTRADE_CONSUMER_KEY"] = "vhWibfnB90jttzrqeLENrKiuvkTY7PDOuQ4gvEylpJVJtQwARq"

from python_backend.services.snaptrade_client import SnapTradeClient

async def test_real_snaptrade():
    """Test SnapTrade integration with real credentials"""
    print("🧪 Testing Real SnapTrade Integration...")
    print(f"Client ID: {os.environ['SNAPTRADE_CLIENT_ID']}")
    print(f"Consumer Key: {os.environ['SNAPTRADE_CONSUMER_KEY'][:20]}...")
    
    # Initialize client
    client = SnapTradeClient()
    
    # Test user creation
    print("\n1. Testing user creation...")
    import time
    unique_user_id = f"test_user_real_{int(time.time())}"
    user_result = await client.create_user(unique_user_id)
    print(f"✅ User creation result: {user_result}")
    
    if user_result.get("mock"):
        print("❌ Still using mock data - credentials may be invalid")
        return
    
    user_id = user_result["userId"]
    user_secret = user_result["userSecret"]
    
    # Test connection portal URL
    print("\n2. Testing connection portal URL...")
    portal_result = await client.get_connection_portal_url(
        user_id=user_id,
        user_secret=user_secret,
        redirect_uri="http://localhost:8787/callback"
    )
    print(f"✅ Portal URL result: {portal_result}")
    
    if portal_result.get("mock"):
        print("❌ Still using mock data for portal URL")
        return
    
    print(f"🔗 Connection URL: {portal_result.get('redirect_url')}")
    
    # Test portfolio summary (will use mock data until account is connected)
    print("\n3. Testing portfolio summary...")
    portfolio = await client.get_portfolio_summary(user_id, user_secret)
    print(f"✅ Portfolio summary: {portfolio.get('summary', 'Mock data - no connected accounts')}")
    
    print("\n🎉 SnapTrade integration test completed!")
    print("\n📋 Next steps:")
    print("1. Add credentials to python_backend/.env file:")
    print("   SNAPTRADE_CLIENT_ID=ORTHOGONAL-TEST-QBIVI")
    print("   SNAPTRADE_CONSUMER_KEY=vhWibfnB90jttzrqeLENrKiuvkTY7PDOuQ4gvEylpJVJtQwARq")
    print("2. Restart the backend server")
    print("3. Test the connection flow in the web UI")
    print("4. Connect a real Robinhood account")

if __name__ == "__main__":
    asyncio.run(test_real_snaptrade())
