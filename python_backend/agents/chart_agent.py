"""
Chart Generator Agent - Creates chart configurations for frontend
"""

from typing import Dict, Any, List

class ChartGeneratorAgent:
    """Generates chart configurations"""
    
    async def generate_chart(
        self,
        ticker: str,
        timeframe: str = "6M",
        chart_type: str = "candlestick",
        indicators: List[str] = None
    ) -> Dict[str, Any]:
        """Generate chart configuration"""
        
        from services.financial_datasets_client import FinancialDatasetsClient
        
        fd_client = FinancialDatasetsClient()
        
        if chart_type == "candlestick":
            data = await fd_client.get_historical_prices(ticker, timeframe)
            
            return {
                "type": "candlestick",
                "ticker": ticker,
                "timeframe": timeframe,
                "data": [
                    {
                        "time": d["date"],
                        "open": d["open"],
                        "high": d["high"],
                        "low": d["low"],
                        "close": d["close"]
                    }
                    for d in data
                ],
                "volume": [
                    {
                        "time": d["date"],
                        "value": d["volume"],
                        "color": "green" if d["close"] > d["open"] else "red"
                    }
                    for d in data
                ]
            }
        
        else:  # line chart
            data = await fd_client.get_historical_prices(ticker, timeframe)
            
            return {
                "type": "line",
                "ticker": ticker,
                "timeframe": timeframe,
                "data": [
                    {
                        "time": d["date"],
                        "value": d["close"]
                    }
                    for d in data
                ]
            }
    
    async def generate_charts_for_analysis(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate charts for a full analysis"""
        charts = []
        
        ticker = analysis.get("ticker")
        
        if ticker:
            # Main price chart
            main_chart = await self.generate_chart(ticker, "6M", "candlestick")
            charts.append(main_chart)
        
        return charts

