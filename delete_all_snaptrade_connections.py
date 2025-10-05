#!/usr/bin/env python3
"""
Delete ALL SnapTrade Connections Tool
⚠️  WARNING: This will delete ALL your SnapTrade connections!
"""

import requests
import json
import sys

def main():
    print("🗑️  DELETE ALL SnapTrade Connections Tool")
    print("=" * 50)
    print("⚠️  WARNING: This will delete ALL your SnapTrade connections!")
    print("   You won't be able to access your portfolio data after this.")
    print("   Make sure this is what you want to do!")
    print()
    
    # Get credentials from user
    user_id = input("Enter your SnapTrade User ID: ").strip()
    user_secret = input("Enter your SnapTrade User Secret: ").strip()
    
    if not user_id or not user_secret:
        print("❌ User ID and User Secret are required!")
        return
    
    # API base URL
    api_base = "http://localhost:8788/api/snaptrade"
    
    try:
        # Step 1: List connections
        print("\n📋 Getting list of your connections...")
        list_response = requests.post(f"{api_base}/connections", json={
            "userId": user_id,
            "userSecret": user_secret
        })
        
        if list_response.status_code != 200:
            print(f"❌ Failed to list connections: {list_response.status_code}")
            print(list_response.text)
            return
        
        connections_data = list_response.json()
        
        if not connections_data.get("success"):
            print(f"❌ Error listing connections: {connections_data.get('error', 'Unknown error')}")
            return
        
        connections = connections_data.get("connections", [])
        
        if not connections:
            print("✅ No connections found. Nothing to delete!")
            return
        
        print(f"\n📊 Found {len(connections)} connection(s) to delete:")
        print("-" * 60)
        
        for i, conn in enumerate(connections, 1):
            print(f"{i}. Authorization ID: {conn['authorization_id']}")
            print(f"   Broker: {conn['broker']}")
            print(f"   Status: {conn['status']}")
            print(f"   Created: {conn['created_at']}")
            print()
        
        # Step 2: Final confirmation
        print("⚠️  FINAL WARNING: This will delete ALL connections listed above!")
        print("   This action cannot be undone.")
        print("   You will lose access to all connected brokerage accounts.")
        
        confirm = input("\nType 'DELETE ALL' to confirm deletion: ").strip()
        
        if confirm != 'DELETE ALL':
            print("❌ Deletion cancelled.")
            return
        
        # Step 3: Delete all connections
        print(f"\n🗑️  Deleting {len(connections)} connection(s)...")
        
        deleted_count = 0
        failed_count = 0
        
        for i, conn in enumerate(connections, 1):
            auth_id = conn['authorization_id']
            broker = conn['broker']
            
            print(f"\n[{i}/{len(connections)}] Deleting {broker} connection...")
            
            delete_response = requests.post(f"{api_base}/connections/delete", json={
                "userId": user_id,
                "userSecret": user_secret,
                "authorizationId": auth_id
            })
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                if delete_data.get("success"):
                    print(f"   ✅ Successfully deleted {broker} connection")
                    deleted_count += 1
                else:
                    print(f"   ❌ Failed to delete {broker}: {delete_data.get('error', 'Unknown error')}")
                    failed_count += 1
            else:
                print(f"   ❌ Failed to delete {broker}: HTTP {delete_response.status_code}")
                failed_count += 1
        
        # Step 4: Summary
        print(f"\n" + "=" * 50)
        print("🎉 DELETION COMPLETE!")
        print(f"✅ Successfully deleted: {deleted_count} connection(s)")
        if failed_count > 0:
            print(f"❌ Failed to delete: {failed_count} connection(s)")
        print()
        
        if deleted_count > 0:
            print("🎊 You now have free slots available!")
            print("   You can create new SnapTrade connections.")
            print("   Go to your app and click 'Connect Robinhood' to create a new connection.")
        else:
            print("😞 No connections were deleted.")
            print("   Check the error messages above for details.")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the backend is running on localhost:8788")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
