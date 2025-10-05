# SnapTrade Robinhood Integration Setup Guide

## Step 1: Get SnapTrade Credentials

1. **Register for SnapTrade**: Go to [https://snaptrade.com/register](https://snaptrade.com/register)
2. **Create Account**: Sign up and verify your email
3. **Get API Credentials**: From your dashboard, you'll get:
   - `SNAPTRADE_CLIENT_ID` - Your unique client identifier
   - `SNAPTRADE_CONSUMER_KEY` - Your secret API key (keep this secure!)

## Step 2: Create Environment File

Create `/Users/vedant/Desktop/pokefin/python_backend/.env` with:

```bash
# Required for SnapTrade
SNAPTRADE_CLIENT_ID=your_actual_client_id_here
SNAPTRADE_CONSUMER_KEY=your_actual_consumer_key_here

# Other required keys
OPENAI_API_KEY=your_openai_api_key_here
FINANCIAL_DATASETS_API_KEY=your_financial_datasets_api_key_here
EXA_API_KEY=your_exa_api_key_here
```

## Step 3: Test the Integration

1. **Start the backend**:
   ```bash
   cd /Users/vedant/Desktop/pokefin/python_backend
   source venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8788
   ```

2. **Start the frontend**:
   ```bash
   cd /Users/vedant/Desktop/pokefin/server
   node index.js
   ```

3. **Test the connection flow**:
   - Visit: http://localhost:8787
   - Click "Connect Robinhood"
   - Follow the SnapTrade connection flow

## Step 4: Verify Integration

The system will:
- Create a SnapTrade user for each connection
- Generate connection portal URLs
- Handle OAuth2 callbacks
- Fetch portfolio data (positions, balances, transactions)
- Integrate with research recommendations

## Current Status

✅ **SnapTrade SDK**: Installed (v11.0.139)  
✅ **Client Code**: Ready in `snaptrade_client.py`  
✅ **Frontend UI**: Connection modal ready  
✅ **Backend API**: Endpoints configured  
⏳ **Credentials**: Need to be added to `.env`  

## What Works After Setup

1. **Portfolio Analysis**: Real-time positions and balances
2. **Trade History**: Past transactions and performance
3. **Research Integration**: Personalized recommendations based on holdings
4. **FIRE Calculations**: Portfolio-based retirement planning
5. **Risk Assessment**: Portfolio-level risk analysis

## Troubleshooting

### "Invalid login link" Error
- Check your SnapTrade credentials in `.env`
- Ensure `SNAPTRADE_CLIENT_ID` and `SNAPTRADE_CONSUMER_KEY` are correct
- Verify your SnapTrade account is active

### Connection Flow Issues
- Check browser console for errors
- Verify redirect URI is set correctly
- Ensure backend is running on port 8788

### Portfolio Data Not Loading
- Check SnapTrade dashboard for connected accounts
- Verify user has granted necessary permissions
- Check backend logs for API errors

## Next Steps

Once credentials are set up:
1. Test the complete connection flow
2. Verify portfolio data fetching
3. Integrate with research recommendations
4. Add portfolio-based FIRE calculations
5. Test with real Robinhood accounts
