#!/usr/bin/env python3
"""
SnapTrade Connection Management Tool
Helps you list and delete SnapTrade connections to free up slots
"""

import asyncio
import os
import sys
from python_backend.services.snaptrade_client import SnapTradeClient

async def main():
    print("🔧 SnapTrade Connection Management Tool")
    print("=" * 50)
    
    # Initialize client
    client = SnapTradeClient()
    
    # Get user credentials from environment or prompt
    user_id = os.getenv("SNAPTRADE_USER_ID")
    user_secret = os.getenv("SNAPTRADE_USER_SECRET")
    
    if not user_id or not user_secret:
        print("❌ SnapTrade credentials not found in environment variables.")
        print("\nTo use this tool, set the following environment variables:")
        print("export SNAPTRADE_USER_ID='your_user_id'")
        print("export SNAPTRADE_USER_SECRET='your_user_secret'")
        print("\nOr run this script with credentials:")
        print("SNAPTRADE_USER_ID='your_id' SNAPTRADE_USER_SECRET='your_secret' python manage_snaptrade_connections.py")
        return
    
    print(f"👤 User ID: {user_id}")
    print(f"🔑 User Secret: {user_secret[:10]}...")
    print()
    
    try:
        # List current connections
        print("📋 Listing current connections...")
        connections = await client.list_connections(user_id, user_secret)
        
        if not connections:
            print("✅ No connections found. You can create new connections.")
            return
        
        print(f"\n📊 Found {len(connections)} connection(s):")
        print("-" * 60)
        
        for i, conn in enumerate(connections, 1):
            print(f"{i}. Authorization ID: {conn['authorization_id']}")
            print(f"   Broker: {conn['broker']}")
            print(f"   Status: {conn['status']}")
            print(f"   Created: {conn['created_at']}")
            print()
        
        # Ask user which connection to delete
        if len(connections) > 0:
            print("🗑️  To delete a connection, enter its number (1, 2, etc.)")
            print("   Or press Enter to exit without deleting anything.")
            
            try:
                choice = input("\nEnter connection number to delete: ").strip()
                
                if choice and choice.isdigit():
                    index = int(choice) - 1
                    
                    if 0 <= index < len(connections):
                        conn_to_delete = connections[index]
                        auth_id = conn_to_delete['authorization_id']
                        
                        print(f"\n⚠️  Are you sure you want to delete connection {auth_id}?")
                        print(f"   Broker: {conn_to_delete['broker']}")
                        confirm = input("   Type 'DELETE' to confirm: ").strip()
                        
                        if confirm == 'DELETE':
                            print(f"\n🗑️  Deleting connection {auth_id}...")
                            result = await client.delete_connection(user_id, user_secret, auth_id)
                            
                            if result['success']:
                                print(f"✅ Successfully deleted connection {auth_id}")
                                print("🎉 You can now create new connections!")
                            else:
                                print(f"❌ Failed to delete connection: {result.get('error', 'Unknown error')}")
                        else:
                            print("❌ Deletion cancelled.")
                    else:
                        print("❌ Invalid connection number.")
                else:
                    print("👋 Exiting without deleting anything.")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Error listing connections: {e}")

if __name__ == "__main__":
    asyncio.run(main())
