/**
 * Chart Manager - Handles TradingView embedded charts
 */

class ChartManager {
  constructor() {
    this.charts = new Map(); // Store chart instances
    this.chartCounter = 0;
  }

  /**
   * Render price chart using TradingView widget (embedded iframe)
   */
  renderPriceChart(containerId, chartData) {
    console.log('📈 renderPriceChart called:', containerId, chartData);
    
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`❌ Container ${containerId} not found`);
      return null;
    }
    
    console.log('✅ Container found, embedding TradingView chart...');

    // Map timeframe to TradingView interval
    const intervalMap = {
      '1D': '5',     // 5 minute
      '1W': '60',    // 1 hour
      '1M': 'D',     // Daily
      '3M': 'D',     // Daily
      '6M': 'D',     // Daily
      '1Y': 'W',     // Weekly
      '5Y': 'M'      // Monthly
    };
    
    const interval = intervalMap[chartData.timeframe] || 'D';
    const ticker = chartData.ticker || 'NVDA';
    
    // Create widget container
    const widgetContainer = document.createElement('div');
    widgetContainer.className = 'tradingview-widget-container';
    widgetContainer.style.cssText = 'height:100%;width:100%';
    
    const widgetDiv = document.createElement('div');
    widgetDiv.className = 'tradingview-widget-container__widget';
    widgetDiv.style.cssText = 'height:calc(100% - 32px);width:100%';
    
    // Create script element with configuration
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: ticker,
      interval: interval,
      timezone: "Etc/UTC",
      theme: "dark",
      style: "1",
      locale: "en",
      enable_publishing: false,
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: false,
      backgroundColor: "rgba(30, 34, 45, 1)",
      gridColor: "rgba(43, 43, 67, 0.3)",
      hide_volume: false,
      support_host: "https://www.tradingview.com"
    });
    
    // Assemble widget
    widgetContainer.appendChild(widgetDiv);
    widgetContainer.appendChild(script);
    
    // Clear container and add widget
    container.innerHTML = '';
    container.appendChild(widgetContainer);
    
    console.log('✅ TradingView widget embedded for', ticker);
    
    // Store reference
    this.charts.set(containerId, { type: 'tradingview-widget', ticker });
    
    return container;
  }

  /**
   * Render comparison chart using TradingView widget
   */
  renderComparisonChart(containerId, chartData) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return null;
    }

    // Use TradingView comparison widget
    const tickers = chartData.tickers || [];
    const symbols = tickers.map(t => `{"symbol":"${t}"}`).join(',');
    
    container.innerHTML = `
      <div class="tradingview-widget-container" style="height:100%;width:100%">
        <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js" async>
        {
          "symbols": [${symbols}],
          "chartOnly": false,
          "width": "100%",
          "height": "100%",
          "locale": "en",
          "colorTheme": "dark",
          "autosize": true,
          "showVolume": false,
          "showMA": false,
          "hideDateRanges": false,
          "hideMarketStatus": false,
          "hideSymbolLogo": false,
          "scalePosition": "right",
          "scaleMode": "Normal",
          "fontFamily": "-apple-system, BlinkMacSystemFont, Trebuchet MS, Roboto, Ubuntu, sans-serif",
          "fontSize": "10",
          "noTimeScale": false,
          "valuesTracking": "1",
          "changeMode": "price-and-percent",
          "chartType": "area",
          "backgroundColor": "rgba(30, 34, 45, 1)",
          "lineWidth": 2,
          "lineType": 0,
          "dateRanges": [
            "12m|1D"
          ]
        }
        </script>
      </div>
    `;

    this.charts.set(containerId, { type: 'tradingview-comparison', tickers });
    return container;
  }

  /**
   * Render sector heatmap
   */
  renderSectorHeatmap(containerId, heatmapData) {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    // Clear container
    container.innerHTML = '';
    container.className = 'sector-heatmap';

    // Create heatmap tiles
    heatmapData.data.forEach(sector => {
      const tile = document.createElement('div');
      tile.className = 'heatmap-tile';
      
      // Color based on performance
      const changePercent = sector.change_percent;
      let bgColor;
      if (changePercent > 2) bgColor = '#00C853';
      else if (changePercent > 1) bgColor = '#64DD17';
      else if (changePercent > 0) bgColor = '#AED581';
      else if (changePercent > -1) bgColor = '#FFAB91';
      else if (changePercent > -2) bgColor = '#FF7043';
      else bgColor = '#F44336';

      tile.style.backgroundColor = bgColor;
      tile.innerHTML = `
        <div class="heatmap-sector-name">${sector.sector}</div>
        <div class="heatmap-change">${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%</div>
      `;

      container.appendChild(tile);
    });
  }


  /**
   * Create a unique container for a chart
   */
  createChartContainer() {
    const id = `chart-${this.chartCounter++}`;
    const container = document.createElement('div');
    container.id = id;
    container.className = 'chart-container';
    container.style.cssText = 'width: 100%; height: 500px; margin: 16px 0; border-radius: 8px; overflow: hidden; background: #1e222d;';
    return container;
  }

  /**
   * Destroy a chart instance
   */
  destroyChart(containerId) {
    const chartObj = this.charts.get(containerId);
    if (chartObj) {
      chartObj.chart.remove();
      chartObj.resizeObserver.disconnect();
      this.charts.delete(containerId);
    }
  }

  /**
   * Destroy all charts
   */
  destroyAllCharts() {
    this.charts.forEach((chartObj, containerId) => {
      this.destroyChart(containerId);
    });
  }
}

// Initialize chart manager (using TradingView widgets, no library needed)
console.log('✅ Chart Manager initialized (TradingView widgets)');
window.chartManager = new ChartManager();

