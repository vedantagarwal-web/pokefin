"""
Portfolio Analyzer
Analyzes portfolio holdings, calculates sector exposure, identifies gaps
"""

from typing import Dict, List, Tuple
from services.sector_classifier import SectorClassifier, GICS_SECTORS

# Mock portfolio for testing
MOCK_PORTFOLIO = {
    "TSLA": 45.0,
    "PLTR": 3.3,
    "URA": 6.7,
    "IAU": 7.0,
    "SLV": 8.0,
    "IBIT": 8.0,
    "MAGS": 12.0,
    "UNH": 6.0,
    "CSV": 4.0
}

# Benchmark S&P 500 sector weights (approximate)
SP500_BENCHMARK_WEIGHTS = {
    "Technology": 29.0,
    "Healthcare": 13.0,
    "Financials": 13.0,
    "Consumer Discretionary": 10.5,
    "Communication Services": 8.5,
    "Industrials": 8.0,
    "Consumer Staples": 6.5,
    "Energy": 4.0,
    "Utilities": 2.5,
    "Real Estate": 2.5,
    "Materials": 2.5
}

class PortfolioAnalyzer:
    """Analyzes portfolio composition and identifies opportunities"""
    
    def __init__(self):
        self.sector_classifier = SectorClassifier()
    
    async def analyze_portfolio(
        self,
        portfolio: Dict[str, float] = None
    ) -> Dict:
        """
        Comprehensive portfolio analysis
        
        Args:
            portfolio: Dict of {ticker: weight_pct}
        
        Returns:
            Analysis including sector exposure, gaps, themes
        """
        if portfolio is None:
            portfolio = MOCK_PORTFOLIO
        
        # Calculate sector exposure
        sector_exposure = await self.calculate_sector_exposure(portfolio)
        
        # Identify diversification opportunities
        diversification_ops = self.identify_diversification_opportunities(sector_exposure)
        
        # Get correlation themes
        themes = await self.get_correlation_themes(list(portfolio.keys()))
        
        # Identify overweight/underweight sectors
        weight_analysis = self.analyze_sector_weights(sector_exposure)
        
        return {
            "portfolio": portfolio,
            "sector_exposure": sector_exposure,
            "diversification_opportunities": diversification_ops,
            "themes": themes,
            "weight_analysis": weight_analysis,
            "total_stocks": len(portfolio),
            "concentration_risk": self._calculate_concentration_risk(portfolio)
        }
    
    async def calculate_sector_exposure(
        self,
        portfolio: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate portfolio exposure by sector
        
        Returns: {sector: weight_pct}
        """
        sector_weights = {}
        
        for ticker, weight in portfolio.items():
            sector = await self.sector_classifier.get_sector(ticker)
            
            if sector in sector_weights:
                sector_weights[sector] += weight
            else:
                sector_weights[sector] = weight
        
        # Sort by weight descending
        return dict(sorted(
            sector_weights.items(),
            key=lambda x: x[1],
            reverse=True
        ))
    
    def identify_diversification_opportunities(
        self,
        sector_exposure: Dict[str, float]
    ) -> List[Dict]:
        """
        Identify sectors that are underweight or missing
        
        Returns: List of opportunities sorted by priority
        """
        opportunities = []
        
        for sector in GICS_SECTORS:
            current_weight = sector_exposure.get(sector, 0)
            benchmark_weight = SP500_BENCHMARK_WEIGHTS.get(sector, 0)
            
            # Calculate gap
            gap = benchmark_weight - current_weight
            
            if gap > 3.0:  # Significant underweight (>3% gap)
                opportunities.append({
                    "sector": sector,
                    "current_weight": round(current_weight, 1),
                    "benchmark_weight": round(benchmark_weight, 1),
                    "gap": round(gap, 1),
                    "priority": "high" if gap > 8 else "medium",
                    "reason": self._get_diversification_reason(sector, gap)
                })
        
        # Sort by gap size (biggest gaps = highest priority)
        opportunities.sort(key=lambda x: x["gap"], reverse=True)
        
        return opportunities
    
    def _get_diversification_reason(self, sector: str, gap: float) -> str:
        """Get human-readable reason for diversification"""
        if gap > 10:
            return f"Critical gap: {sector} exposure is significantly below market benchmark"
        elif gap > 5:
            return f"Major opportunity: Adding {sector} would improve diversification"
        else:
            return f"Moderate gap: Consider small {sector} allocation for balance"
    
    async def get_correlation_themes(
        self,
        holdings: List[str]
    ) -> Dict[str, List[str]]:
        """
        Identify thematic correlations in portfolio
        
        Returns: {theme: [related_tickers]}
        """
        themes = {}
        
        # Get sectors for all holdings
        sectors = await self.sector_classifier.get_sectors_bulk(holdings)
        
        # Group by sector (basic theme)
        for ticker, sector in sectors.items():
            theme = f"{sector} Exposure"
            if theme not in themes:
                themes[theme] = []
            themes[theme].append(ticker)
        
        # Identify special themes
        commodities = [t for t in holdings if t in ["URA", "IAU", "SLV", "GLD"]]
        if commodities:
            themes["Commodities & Precious Metals"] = commodities
        
        crypto_exposure = [t for t in holdings if t in ["IBIT", "COIN", "MSTR"]]
        if crypto_exposure:
            themes["Crypto/Bitcoin Exposure"] = crypto_exposure
        
        mega_tech = [t for t in holdings if t in ["AAPL", "MSFT", "GOOGL", "META", "AMZN", "NVDA", "TSLA"]]
        if mega_tech:
            themes["Mega-Cap Tech"] = mega_tech
        
        return themes
    
    def analyze_sector_weights(
        self,
        sector_exposure: Dict[str, float]
    ) -> Dict[str, Dict]:
        """
        Analyze if sectors are overweight, underweight, or balanced
        
        Returns: {sector: {status, current, benchmark, diff}}
        """
        analysis = {}
        
        for sector, weight in sector_exposure.items():
            benchmark = SP500_BENCHMARK_WEIGHTS.get(sector, 0)
            diff = weight - benchmark
            
            # Determine status
            if diff > 10:
                status = "HEAVILY OVERWEIGHT"
            elif diff > 5:
                status = "OVERWEIGHT"
            elif diff < -10:
                status = "HEAVILY UNDERWEIGHT"
            elif diff < -5:
                status = "UNDERWEIGHT"
            else:
                status = "BALANCED"
            
            analysis[sector] = {
                "status": status,
                "current": round(weight, 1),
                "benchmark": round(benchmark, 1),
                "diff": round(diff, 1)
            }
        
        # Add missing sectors
        for sector in GICS_SECTORS:
            if sector not in analysis:
                benchmark = SP500_BENCHMARK_WEIGHTS.get(sector, 0)
                analysis[sector] = {
                    "status": "MISSING" if benchmark > 3 else "ABSENT",
                    "current": 0,
                    "benchmark": round(benchmark, 1),
                    "diff": round(-benchmark, 1)
                }
        
        return analysis
    
    def _calculate_concentration_risk(
        self,
        portfolio: Dict[str, float]
    ) -> str:
        """Calculate portfolio concentration risk level"""
        # Check top 3 holdings
        sorted_holdings = sorted(portfolio.values(), reverse=True)
        
        if len(sorted_holdings) >= 3:
            top3_concentration = sum(sorted_holdings[:3])
        else:
            top3_concentration = sum(sorted_holdings)
        
        # Risk levels
        if top3_concentration > 70:
            return "VERY HIGH - Top 3 holdings exceed 70%"
        elif top3_concentration > 50:
            return "HIGH - Top 3 holdings exceed 50%"
        elif top3_concentration > 35:
            return "MODERATE - Top 3 holdings exceed 35%"
        else:
            return "LOW - Well diversified"
    
    def get_top_holdings(
        self,
        portfolio: Dict[str, float],
        n: int = 5
    ) -> List[Tuple[str, float]]:
        """Get top N holdings by weight"""
        return sorted(
            portfolio.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
    
    def get_portfolio_summary(
        self,
        portfolio: Dict[str, float] = None
    ) -> str:
        """Generate human-readable portfolio summary"""
        if portfolio is None:
            portfolio = MOCK_PORTFOLIO
        
        top_holdings = self.get_top_holdings(portfolio, 3)
        
        summary = f"Portfolio of {len(portfolio)} positions. "
        summary += f"Top holdings: "
        summary += ", ".join([f"{ticker} ({weight}%)" for ticker, weight in top_holdings])
        
        return summary

