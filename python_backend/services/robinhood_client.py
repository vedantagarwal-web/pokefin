"""
Robinhood OAuth2 Client - Direct integration with Robinhood API
Handles OAuth2 flow and portfolio data fetching
"""

import os
import uuid
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import httpx
from urllib.parse import urlencode, parse_qs

load_dotenv()

class RobinhoodClient:
    """Direct Robinhood OAuth2 client"""
    
    def __init__(self):
        self.client_id = os.getenv("ROBINHOOD_CLIENT_ID", "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS")
        self.client_secret = os.getenv("ROBINHOOD_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("ROBINHOOD_REDIRECT_URI", "http://localhost:8787/callback")
        self.base_url = "https://api.robinhood.com"
        self.oauth_url = "https://api.robinhood.com/oauth2/token/"
        
        print(f"✅ Robinhood client initialized (redirect: {self.redirect_uri})")
    
    def get_authorization_url(self, state: str = None) -> Dict[str, Any]:
        """Generate OAuth2 authorization URL - Note: Robinhood no longer provides public OAuth2"""
        if not state:
            state = str(uuid.uuid4())
        
        # Robinhood no longer provides public OAuth2 API
        # Return a demo/fallback URL that explains the situation
        demo_url = f"https://app.snaptrade.com/connect?brokerage=robinhood&demo=true&state={state}"
        
        return {
            "authorization_url": demo_url,
            "state": state,
            "client_id": "demo",
            "redirect_uri": self.redirect_uri,
            "demo": True,
            "message": "Robinhood no longer provides public OAuth2 API. Using SnapTrade demo flow."
        }
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": self.client_id,
                    "redirect_uri": self.redirect_uri
                }
                
                response = await client.post(self.oauth_url, data=data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    return {
                        "success": True,
                        "access_token": token_data.get("access_token"),
                        "refresh_token": token_data.get("refresh_token"),
                        "expires_in": token_data.get("expires_in"),
                        "token_type": token_data.get("token_type", "Bearer")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Token exchange failed: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Token exchange error: {str(e)}"
            }
    
    async def get_accounts(self, access_token: str) -> Dict[str, Any]:
        """Get user's Robinhood accounts"""
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/accounts/",
                    headers=headers
                )
                
                if response.status_code == 200:
                    accounts_data = response.json()
                    return {
                        "success": True,
                        "accounts": accounts_data.get("results", [])
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get accounts: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Accounts fetch error: {str(e)}"
            }
    
    async def get_positions(self, access_token: str, account_id: str = None) -> Dict[str, Any]:
        """Get user's positions"""
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/positions/"
                if account_id:
                    url = f"{self.base_url}/accounts/{account_id}/positions/"
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    positions_data = response.json()
                    return {
                        "success": True,
                        "positions": positions_data.get("results", [])
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get positions: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Positions fetch error: {str(e)}"
            }
    
    async def get_portfolios(self, access_token: str, account_id: str = None) -> Dict[str, Any]:
        """Get user's portfolio summary"""
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/portfolios/"
                if account_id:
                    url = f"{self.base_url}/accounts/{account_id}/portfolio/"
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    portfolio_data = response.json()
                    if isinstance(portfolio_data, dict):
                        portfolio_data = [portfolio_data]
                    return {
                        "success": True,
                        "portfolios": portfolio_data
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get portfolios: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Portfolio fetch error: {str(e)}"
            }
    
    async def get_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get market data for symbols"""
        try:
            async with httpx.AsyncClient() as client:
                symbols_str = ",".join(symbols)
                url = f"{self.base_url}/quotes/?symbols={symbols_str}"
                
                response = await client.get(url)
                
                if response.status_code == 200:
                    market_data = response.json()
                    return {
                        "success": True,
                        "quotes": market_data.get("results", [])
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get market data: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Market data fetch error: {str(e)}"
            }
