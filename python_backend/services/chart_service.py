"""
Chart Service - Generates chart data for TradingView Lightweight Charts
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .financial_datasets_client import FinancialDatasetsClient

class ChartService:
    """
    Service for generating chart data compatible with TradingView Lightweight Charts
    """
    
    def __init__(self):
        self.fd_client = FinancialDatasetsClient()
    
    async def generate_price_chart(
        self,
        ticker: str,
        timeframe: str = "1D",
        chart_type: str = "candlestick",
        include_volume: bool = True,
        indicators: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate price chart data
        
        Args:
            ticker: Stock ticker symbol
            timeframe: 1D, 1W, 1M, 3M, 6M, 1Y, 5Y
            chart_type: candlestick, line, area
            include_volume: Include volume bars
            indicators: List of technical indicators to add (ma20, ma50, rsi, macd)
        
        Returns:
            Chart configuration for frontend rendering
        """
        
        # Get price data based on timeframe
        if timeframe == "1D":
            prices = await self.fd_client.get_intraday_prices(ticker)
            price_data = self._format_intraday_data(prices)
        else:
            prices = await self.fd_client.get_historical_prices(ticker, timeframe)
            price_data = self._format_historical_data(prices, chart_type)
        
        chart = {
            "ticker": ticker,
            "timeframe": timeframe,
            "type": chart_type,
            "data": price_data,
            "metadata": {
                "start_date": price_data[0]["time"] if price_data else None,
                "end_date": price_data[-1]["time"] if price_data else None,
                "data_points": len(price_data)
            }
        }
        
        # Add volume data
        if include_volume and prices:
            chart["volume"] = self._format_volume_data(prices)
        
        # Add technical indicators
        if indicators:
            chart["indicators"] = await self._calculate_indicators(prices, indicators)
        
        return chart
    
    async def generate_comparison_chart(
        self,
        tickers: List[str],
        timeframe: str = "1Y"
    ) -> Dict[str, Any]:
        """
        Generate normalized comparison chart for multiple stocks
        
        Returns data normalized to 100 at start date for easy comparison
        """
        import asyncio
        
        # Get data for all tickers in parallel
        all_data = await asyncio.gather(*[
            self.fd_client.get_historical_prices(ticker, timeframe)
            for ticker in tickers
        ], return_exceptions=True)
        
        # Normalize each series to 100 at start
        normalized_series = []
        for ticker, data in zip(tickers, all_data):
            if isinstance(data, Exception) or not data:
                continue
            
            start_price = data[0].get("close", 100)
            normalized = {
                "ticker": ticker,
                "data": [
                    {
                        "time": item.get("time", item.get("date", "")).split("T")[0],
                        "value": (item.get("close", 0) / start_price) * 100
                    }
                    for item in data
                ]
            }
            normalized_series.append(normalized)
        
        return {
            "type": "comparison",
            "timeframe": timeframe,
            "series": normalized_series,
            "tickers": tickers
        }
    
    async def generate_portfolio_chart(
        self,
        holdings: List[Dict[str, Any]],
        timeframe: str = "1M"
    ) -> Dict[str, Any]:
        """
        Generate portfolio value chart over time
        
        Args:
            holdings: [{ticker, shares, cost_basis}]
            timeframe: Time period
        """
        import asyncio
        
        # Get historical prices for all holdings
        tickers = [h["ticker"] for h in holdings]
        all_prices = await asyncio.gather(*[
            self.fd_client.get_historical_prices(ticker, timeframe)
            for ticker in tickers
        ], return_exceptions=True)
        
        # Calculate portfolio value at each point in time
        portfolio_values = []
        
        # Get all unique dates
        dates = set()
        for prices in all_prices:
            if not isinstance(prices, Exception) and prices:
                dates.update(p.get("time", p.get("date", "")).split("T")[0] for p in prices)
        
        dates = sorted(dates)
        
        # Calculate total value for each date
        for date in dates:
            total_value = 0
            for holding, prices in zip(holdings, all_prices):
                if isinstance(prices, Exception):
                    continue
                
                # Find price for this date
                price_data = next((p for p in prices if p.get("time", p.get("date", "")).split("T")[0] == date), None)
                if price_data:
                    total_value += holding["shares"] * price_data.get("close", 0)
            
            portfolio_values.append({
                "time": date,
                "value": total_value
            })
        
        # Calculate performance metrics
        if portfolio_values:
            start_value = portfolio_values[0]["value"]
            end_value = portfolio_values[-1]["value"]
            total_return = ((end_value - start_value) / start_value) * 100
            
            # Calculate cost basis total
            cost_basis_total = sum(h["shares"] * h.get("cost_basis", 0) for h in holdings)
            unrealized_gain = end_value - cost_basis_total
            unrealized_gain_pct = (unrealized_gain / cost_basis_total * 100) if cost_basis_total else 0
        else:
            total_return = 0
            unrealized_gain = 0
            unrealized_gain_pct = 0
        
        return {
            "type": "portfolio",
            "timeframe": timeframe,
            "data": portfolio_values,
            "metrics": {
                "total_return_pct": round(total_return, 2),
                "unrealized_gain": round(unrealized_gain, 2),
                "unrealized_gain_pct": round(unrealized_gain_pct, 2)
            }
        }
    
    async def generate_sector_heatmap(self) -> Dict[str, Any]:
        """
        Generate sector performance heatmap data
        """
        import asyncio
        
        sectors = {
            "Technology": "XLK",
            "Healthcare": "XLV",
            "Financials": "XLF",
            "Energy": "XLE",
            "Consumer Discretionary": "XLY",
            "Industrials": "XLI",
            "Materials": "XLB",
            "Consumer Staples": "XLP",
            "Utilities": "XLU",
            "Real Estate": "XLRE",
            "Communication": "XLC"
        }
        
        # Get quotes for all sector ETFs
        quotes = await asyncio.gather(*[
            self.fd_client.get_quote(ticker)
            for ticker in sectors.values()
        ], return_exceptions=True)
        
        heatmap_data = []
        for (name, ticker), quote in zip(sectors.items(), quotes):
            if isinstance(quote, Exception):
                continue
            
            heatmap_data.append({
                "sector": name,
                "ticker": ticker,
                "change_percent": quote.get("change_percent", 0),
                "price": quote.get("price", 0)
            })
        
        # Sort by performance
        heatmap_data.sort(key=lambda x: x["change_percent"], reverse=True)
        
        return {
            "type": "heatmap",
            "data": heatmap_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def _format_intraday_data(self, prices: List[Dict]) -> List[Dict]:
        """Format intraday prices for TradingView"""
        return [
            {
                "time": item.get("time", ""),
                "value": item.get("price", 0)
            }
            for item in prices
        ]
    
    def _format_historical_data(self, prices: List[Dict], chart_type: str) -> List[Dict]:
        """Format historical prices for TradingView"""
        if chart_type == "candlestick":
            return [
                {
                    "time": item.get("time", item.get("date", "")).split("T")[0],  # Extract date part
                    "open": item.get("open", item.get("close", 0)),
                    "high": item.get("high", item.get("close", 0)),
                    "low": item.get("low", item.get("close", 0)),
                    "close": item.get("close", 0)
                }
                for item in prices
            ]
        else:  # line or area
            return [
                {
                    "time": item.get("time", item.get("date", "")).split("T")[0],  # Extract date part
                    "value": item.get("close", 0)
                }
                for item in prices
            ]
    
    def _format_volume_data(self, prices: List[Dict]) -> List[Dict]:
        """Format volume data for TradingView"""
        return [
            {
                "time": item.get("time", item.get("date", "")).split("T")[0] if "T" in item.get("time", item.get("date", "")) else item.get("time", item.get("date", "")),
                "value": item.get("volume", 0),
                "color": "#26a69a" if item.get("close", 0) >= item.get("open", 0) else "#ef5350"
            }
            for item in prices
        ]
    
    async def _calculate_indicators(
        self,
        prices: List[Dict],
        indicators: List[str]
    ) -> Dict[str, List[Dict]]:
        """
        Calculate technical indicators
        
        Supported: ma20, ma50, ma200, rsi, macd
        """
        result = {}
        
        if not prices:
            return result
        
        closes = [p.get("close", 0) for p in prices]
        dates = [p.get("time", p.get("date", "")).split("T")[0] if "T" in p.get("time", p.get("date", "")) else p.get("time", p.get("date", "")) for p in prices]
        
        for indicator in indicators:
            if indicator == "ma20":
                result["ma20"] = self._calculate_ma(closes, dates, 20)
            elif indicator == "ma50":
                result["ma50"] = self._calculate_ma(closes, dates, 50)
            elif indicator == "ma200":
                result["ma200"] = self._calculate_ma(closes, dates, 200)
            elif indicator == "rsi":
                result["rsi"] = self._calculate_rsi(closes, dates)
            elif indicator == "macd":
                result["macd"] = self._calculate_macd(closes, dates)
        
        return result
    
    def _calculate_ma(self, closes: List[float], dates: List[str], period: int) -> List[Dict]:
        """Calculate moving average"""
        ma_values = []
        
        for i in range(len(closes)):
            if i < period - 1:
                ma_values.append({"time": dates[i], "value": None})
            else:
                ma = sum(closes[i-period+1:i+1]) / period
                ma_values.append({"time": dates[i], "value": ma})
        
        return ma_values
    
    def _calculate_rsi(self, closes: List[float], dates: List[str], period: int = 14) -> List[Dict]:
        """Calculate RSI (Relative Strength Index)"""
        rsi_values = []
        
        # Calculate price changes
        changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        
        gains = [c if c > 0 else 0 for c in changes]
        losses = [-c if c < 0 else 0 for c in changes]
        
        for i in range(len(changes)):
            if i < period:
                rsi_values.append({"time": dates[i+1], "value": None})
            else:
                avg_gain = sum(gains[i-period+1:i+1]) / period
                avg_loss = sum(losses[i-period+1:i+1]) / period
                
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                
                rsi_values.append({"time": dates[i+1], "value": rsi})
        
        return rsi_values
    
    def _calculate_macd(self, closes: List[float], dates: List[str]) -> Dict[str, List[Dict]]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        # Calculate EMAs
        ema12 = self._calculate_ema(closes, 12)
        ema26 = self._calculate_ema(closes, 26)
        
        # MACD line = EMA12 - EMA26
        macd_line = [ema12[i] - ema26[i] if ema12[i] and ema26[i] else None 
                     for i in range(len(closes))]
        
        # Signal line = 9-day EMA of MACD
        signal_line = self._calculate_ema([m for m in macd_line if m is not None], 9)
        
        # Pad signal line with None values
        signal_line = [None] * (len(macd_line) - len(signal_line)) + signal_line
        
        # Histogram = MACD - Signal
        histogram = [macd_line[i] - signal_line[i] if macd_line[i] and signal_line[i] else None
                    for i in range(len(macd_line))]
        
        return {
            "macd": [{"time": dates[i], "value": macd_line[i]} for i in range(len(dates))],
            "signal": [{"time": dates[i], "value": signal_line[i]} for i in range(len(dates))],
            "histogram": [{"time": dates[i], "value": histogram[i]} for i in range(len(dates))]
        }
    
    def _calculate_ema(self, values: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        ema = []
        multiplier = 2 / (period + 1)
        
        # Start with SMA for first value
        sma = sum(values[:period]) / period
        ema.append(sma)
        
        # Calculate EMA for rest
        for i in range(period, len(values)):
            ema_value = (values[i] - ema[-1]) * multiplier + ema[-1]
            ema.append(ema_value)
        
        # Pad with None values
        return [None] * (period - 1) + ema

