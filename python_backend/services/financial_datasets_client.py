"""
Financial Datasets AI Client
https://financialdatasets.ai/
"""

import os
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class FinancialDatasetsClient:
    """
    Client for Financial Datasets AI API
    Provides stock prices, financials, SEC filings, etc.
    """
    
    def __init__(self):
        self.api_key = os.getenv("FDS_API_KEY", "")
        self.base_url = "https://api.financialdatasets.ai"
        self.client = httpx.AsyncClient(
            headers={
                "X-API-KEY": self.api_key
            },
            timeout=30.0,
            follow_redirects=True  # CRITICAL: Follow redirects!
        )
        
        if self.api_key:
            print(f"✅ Financial Datasets AI client initialized (key: {self.api_key[:10]}...)")
        else:
            print("⚠️  No FDS_API_KEY found, using mock data")
    
    async def get_quote(self, ticker: str) -> Dict[str, Any]:
        """
        Get real-time quote for a ticker
        """
        try:
            # Financial Datasets AI endpoint: /prices/snapshot/ (trailing slash required!)
            response = await self.client.get(
                f"{self.base_url}/prices/snapshot/",
                params={"ticker": ticker}
            )
            
            print(f"📊 FDS API Response ({ticker}): Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Got real data from FDS: {data}")
                
                # Extract from FDS response format (snapshot wrapper)
                snapshot = data.get("snapshot", {})
                
                return {
                    "ticker": ticker,
                    "price": snapshot.get("price", 0),
                    "change": snapshot.get("day_change", 0),
                    "change_percent": snapshot.get("day_change_percent", 0),
                    "volume": 0,  # Not in snapshot endpoint
                    "market_cap": snapshot.get("market_cap"),
                    "timestamp": snapshot.get("time", datetime.now().isoformat())
                }
            else:
                print(f"⚠️  FDS API returned {response.status_code}, using mock data")
                print(f"Response: {response.text[:200]}")
                # Fallback to mock data for development
                return self._mock_quote(ticker)
        
        except Exception as e:
            print(f"❌ Financial Datasets API error: {e}")
            import traceback
            traceback.print_exc()
            return self._mock_quote(ticker)
    
    async def get_historical_prices(
        self,
        ticker: str,
        timeframe: str = "1Y"
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data
        """
        try:
            # Calculate date range based on timeframe
            from datetime import timedelta
            end_date = datetime.now()
            
            days_map = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "5Y": 1825}
            days = days_map.get(timeframe, 365)
            start_date = end_date - timedelta(days=days)
            
            response = await self.client.get(
                f"{self.base_url}/prices/",
                params={
                    "ticker": ticker,
                    "interval": "day",
                    "interval_multiplier": 1,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
            )
            
            if response.status_code == 200:
                return response.json().get("prices", [])
            else:
                return self._mock_historical_data(ticker, timeframe)
        
        except Exception as e:
            print(f"❌ Financial Datasets API error: {e}")
            return self._mock_historical_data(ticker, timeframe)
    
    async def get_intraday_prices(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Get intraday price data (1-day, 1-minute intervals)
        """
        try:
            from datetime import timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            response = await self.client.get(
                f"{self.base_url}/prices/",
                params={
                    "ticker": ticker,
                    "interval": "minute",
                    "interval_multiplier": 5,  # 5-minute intervals
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
            )
            
            if response.status_code == 200:
                prices = response.json().get("prices", [])
                # Convert to simple format for charts
                return [
                    {
                        "time": p.get("time", "").split("T")[1][:5] if "T" in p.get("time", "") else "",
                        "price": p.get("close", 0),
                        "volume": p.get("volume", 0)
                    }
                    for p in prices
                ]
            else:
                return self._mock_intraday_data(ticker)
        
        except Exception as e:
            return self._mock_intraday_data(ticker)
    
    async def get_company_profile(self, ticker: str) -> Dict[str, Any]:
        """
        Get company profile and fundamental data
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/company/facts/",
                params={"ticker": ticker}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("company_facts", {})
            else:
                return self._mock_company_profile(ticker)
        
        except Exception as e:
            return self._mock_company_profile(ticker)
    
    async def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for ticker symbols by company name
        Note: FDS API doesn't have a direct search endpoint, so we use company facts
        """
        try:
            # Try to get company facts for the query (if it's a ticker)
            response = await self.client.get(
                f"{self.base_url}/company/facts/",
                params={"ticker": query.upper()}
            )
            
            if response.status_code == 200:
                data = response.json()
                facts = data.get("company_facts", {})
                return [{
                    "symbol": facts.get("ticker", query.upper()),
                    "name": facts.get("name", ""),
                    "exchange": facts.get("exchange", "")
                }]
            else:
                return self._mock_search_results(query)
        
        except Exception as e:
            print(f"❌ Search error: {e}")
            return self._mock_search_results(query)
    
    # Mock data for development/fallback
    
    def _mock_quote(self, ticker: str) -> Dict[str, Any]:
        """Mock quote data for development"""
        import random
        base_price = {"NVDA": 875, "AAPL": 175, "TSLA": 242, "MSFT": 420}.get(ticker, 100)
        change = random.uniform(-5, 5)
        
        return {
            "ticker": ticker,
            "price": base_price + change,
            "change": change,
            "change_percent": (change / base_price) * 100,
            "volume": random.randint(10000000, 100000000),
            "market_cap": random.randint(100000000000, 3000000000000),
            "timestamp": datetime.now().isoformat()
        }
    
    def _mock_historical_data(self, ticker: str, timeframe: str) -> List[Dict[str, Any]]:
        """Mock historical data"""
        import random
        
        days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "5Y": 1825}.get(timeframe, 365)
        base_price = 100
        
        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            price = base_price * (1 + random.uniform(-0.02, 0.02))
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": price * (1 + random.uniform(-0.01, 0.01)),
                "high": price * (1 + random.uniform(0, 0.02)),
                "low": price * (1 + random.uniform(-0.02, 0)),
                "close": price,
                "volume": random.randint(10000000, 100000000)
            })
            
            base_price = price
        
        return data
    
    def _mock_intraday_data(self, ticker: str) -> List[Dict[str, Any]]:
        """Mock intraday data (1 day, 5-min intervals)"""
        import random
        
        data = []
        base_price = 100
        
        # Market hours: 9:30 AM to 4:00 PM (6.5 hours = 78 five-minute intervals)
        for i in range(78):
            minutes = i * 5
            hour = 9 + (30 + minutes) // 60
            minute = (30 + minutes) % 60
            
            time = f"{hour:02d}:{minute:02d}"
            price = base_price * (1 + random.uniform(-0.005, 0.005))
            
            data.append({
                "time": time,
                "price": price,
                "volume": random.randint(100000, 1000000)
            })
            
            base_price = price
        
        return data
    
    def _mock_company_profile(self, ticker: str) -> Dict[str, Any]:
        """Mock company profile"""
        profiles = {
            "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
            "AAPL": {"name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
            "TSLA": {"name": "Tesla, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
            "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"},
            "HOOD": {"name": "Robinhood Markets, Inc.", "sector": "Financial Services", "industry": "Capital Markets"},
        }
        
        default = {"name": f"{ticker} Inc.", "sector": "Unknown", "industry": "Unknown"}
        
        profile = profiles.get(ticker, default)
        profile["symbol"] = ticker
        profile["description"] = f"{profile['name']} is a leading company in the {profile['industry']} industry."
        
        return profile
    
    def _mock_search_results(self, query: str) -> List[Dict[str, Any]]:
        """Mock search results"""
        common_tickers = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
            {"symbol": "NVDA", "name": "NVIDIA Corporation"},
        ]
        
        return [t for t in common_tickers if query.lower() in t["name"].lower() or query.upper() == t["symbol"]]

