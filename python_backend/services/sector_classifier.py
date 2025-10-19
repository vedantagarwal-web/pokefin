"""
Sector Classification Service
Maps stocks to GICS sectors for portfolio analysis
"""

from typing import Dict, Optional
import os
from services.financial_datasets_client import FinancialDatasetsClient

# 11 GICS Sectors
GICS_SECTORS = [
    "Technology",
    "Healthcare", 
    "Financials",
    "Consumer Discretionary",
    "Consumer Staples",
    "Communication Services",
    "Industrials",
    "Materials",
    "Energy",
    "Utilities",
    "Real Estate"
]

# Hardcoded mappings for common tickers (fallback)
TICKER_SECTOR_MAP = {
    # Technology
    "AAPL": "Technology",
    "MSFT": "Technology",
    "NVDA": "Technology",
    "GOOGL": "Technology",
    "GOOG": "Technology",
    "META": "Communication Services",
    "TSLA": "Consumer Discretionary",  # Tesla is classified as Auto (Consumer Discretionary)
    "AVGO": "Technology",
    "ORCL": "Technology",
    "ADBE": "Technology",
    "CRM": "Technology",
    "CSCO": "Technology",
    "ACN": "Technology",
    "AMD": "Technology",
    "PLTR": "Technology",
    "MAGS": "Technology",  # Magnificent 7 ETF - Tech heavy
    
    # Healthcare
    "UNH": "Healthcare",
    "LLY": "Healthcare",
    "JNJ": "Healthcare",
    "ABBV": "Healthcare",
    "MRK": "Healthcare",
    "TMO": "Healthcare",
    "ABT": "Healthcare",
    
    # Financials
    "BRK.B": "Financials",
    "JPM": "Financials",
    "V": "Financials",
    "MA": "Financials",
    "BAC": "Financials",
    "WFC": "Financials",
    
    # Consumer Discretionary
    "AMZN": "Consumer Discretionary",
    "HD": "Consumer Discretionary",
    "MCD": "Consumer Discretionary",
    "NKE": "Consumer Discretionary",
    "SBUX": "Consumer Discretionary",
    "CSV": "Consumer Discretionary",
    
    # Consumer Staples
    "WMT": "Consumer Staples",
    "PG": "Consumer Staples",
    "COST": "Consumer Staples",
    "KO": "Consumer Staples",
    "PEP": "Consumer Staples",
    
    # Communication Services
    "NFLX": "Communication Services",
    "DIS": "Communication Services",
    "CMCSA": "Communication Services",
    
    # Materials & Commodities
    "LIN": "Materials",
    "APD": "Materials",
    "FCX": "Materials",
    "NEM": "Materials",
    "URA": "Materials",  # Uranium ETF
    "IAU": "Materials",  # Gold ETF
    "SLV": "Materials",  # Silver ETF
    
    # Energy
    "XOM": "Energy",
    "CVX": "Energy",
    "COP": "Energy",
    
    # Crypto/Bitcoin
    "IBIT": "Financials",  # Bitcoin ETF - categorize as Financials
    
    # Industrials
    "UNP": "Industrials",
    "CAT": "Industrials",
    "BA": "Industrials",
    "GE": "Industrials",
}

class SectorClassifier:
    """Classifies stocks into GICS sectors"""
    
    def __init__(self):
        self.fd_client = FinancialDatasetsClient()
        self.cache = {}
    
    async def get_sector(self, ticker: str) -> str:
        """
        Get the GICS sector for a ticker
        Returns one of the 11 GICS sectors
        """
        ticker = ticker.upper()
        
        # Check cache
        if ticker in self.cache:
            return self.cache[ticker]
        
        # Check hardcoded mappings first
        if ticker in TICKER_SECTOR_MAP:
            sector = TICKER_SECTOR_MAP[ticker]
            self.cache[ticker] = sector
            return sector
        
        # Try to get from Financial Datasets API
        try:
            profile = await self.fd_client.get_company_profile(ticker)
            
            if profile and "sector" in profile:
                sector = self._normalize_sector(profile["sector"])
                self.cache[ticker] = sector
                return sector
            
            if profile and "industry" in profile:
                # Try to infer sector from industry
                sector = self._infer_sector_from_industry(profile["industry"])
                self.cache[ticker] = sector
                return sector
        
        except Exception as e:
            print(f"⚠️ Could not fetch sector for {ticker}: {e}")
        
        # Default fallback
        default_sector = "Technology"  # Most common sector
        self.cache[ticker] = default_sector
        return default_sector
    
    def _normalize_sector(self, sector: str) -> str:
        """Normalize sector name to GICS standard"""
        sector_lower = sector.lower()
        
        # Map common variations to GICS sectors
        if "tech" in sector_lower or "software" in sector_lower or "semiconductor" in sector_lower:
            return "Technology"
        elif "health" in sector_lower or "pharma" in sector_lower or "bio" in sector_lower:
            return "Healthcare"
        elif "financ" in sector_lower or "bank" in sector_lower or "insurance" in sector_lower:
            return "Financials"
        elif "consumer" in sector_lower:
            if "staple" in sector_lower or "defensive" in sector_lower:
                return "Consumer Staples"
            else:
                return "Consumer Discretionary"
        elif "commun" in sector_lower or "media" in sector_lower or "telecom" in sector_lower:
            return "Communication Services"
        elif "industr" in sector_lower or "aero" in sector_lower or "defense" in sector_lower:
            return "Industrials"
        elif "material" in sector_lower or "chemical" in sector_lower or "mining" in sector_lower:
            return "Materials"
        elif "energy" in sector_lower or "oil" in sector_lower or "gas" in sector_lower:
            return "Energy"
        elif "utilit" in sector_lower or "electric" in sector_lower or "water" in sector_lower:
            return "Utilities"
        elif "real estate" in sector_lower or "reit" in sector_lower:
            return "Real Estate"
        
        return "Technology"  # Default
    
    def _infer_sector_from_industry(self, industry: str) -> str:
        """Infer GICS sector from industry classification"""
        return self._normalize_sector(industry)
    
    async def get_sectors_bulk(self, tickers: list) -> Dict[str, str]:
        """Get sectors for multiple tickers"""
        result = {}
        for ticker in tickers:
            result[ticker] = await self.get_sector(ticker)
        return result
    
    def get_sector_description(self, sector: str) -> str:
        """Get a brief description of what the sector represents"""
        descriptions = {
            "Technology": "Software, hardware, semiconductors, IT services",
            "Healthcare": "Pharmaceuticals, biotech, medical devices, healthcare services",
            "Financials": "Banks, insurance, asset management, payment processors",
            "Consumer Discretionary": "Retail, automotive, restaurants, entertainment, luxury goods",
            "Consumer Staples": "Food, beverages, household products, tobacco",
            "Communication Services": "Telecom, media, entertainment, social media",
            "Industrials": "Aerospace, defense, machinery, transportation, construction",
            "Materials": "Chemicals, metals, mining, paper, commodities",
            "Energy": "Oil & gas exploration, production, refining, equipment",
            "Utilities": "Electric, gas, water utilities, renewable energy",
            "Real Estate": "REITs, real estate management, development"
        }
        return descriptions.get(sector, "Various companies in this sector")

