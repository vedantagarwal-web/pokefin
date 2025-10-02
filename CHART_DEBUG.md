# 🔍 Chart Debugging Guide

## What You're Seeing
- ✅ AI response appears
- ✅ Dark chart container appears
- ❌ Chart content is blank/empty

## Possible Causes

### 1. TradingView Library Not Loading
**Symptom**: Console shows "TradingView library not loaded"

**Test**:
```
Open: http://localhost:8787/test-chart.html
```

**Fix if needed**:
- Check internet connection
- Try different CDN URL
- Check browser network tab for 404/CORS errors

### 2. Chart Data Format Issue
**Symptom**: Console shows errors about data format

**Current data format**:
```javascript
{
  time: '2025-09-02',  // YYYY-MM-DD format
  open: 170,
  high: 172.38,
  low: 167.22,
  close: 170.78
}
```

### 3. Container Width Issue
**Symptom**: Container has 0 width

**Check**: Console should show container dimensions
**Fix**: Added min-width: 600px to container

## Debugging Steps

### Step 1: Open Browser Console
1. Press F12 (or Cmd+Option+I on Mac)
2. Go to "Console" tab
3. Refresh page

### Step 2: Look for These Messages
```
✅ TradingView Lightweight Charts library loaded
📊 Rendering 1 chart(s)
Chart 0: candlestick NVDA
📈 renderPriceChart called
✅ Container found, dimensions: XXX x 400
✅ Chart rendered: chart-0
```

### Step 3: Check for Errors
Look for any red error messages:
- ❌ TradingView library not loaded
- ❌ Container not found
- ❌ Uncaught TypeError
- ❌ Cannot read property 'createChart'

### Step 4: Inspect Chart Container
1. Right-click on the dark box
2. Click "Inspect Element"
3. Check:
   - Does it have id="chart-0"?
   - Does it have width > 0?
   - Are there any child elements?

## Quick Fixes to Try

### Fix 1: Hard Refresh
```
Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

### Fix 2: Clear Cache
1. Open DevTools (F12)
2. Right-click refresh button
3. Click "Empty Cache and Hard Reload"

### Fix 3: Check Network Tab
1. Go to Network tab in DevTools
2. Refresh page
3. Look for: `lightweight-charts.standalone.production.js`
4. Status should be 200 (not 404 or failed)

## Alternative: Test Chart Directly

Open this test page:
```
http://localhost:8787/test-chart.html
```

You should see:
- ✅ "TradingView library loaded"
- ✅ "Chart rendered successfully!"
- ✅ A working candlestick chart

If test chart works but main app doesn't:
→ Issue is in our chart rendering code

If test chart also doesn't work:
→ Issue is with TradingView library loading

## Console Commands to Run

### Check if library is loaded
```javascript
typeof LightweightCharts
```
Should return: `"object"` (not `"undefined"`)

### Check if chart manager exists
```javascript
window.chartManager
```
Should return: `ChartManager {charts: Map(0), chartCounter: 0}`

### Manually create a test chart
```javascript
const testContainer = document.createElement('div');
testContainer.style.cssText = 'width: 600px; height: 400px; background: #1e222d;';
document.body.appendChild(testContainer);

const chart = LightweightCharts.createChart(testContainer, {
  width: 600,
  height: 400,
  layout: { background: { color: '#1e222d' }, textColor: '#fff' }
});

const series = chart.addCandlestickSeries();
series.setData([
  { time: '2024-09-01', open: 100, high: 110, low: 95, close: 105 },
  { time: '2024-09-02', open: 105, high: 115, low: 100, close: 112 }
]);
```

If this works → Our chart data is the issue
If this fails → Library is the issue

## What I Fixed

1. ✅ Added library load check
2. ✅ Added container width fallback (600px)
3. ✅ Added min-width to container
4. ✅ Added comprehensive error logging
5. ✅ Added dynamic library loading fallback
6. ✅ Fixed chart persistence in backend

## Next Steps Based on Console Output

**If you see**: "TradingView library not loaded"
→ Library loading issue, check network tab

**If you see**: "Container not found"
→ DOM timing issue, chart rendered before container ready

**If you see**: Container width is 0
→ CSS issue, container not sized properly

**If you see**: Data format error
→ Chart data format issue with dates/numbers

**If you see no errors**:
→ Chart might be rendering but invisible due to CSS

## Screenshots Needed

Please share:
1. Browser console output
2. Network tab (filter: lightweight-charts)
3. Elements tab (inspect chart container)
4. What you see on test-chart.html

This will help identify the exact issue!

