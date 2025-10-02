"""
Ticker Resolver - Converts company names to tickers
"""

from typing import Dict, Any
from .financial_datasets_client import FinancialDatasetsClient

class TickerResolver:
    """Resolves company names to ticker symbols"""
    
    def __init__(self):
        self.fd_client = FinancialDatasetsClient()
        
        # Cache for common company names
        self.cache = {
            "nvidia": "NVDA",
            "apple": "AAPL",
            "tesla": "TSLA",
            "microsoft": "MSFT",
            "amazon": "AMZN",
            "google": "GOOGL",
            "meta": "META",
            "facebook": "META",
            "robinhood": "HOOD",
            "coinbase": "COIN",
            "amd": "AMD",
            "intel": "INTC",
        }
    
    async def resolve(self, query: str) -> Dict[str, Any]:
        """Resolve query to ticker symbol"""
        query_lower = query.lower().strip()
        
        # Check if it's already a ticker (all caps, short)
        if query.isupper() and len(query) <= 5:
            return {
                "ticker": query,
                "company_name": await self._get_company_name(query),
                "confidence": "high"
            }
        
        # Check cache
        if query_lower in self.cache:
            ticker = self.cache[query_lower]
            return {
                "ticker": ticker,
                "company_name": query,
                "confidence": "high"
            }
        
        # Search Financial Datasets
        search_results = await self.fd_client.search_symbols(query)
        
        if search_results and len(search_results) > 0:
            return {
                "ticker": search_results[0]["symbol"],
                "company_name": search_results[0]["name"],
                "confidence": "high" if len(search_results) == 1 else "medium",
                "alternatives": [
                    {"ticker": r["symbol"], "name": r["name"]}
                    for r in search_results[1:4]
                ] if len(search_results) > 1 else []
            }
        
        return {
            "ticker": None,
            "error": f"Could not find ticker for '{query}'",
            "confidence": "none"
        }
    
    async def _get_company_name(self, ticker: str) -> str:
        """Get company name from ticker"""
        try:
            profile = await self.fd_client.get_company_profile(ticker)
            return profile.get("name", ticker)
        except:
            return ticker

