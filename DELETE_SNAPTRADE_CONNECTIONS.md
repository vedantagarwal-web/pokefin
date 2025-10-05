# How to Delete SnapTrade Connections

You've hit the SnapTrade free trial limit of 5 connections. Here's how to delete existing connections to free up slots.

## Quick Method (Recommended)

### Option 1: Use the Deletion Tool

1. **Run the deletion script:**
   ```bash
   cd /Users/vedant/Desktop/pokefin
   python3 delete_snaptrade_connection.py
   ```

2. **Enter your SnapTrade credentials when prompted**

3. **Select which connection to delete**

### Option 2: Use the API Directly

1. **List your connections:**
   ```bash
   curl -X POST "http://localhost:8788/api/snaptrade/connections" \
     -H "Content-Type: application/json" \
     -d '{"userId": "YOUR_USER_ID", "userSecret": "YOUR_USER_SECRET"}'
   ```

2. **Delete a specific connection:**
   ```bash
   curl -X POST "http://localhost:8788/api/snaptrade/connections/delete" \
     -H "Content-Type: application/json" \
     -d '{"userId": "YOUR_USER_ID", "userSecret": "YOUR_USER_SECRET", "authorizationId": "AUTHORIZATION_ID"}'
   ```

## Manual Method

### Via SnapTrade Dashboard

1. Go to [app.snaptrade.com](https://app.snaptrade.com)
2. Log in with your SnapTrade account
3. Navigate to "Connected Accounts" or "Brokerages"
4. Find the connection you want to remove
5. Click "Disconnect" or "Remove"

### Via SnapTrade API Documentation

1. Go to [docs.snaptrade.com](https://docs.snaptrade.com)
2. Find the "Connections" section
3. Use the "Force disable connection" endpoint:
   ```
   POST https://api.snaptrade.com/api/v1/authorizations/{authorizationId}/disable
   ```

## What You Need

- **User ID**: Your SnapTrade user ID
- **User Secret**: Your SnapTrade user secret
- **Authorization ID**: The ID of the specific connection to delete

## Finding Your Credentials

Your SnapTrade credentials are stored in your browser's localStorage:

1. Open your browser's developer tools (F12)
2. Go to the "Application" or "Storage" tab
3. Find "Local Storage" for localhost:8787
4. Look for:
   - `snaptrade_user_id`
   - `snaptrade_user_secret`

## After Deleting

Once you delete a connection:

1. ✅ A slot becomes available in your free trial
2. ✅ You can create new connections
3. ✅ The deleted connection is permanently removed

## Troubleshooting

### "Invalid userID or userSecret"
- Make sure you're using the correct credentials
- Check that the backend is running on localhost:8788

### "Connection not found"
- The authorization ID might be incorrect
- List connections first to get the correct ID

### "Unauthorized"
- Your SnapTrade API credentials might be invalid
- Check your .env file for correct SNAPTRADE_CLIENT_ID and SNAPTRADE_CONSUMER_KEY

## Free Trial Limits

- **Maximum connections**: 5
- **Reset period**: Monthly
- **Upgrade**: Contact SnapTrade for higher limits

## Need Help?

If you're still having issues:

1. Check the terminal logs for detailed error messages
2. Verify your SnapTrade API credentials
3. Contact SnapTrade support for account-specific issues
