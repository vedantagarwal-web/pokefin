#!/usr/bin/env python3
"""
Test SnapTrade Integration
Run this to test the SnapTrade integration with mock data
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_backend'))

from python_backend.services.snaptrade_client import SnapTradeClient

async def test_snaptrade_integration():
    """Test SnapTrade integration with mock data"""
    print("🧪 Testing SnapTrade Integration...")
    
    # Initialize client
    client = SnapTradeClient()
    
    # Test user creation
    print("\n1. Testing user creation...")
    user_result = await client.create_user("test_user_123")
    print(f"✅ User created: {user_result}")
    
    user_id = user_result["userId"]
    user_secret = user_result["userSecret"]
    
    # Test connection portal URL
    print("\n2. Testing connection portal URL...")
    portal_result = await client.get_connection_portal_url(
        user_id=user_id,
        user_secret=user_secret,
        redirect_uri="http://localhost:8787/callback"
    )
    print(f"✅ Portal URL: {portal_result}")
    
    # Test portfolio summary
    print("\n3. Testing portfolio summary...")
    portfolio = await client.get_portfolio_summary(user_id, user_secret)
    print(f"✅ Portfolio summary: {portfolio['summary']}")
    
    # Test account positions
    print("\n4. Testing account positions...")
    positions = await client.get_account_positions(user_id, user_secret)
    print(f"✅ Positions: {len(positions)} found")
    for pos in positions[:3]:  # Show first 3
        print(f"   - {pos['symbol']}: {pos['shares']} shares @ ${pos['current_price']}")
    
    # Test trade history
    print("\n5. Testing trade history...")
    trades = await client.get_account_transactions(user_id, user_secret, portfolio['accounts'][0]['id'])
    print(f"✅ Trade history: {len(trades)} transactions found")
    for trade in trades[:3]:  # Show first 3
        print(f"   - {trade['action']} {trade['symbol']}: {trade['quantity']} shares @ ${trade['price']}")
    
    # Test account balances
    print("\n6. Testing account balances...")
    balances = await client.get_account_balances(user_id, user_secret, portfolio['accounts'][0]['id'])
    print(f"✅ Account balances: ${balances['total_equity']:,.2f} total equity")
    
    print("\n🎉 SnapTrade integration test completed successfully!")
    print("\n📋 Next steps:")
    print("1. Register for SnapTrade account at https://snaptrade.com/register")
    print("2. Get your SNAPTRADE_CLIENT_ID and SNAPTRADE_CONSUMER_KEY")
    print("3. Add them to python_backend/.env file")
    print("4. Restart the backend server")
    print("5. Test with real Robinhood accounts")

if __name__ == "__main__":
    asyncio.run(test_snaptrade_integration())
