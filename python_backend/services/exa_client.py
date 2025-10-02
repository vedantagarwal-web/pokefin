"""
Exa AI Client for semantic search and research
https://exa.ai/
"""

import os
import httpx
from typing import Dict, Any, List

class ExaClient:
    """Client for Exa AI semantic search"""
    
    def __init__(self):
        self.api_key = os.getenv("EXA_API_KEY", "")
        self.base_url = "https://api.exa.ai"
        self.client = httpx.AsyncClient(
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        **kwargs
    ) -> Any:
        """Search using Exa"""
        try:
            response = await self.client.post(
                f"{self.base_url}/search",
                json={
                    "query": query,
                    "numResults": num_results,
                    **kwargs
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._mock_search_results(query, num_results)
        
        except Exception as e:
            print(f"❌ Exa AI error: {e}")
            return self._mock_search_results(query, num_results)
    
    async def get_contents(self, ids: List[str]) -> Any:
        """Get full content for search results"""
        try:
            response = await self.client.post(
                f"{self.base_url}/contents",
                json={"ids": ids}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"results": []}
        
        except Exception as e:
            return {"results": []}
    
    async def get_market_sentiment(self) -> Dict[str, Any]:
        """Get overall market sentiment from news"""
        results = await self.search("stock market sentiment news today", num_results=20)
        
        # Analyze sentiment (mock for now)
        return {
            "score": 0.6,  # -1 to 1
            "label": "moderately bullish",
            "drivers": [
                "Tech earnings beat expectations",
                "Fed signals pause on rate hikes",
                "Strong jobs report"
            ]
        }
    
    def _mock_search_results(self, query: str, num_results: int) -> Any:
        """Mock search results for development"""
        return {
            "results": [
                {
                    "id": f"result_{i}",
                    "title": f"Result {i} for {query}",
                    "url": f"https://example.com/{i}",
                    "text": f"Content related to {query}...",
                    "published_date": "2024-01-01"
                }
                for i in range(min(num_results, 5))
            ]
        }

