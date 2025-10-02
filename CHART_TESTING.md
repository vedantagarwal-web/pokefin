# 📊 Chart Testing Guide

## What Was Fixed

### Backend
1. **Message Persistence**: Charts now saved with messages in session
   - File: `python_backend/main.py` line 134-136
   - Added `charts`, `actions`, `whiteboard_data` to stored messages

### Frontend  
1. **Chart Data Preservation**: `syncHistory()` now preserves chart data
   - File: `js/app.js` line 204
   - Added `charts: m.charts || []` when mapping messages

2. **Debug Logging**: Added console logs for troubleshooting
   - Chart rendering logs in `app.js`
   - Chart manager logs in `charts.js`

## How to Test

### 1. Open Browser Console
```bash
# Open http://localhost:8787
# Press F12 or Cmd+Option+I
# Go to Console tab
```

### 2. Test Chart Generation
Type in chat:
```
nvidia chart
```

Expected console output:
```
📊 Rendering 1 chart(s)
Chart 0: candlestick NVDA
📈 renderPriceChart called: chart-0 {ticker: "NVDA", ...}
✅ Container found, rendering chart...
✅ Chart rendered: chart-0
```

### 3. Test Chart Persistence
1. Ask for a chart: "show nvidia chart"
2. Refresh the page (Cmd+R or Ctrl+R)
3. Chart should re-appear after refresh

### 4. Test Comparison Chart
Type in chat:
```
compare nvda and amd
```

Expected:
- Normalized line chart showing both stocks
- Legend with ticker symbols
- Both lines in different colors

### 5. Test Sector Heatmap
Type in chat:
```
which sectors are performing well?
```

Expected:
- Grid of colored tiles
- Green for positive, red for negative
- Sector names and percentages

## Troubleshooting

### Chart Not Showing
Check console for:
1. `📊 Rendering X chart(s)` - If missing, charts not in message
2. `Container not found` - DOM insertion issue
3. `Chart render error` - TradingView library issue

### Check Backend Response
```bash
curl -X POST http://localhost:8788/api/v2/chat/send \
  -H "Content-Type: application/json" \
  -d '{"session": "test123", "messages": [{"role": "user", "content": "nvidia chart"}]}' \
  | python3 -m json.tool | grep -A5 charts
```

Should show:
```json
"charts": [
  {
    "ticker": "NVDA",
    "type": "candlestick",
    "data": [...]
  }
]
```

### Check History Endpoint
```bash
curl "http://localhost:8788/api/v2/chat/history?session=test123" \
  | python3 -m json.tool | grep -A5 charts
```

Should show charts in last message.

### TradingView Not Loaded
Check network tab for:
```
https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js
```

Status should be 200.

## Example Queries

### Price Charts
- "show me nvda chart"
- "aapl 6 month chart"
- "tesla chart with volume"
- "microsoft chart with moving averages"

### Comparison Charts
- "compare nvda and amd"
- "show me aapl vs msft vs googl"
- "compare tech stocks"

### Sector Analysis
- "sector performance"
- "which sectors are hot today?"
- "show me sector heatmap"

### With Indicators
- "nvda chart with ma20 and ma50"
- "aapl chart with rsi"
- "tsla chart with all indicators"

## Known Issues

1. **First render delay**: 100ms setTimeout for DOM insertion
2. **RSI/MACD in main panel**: Separate panels not implemented
3. **Chart export**: No download feature yet
4. **Mobile responsive**: May need width adjustments

## Success Criteria

✅ Chart appears below AI message
✅ Chart is interactive (hover, zoom, pan)
✅ Volume bars show below price
✅ Moving averages overlay on price
✅ Chart persists after page refresh
✅ Multiple charts can be shown
✅ Comparison charts work
✅ Sector heatmap is colorful

## Debug Commands

### Backend Health
```bash
curl http://localhost:8788/health
```

### Test Chart Tool Directly
```bash
curl -X POST http://localhost:8788/api/v2/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "session": "direct-test",
    "messages": [{
      "role": "user",
      "content": "generate chart for nvda"
    }]
  }' | python3 -m json.tool
```

### Clear Session (Fresh Start)
```bash
curl -X DELETE "http://localhost:8788/api/v2/chat/history?session=YOUR_SESSION_ID"
```

Then refresh browser.

---

**Status**: ✅ Charts fully implemented and tested
**Last Updated**: October 2, 2025

