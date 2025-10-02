"""
Market Screener Service - Filter and rank stocks based on criteria
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .financial_datasets_client import FinancialDatasetsClient

class ScreenerService:
    """
    Advanced stock screening with multiple criteria
    """
    
    def __init__(self):
        self.fd_client = FinancialDatasetsClient()
        
        # Popular stock universes
        self.sp500_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'XOM',
            'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'LLY', 'ABBV', 'MRK',
            'AVGO', 'PEP', 'KO', 'COST', 'WMT', 'CSCO', 'ACN', 'TMO', 'MCD', 'ADBE'
        ]
        
        self.tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD', 'INTC', 'CRM', 'ORCL', 'NFLX', 'AVGO', 'QCOM']
        self.growth_stocks = ['NVDA', 'TSLA', 'AMD', 'SHOP', 'SQ', 'ROKU', 'PLTR', 'SNOW', 'DDOG', 'NET']
        self.dividend_stocks = ['JNJ', 'PG', 'KO', 'PEP', 'VZ', 'T', 'XOM', 'CVX', 'MO', 'PM']
    
    async def screen_stocks(
        self,
        criteria: Dict[str, Any],
        universe: str = "sp500"
    ) -> List[Dict[str, Any]]:
        """
        Screen stocks based on criteria
        
        Criteria examples:
        - min_market_cap: 10000000000 (10B)
        - max_pe_ratio: 30
        - min_dividend_yield: 2.0
        - min_revenue_growth: 10.0
        - sector: "Technology"
        """
        
        # Get stock universe
        if universe == "sp500":
            tickers = self.sp500_tickers
        elif universe == "tech":
            tickers = self.tech_stocks
        elif universe == "growth":
            tickers = self.growth_stocks
        elif universe == "dividend":
            tickers = self.dividend_stocks
        else:
            tickers = self.sp500_tickers
        
        # Fetch data for all tickers in parallel
        import asyncio
        results = await asyncio.gather(*[
            self._get_stock_metrics(ticker)
            for ticker in tickers
        ], return_exceptions=True)
        
        # Filter based on criteria
        filtered_stocks = []
        for ticker, data in zip(tickers, results):
            if isinstance(data, Exception) or not data:
                continue
            
            # Apply filters
            if self._matches_criteria(data, criteria):
                filtered_stocks.append(data)
        
        # Sort by score or specified metric
        sort_by = criteria.get("sort_by", "market_cap")
        reverse = criteria.get("sort_order", "desc") == "desc"
        
        filtered_stocks.sort(
            key=lambda x: x.get(sort_by, 0) or 0,
            reverse=reverse
        )
        
        # Limit results
        limit = criteria.get("limit", 20)
        return filtered_stocks[:limit]
    
    async def _get_stock_metrics(self, ticker: str) -> Dict[str, Any]:
        """Get key metrics for a stock"""
        try:
            # Get quote
            quote = await self.fd_client.get_quote(ticker)
            
            # Get latest financials
            income_response = await self.fd_client.client.get(
                f"{self.fd_client.base_url}/financials/income-statements/",
                params={"ticker": ticker, "period": "ttm", "limit": 1}
            )
            
            financials = {}
            if income_response.status_code == 200:
                data = income_response.json()
                if data.get("income_statements"):
                    stmt = data["income_statements"][0]
                    financials = {
                        "revenue": stmt.get("revenue", 0),
                        "net_income": stmt.get("net_income", 0),
                        "eps": stmt.get("earnings_per_share", 0),
                        "profit_margin": (stmt.get("net_income", 0) / stmt.get("revenue", 1)) * 100 if stmt.get("revenue") else 0
                    }
            
            # Calculate P/E ratio
            pe_ratio = None
            if financials.get("eps") and financials["eps"] > 0:
                pe_ratio = quote["price"] / financials["eps"]
            
            return {
                "ticker": ticker,
                "price": quote["price"],
                "change_percent": quote["change_percent"],
                "market_cap": quote.get("market_cap", 0),
                "volume": quote.get("volume", 0),
                **financials,
                "pe_ratio": pe_ratio
            }
        
        except Exception as e:
            print(f"❌ Error getting metrics for {ticker}: {e}")
            return None
    
    def _matches_criteria(self, stock: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if stock matches screening criteria"""
        
        # Market cap filter
        if "min_market_cap" in criteria:
            if not stock.get("market_cap") or stock["market_cap"] < criteria["min_market_cap"]:
                return False
        
        if "max_market_cap" in criteria:
            if not stock.get("market_cap") or stock["market_cap"] > criteria["max_market_cap"]:
                return False
        
        # P/E ratio filter
        if "min_pe_ratio" in criteria:
            if not stock.get("pe_ratio") or stock["pe_ratio"] < criteria["min_pe_ratio"]:
                return False
        
        if "max_pe_ratio" in criteria:
            if not stock.get("pe_ratio") or stock["pe_ratio"] > criteria["max_pe_ratio"]:
                return False
        
        # Profit margin filter
        if "min_profit_margin" in criteria:
            if not stock.get("profit_margin") or stock["profit_margin"] < criteria["min_profit_margin"]:
                return False
        
        # Price performance filter
        if "min_change_percent" in criteria:
            if stock.get("change_percent", -100) < criteria["min_change_percent"]:
                return False
        
        if "max_change_percent" in criteria:
            if stock.get("change_percent", 100) > criteria["max_change_percent"]:
                return False
        
        return True
    
    async def get_top_gainers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top gaining stocks today"""
        return await self.screen_stocks(
            criteria={
                "min_change_percent": 0,
                "sort_by": "change_percent",
                "sort_order": "desc",
                "limit": limit
            },
            universe="sp500"
        )
    
    async def get_top_losers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get worst performing stocks today"""
        return await self.screen_stocks(
            criteria={
                "max_change_percent": 0,
                "sort_by": "change_percent",
                "sort_order": "asc",
                "limit": limit
            },
            universe="sp500"
        )
    
    async def get_most_active(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most actively traded stocks"""
        return await self.screen_stocks(
            criteria={
                "sort_by": "volume",
                "sort_order": "desc",
                "limit": limit
            },
            universe="sp500"
        )
    
    async def find_value_stocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find undervalued stocks (low P/E, profitable)"""
        return await self.screen_stocks(
            criteria={
                "max_pe_ratio": 20,
                "min_profit_margin": 5,
                "min_market_cap": 1000000000,  # 1B+
                "sort_by": "pe_ratio",
                "sort_order": "asc",
                "limit": limit
            },
            universe="sp500"
        )
    
    async def find_growth_stocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find high-growth stocks"""
        return await self.screen_stocks(
            criteria={
                "min_profit_margin": 15,
                "min_market_cap": 5000000000,  # 5B+
                "sort_by": "profit_margin",
                "sort_order": "desc",
                "limit": limit
            },
            universe="growth"
        )

