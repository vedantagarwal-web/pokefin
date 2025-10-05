# SnapTrade API Setup Guide

## Current Issue
The "Invalid login link" error occurs because the current SnapTrade credentials are invalid/expired:
- `SNAPTRADE_CLIENT_ID=ORTHOGONAL-TEST-QBIVI`
- `SNAPTRADE_CONSUMER_KEY=vhWibfnB90jttzrqeLENrKiuvkTY7PDOuQ4gvEylpJVJtQwARq`

## Solution: Get Valid SnapTrade Credentials

### Step 1: Register for SnapTrade API Access
1. Go to [snaptrade.com/register](https://snaptrade.com/register)
2. Create an account and verify your email
3. Access your dashboard to get API credentials

### Step 2: Get Your Credentials
From your SnapTrade dashboard, you'll get:
- **Client ID**: Your unique client identifier
- **Consumer Key**: Your secret API key (keep this secure!)

### Step 3: Update Environment Variables
Update your `.env` file with the new credentials:

```bash
# Replace with your actual SnapTrade credentials
SNAPTRADE_CLIENT_ID=your_actual_client_id_here
SNAPTRADE_CONSUMER_KEY=your_actual_consumer_key_here
```

### Step 4: Restart the Backend
```bash
# Kill existing backend
pkill -f "uvicorn.*main:app"

# Restart the system
./start-full-system.sh
```

## Testing with Alpaca Paper Trading

As recommended in the [SnapTrade docs](https://docs.snaptrade.com/demo/getting-started):

1. **Create Alpaca Paper Account**: Sign up at [alpaca.markets](https://alpaca.markets)
2. **Get Paper Trading Credentials**: Use Alpaca's paper trading environment
3. **Connect via SnapTrade**: Select "Alpaca Paper" as the institution in SnapTrade's Connection Portal

## Current Demo Mode Features

While waiting for valid credentials, the system provides:

✅ **Demo Mode**: Connection flow simulation  
✅ **Error Detection**: Clear credential validation  
✅ **Mock Portfolio**: Sample data for testing  
✅ **FIRE Calculations**: Demo scenarios  
✅ **Portfolio Analysis**: Mock data for development  

## API Integration Status

- ✅ **SnapTrade SDK**: Properly configured (v11.0.139)
- ✅ **Authentication**: Correct API methods implemented
- ✅ **User Registration**: `register_snap_trade_user` working
- ✅ **Connection Portal**: `login_snap_trade_user` with trading enabled
- ✅ **Error Handling**: Invalid credential detection
- ❌ **Credentials**: Need valid Client ID and Consumer Key

## Next Steps

1. **Get SnapTrade Credentials**: Register and obtain valid API access
2. **Test with Alpaca Paper**: Use paper trading for safe testing
3. **Enable Trading**: Connection portal already configured with `connection_type="trade"`
4. **Production Ready**: Once credentials are valid, full brokerage integration will work

## Resources

- [SnapTrade Getting Started](https://docs.snaptrade.com/demo/getting-started)
- [SnapTrade API Reference](https://docs.snaptrade.com/api-reference/overview)
- [Alpaca Paper Trading](https://alpaca.markets)
- [SnapTrade Registration](https://snaptrade.com/register)
