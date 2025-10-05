# SnapTrade Callback Flow Fix

## 🎯 Problem Identified

After connecting a Robinhood account via SnapTrade, the "Return to App" button wasn't updating the UI. The system remained in the "Connect Robinhood" state instead of showing the connected status.

**Root Cause**: The callback page was trying to access `sessionStorage` from a different window/tab, but `sessionStorage` is not shared between windows. The user credentials were being lost during the SnapTrade portal flow.

## ✅ Fixes Applied

### 1. Fixed Callback Page Credential Handling (`server/index.js`)

**Before**: 
```javascript
// Try to get stored user details from sessionStorage (set during connection flow)
const userId = sessionStorage.getItem('snaptrade_user_id') || 'connected_user';
const userSecret = sessionStorage.getItem('snaptrade_user_secret') || 'connected_secret';
```

**After**:
```javascript
// Get user credentials from URL parameters or backend response
const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('userId') || ${JSON.stringify(result.user_id)} || 'connected_user';
const userSecret = urlParams.get('userSecret') || ${JSON.stringify(result.user_secret)} || 'connected_secret';
```

### 2. Enhanced Connection Status Check (`js/app.js`)

**Before**: Simple check for any accounts
```javascript
if (result.success && result.accounts && result.accounts.length > 0) {
```

**After**: Proper handling of different connection states
```javascript
// Check if we have real accounts (not mock accounts)
const hasRealAccounts = result.success && result.accounts && result.accounts.length > 0 && 
  !(result.accounts.length === 1 && result.accounts[0].id === 'mock_account_1');

if (hasRealAccounts) {
  // Show connected with real accounts
} else if (result.success && result.accounts && result.accounts.length === 0) {
  // Show connected but no brokerage accounts yet
} else {
  // Clear invalid connection
}
```

### 3. Added Auto-Refresh on Return (`js/app.js`)

Added automatic connection status refresh when returning from SnapTrade portal:
```javascript
// Function to refresh connection status
async function refreshConnectionStatus() {
  console.log('Refreshing connection status...');
  const checkBtn = document.getElementById('checkConnection');
  if (checkBtn) {
    checkBtn.click();
  }
}

// Check if we're returning from a SnapTrade callback
if (window.location.search.includes('snaptrade_callback') || 
    window.location.hash.includes('snaptrade_callback')) {
  console.log('Detected SnapTrade callback return, refreshing status...');
  setTimeout(refreshConnectionStatus, 2000);
}
```

## 🔧 How It Works Now

### Complete Flow:
1. **User clicks "Connect Robinhood"** → Creates SnapTrade user with real credentials
2. **Portal URL generated** → Includes `userId` and `userSecret` as URL parameters
3. **User connects brokerage** → In SnapTrade portal (separate window/tab)
4. **SnapTrade redirects** → Back to `/callback` with credentials in URL
5. **Callback page stores credentials** → In `localStorage` for persistence
6. **Auto-refresh triggered** → Connection status updated automatically
7. **UI updates** → Shows connected status with real account data

### Key Improvements:
- ✅ Credentials persist across window boundaries
- ✅ Automatic status refresh on return
- ✅ Proper handling of different connection states
- ✅ Real account detection (vs mock accounts)
- ✅ Better error handling and user feedback

## 🧪 Testing Results

### Backend Tests:
```bash
# User creation works
curl "http://localhost:8788/api/snaptrade/connect"
# Returns: user_id, user_secret, portal_url

# Callback handling works  
curl "http://localhost:8788/api/snaptrade/callback?userId=test&userSecret=test&authorizationId=123" -X POST
# Returns: success=true, credentials extracted, accounts verified
```

### Expected User Experience:
1. Click "Connect Robinhood" → Portal opens
2. Connect brokerage account → "Connection successful" message
3. Click "Return to App" → UI automatically updates
4. See connected status → Real portfolio data available

## 📝 Files Modified

- `server/index.js` - Fixed callback credential handling
- `js/app.js` - Enhanced connection status and auto-refresh

## 🚀 Next Steps

1. **Test with real brokerage account** - Connect actual Robinhood account
2. **Verify portfolio data** - Confirm real account data appears
3. **Test AI integration** - Ensure AI agents can access real data

The SnapTrade integration should now properly persist connections and update the UI after successful brokerage linking! 🎉
