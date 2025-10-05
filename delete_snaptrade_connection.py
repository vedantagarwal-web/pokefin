#!/usr/bin/env python3
"""
Quick SnapTrade Connection Deletion Tool
"""

import requests
import json
import sys

def main():
    print("🗑️  SnapTrade Connection Deletion Tool")
    print("=" * 40)
    
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
        print("\n📋 Listing your connections...")
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
            print("✅ No connections found. You can create new connections!")
            return
        
        print(f"\n📊 Found {len(connections)} connection(s):")
        print("-" * 60)
        
        for i, conn in enumerate(connections, 1):
            print(f"{i}. Authorization ID: {conn['authorization_id']}")
            print(f"   Broker: {conn['broker']}")
            print(f"   Status: {conn['status']}")
            print(f"   Created: {conn['created_at']}")
            print()
        
        # Step 2: Ask which connection to delete
        print("🗑️  To delete a connection, enter its number (1, 2, etc.)")
        print("   Or press Enter to exit without deleting anything.")
        
        choice = input("\nEnter connection number to delete: ").strip()
        
        if not choice:
            print("👋 Exiting without deleting anything.")
            return
        
        if not choice.isdigit():
            print("❌ Please enter a valid number.")
            return
        
        index = int(choice) - 1
        
        if not (0 <= index < len(connections)):
            print("❌ Invalid connection number.")
            return
        
        conn_to_delete = connections[index]
        auth_id = conn_to_delete['authorization_id']
        
        # Step 3: Confirm deletion
        print(f"\n⚠️  Are you sure you want to delete connection {auth_id}?")
        print(f"   Broker: {conn_to_delete['broker']}")
        confirm = input("   Type 'DELETE' to confirm: ").strip()
        
        if confirm != 'DELETE':
            print("❌ Deletion cancelled.")
            return
        
        # Step 4: Delete connection
        print(f"\n🗑️  Deleting connection {auth_id}...")
        delete_response = requests.post(f"{api_base}/connections/delete", json={
            "userId": user_id,
            "userSecret": user_secret,
            "authorizationId": auth_id
        })
        
        if delete_response.status_code != 200:
            print(f"❌ Failed to delete connection: {delete_response.status_code}")
            print(delete_response.text)
            return
        
        delete_data = delete_response.json()
        
        if delete_data.get("success"):
            print(f"✅ Successfully deleted connection {auth_id}")
            print("🎉 You can now create new connections!")
        else:
            print(f"❌ Failed to delete connection: {delete_data.get('error', 'Unknown error')}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the backend is running on localhost:8788")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
