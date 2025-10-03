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
    console.log('📊 renderComparisonChart called:', containerId, chartData);
    
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`❌ Container ${containerId} not found`);
      return null;
    }

    console.log('✅ Container found, creating comparison chart...');

    // Use TradingView's advanced chart with comparison
    const tickers = chartData.tickers || [];
    if (tickers.length === 0) {
      console.error('❌ No tickers provided for comparison');
      return null;
    }

    const mainSymbol = tickers[0];
    const compareSymbols = tickers.slice(1).map(t => `"${t}"`).join(',');
    
    // Create widget container
    const widgetContainer = document.createElement('div');
    widgetContainer.className = 'tradingview-widget-container';
    widgetContainer.style.cssText = 'height:100%;width:100%';
    
    const widgetDiv = document.createElement('div');
    widgetDiv.className = 'tradingview-widget-container__widget';
    widgetDiv.style.cssText = 'height:calc(100% - 32px);width:100%';
    
    // Create script element with comparison configuration
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.async = true;
    
    // Build comparison studies string
    const comparisonStudies = compareSymbols ? 
      `"studies": [${compareSymbols.split(',').map((s, i) => 
        `{"id":"Compare@tv-basicstudies","inputs":{"symbol":${s},"source":"close"}}`
      ).join(',')}],` : '';
    
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: mainSymbol,
      interval: "D",
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
      ...(compareSymbols && {
        studies: tickers.slice(1).map(ticker => ({
          id: "Compare@tv-basicstudies",
          inputs: {
            symbol: ticker,
            source: "close"
          }
        }))
      }),
      support_host: "https://www.tradingview.com"
    });
    
    // Assemble widget
    widgetContainer.appendChild(widgetDiv);
    widgetContainer.appendChild(script);
    
    // Clear container and add widget
    container.innerHTML = '';
    container.appendChild(widgetContainer);
    
    console.log('✅ TradingView comparison widget embedded for', tickers);

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
    // Styling handled by CSS now
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

