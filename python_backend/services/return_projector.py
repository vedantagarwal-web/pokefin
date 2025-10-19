"""
Return Projection Engine
Simple MVP for projecting portfolio returns with new allocations
"""

from typing import Dict, List, Tuple
from services.financial_datasets_client import FinancialDatasetsClient

class ReturnProjector:
    """Projects portfolio returns with new stock allocations"""
    
    def __init__(self):
        self.fd_client = FinancialDatasetsClient()
    
    async def project_portfolio_return(
        self,
        current_portfolio: Dict[str, float],  # {ticker: weight_pct}
        new_stock: str,
        new_allocation_pct: float,
        target_prices: Dict[str, float],  # {ticker: target_price}
        current_prices: Dict[str, float],  # {ticker: current_price}
        conviction: int = 7
    ) -> Dict:
        """
        Project portfolio returns after adding a new stock
        
        Args:
            current_portfolio: Current holdings {ticker: weight_pct}
            new_stock: Ticker of stock to add
            new_allocation_pct: Percentage to allocate to new stock
            target_prices: Target prices for all stocks
            current_prices: Current prices for all stocks
            conviction: Conviction score 1-10
        
        Returns:
            Dict with before/after projections
        """
        
        # Calculate current portfolio expected return
        current_return = 0
        for ticker, weight in current_portfolio.items():
            if ticker in target_prices and ticker in current_prices:
                stock_return = ((target_prices[ticker] - current_prices[ticker]) / 
                               current_prices[ticker] * 100)
                current_return += (weight / 100) * stock_return
        
        # Calculate new portfolio weights (scale down existing to make room)
        scale_factor = (100 - new_allocation_pct) / 100
        new_portfolio = {
            ticker: weight * scale_factor 
            for ticker, weight in current_portfolio.items()
        }
        new_portfolio[new_stock] = new_allocation_pct
        
        # Calculate new portfolio expected return
        new_return = 0
        for ticker, weight in new_portfolio.items():
            if ticker in target_prices and ticker in current_prices:
                stock_return = ((target_prices[ticker] - current_prices[ticker]) / 
                               current_prices[ticker] * 100)
                new_return += (weight / 100) * stock_return
        
        # Calculate new stock's expected return
        new_stock_return = 0
        if new_stock in target_prices and new_stock in current_prices:
            new_stock_return = ((target_prices[new_stock] - current_prices[new_stock]) / 
                               current_prices[new_stock] * 100)
        
        return {
            "current_portfolio_return": round(current_return, 2),
            "new_portfolio_return": round(new_return, 2),
            "improvement": round(new_return - current_return, 2),
            "new_stock_return": round(new_stock_return, 2),
            "new_allocation": new_allocation_pct,
            "new_portfolio_weights": {
                ticker: round(weight, 2) 
                for ticker, weight in new_portfolio.items()
            },
            "timeframe": "12 months",
            "conviction_adjusted_return": round(new_return * (conviction / 10), 2)
        }
    
    def generate_dca_schedule(
        self,
        total_amount: float,
        weeks: int = 4
    ) -> List[Dict]:
        """
        Generate dollar-cost averaging schedule
        
        Args:
            total_amount: Total amount to invest
            weeks: Number of weeks to spread investment
        
        Returns:
            List of investment tranches
        """
        amount_per_week = total_amount / weeks
        
        schedule = []
        for week in range(1, weeks + 1):
            schedule.append({
                "week": week,
                "amount": round(amount_per_week, 2),
                "percentage": round(100 / weeks, 1)
            })
        
        return schedule
    
    async def get_current_prices(self, tickers: List[str]) -> Dict[str, float]:
        """Fetch current prices for a list of tickers"""
        prices = {}
        
        for ticker in tickers:
            try:
                # Use Financial Datasets client to get price
                price_data = await self.fd_client.get_stock_price(ticker)
                if price_data and "price" in price_data:
                    prices[ticker] = price_data["price"]
                else:
                    # Fallback mock price
                    prices[ticker] = 100.0
            except Exception as e:
                print(f"⚠️ Could not fetch price for {ticker}: {e}")
                prices[ticker] = 100.0
        
        return prices
    
    def calculate_portfolio_value_projection(
        self,
        portfolio_value: float,
        expected_return_pct: float,
        months: int = 12
    ) -> Dict:
        """Calculate future portfolio value based on expected return"""
        
        # Simple compound return calculation
        monthly_return = expected_return_pct / 12 / 100
        future_value = portfolio_value * ((1 + monthly_return) ** months)
        
        return {
            "current_value": round(portfolio_value, 2),
            "future_value": round(future_value, 2),
            "gain": round(future_value - portfolio_value, 2),
            "return_pct": round((future_value - portfolio_value) / portfolio_value * 100, 2),
            "timeframe_months": months
        }
    
    def calculate_recommended_allocation(
        self,
        portfolio_value: float,
        risk_tolerance: str,
        conviction: int,
        sector_exposure: Dict[str, float]
    ) -> float:
        """
        Calculate recommended allocation percentage for new stock
        
        Args:
            portfolio_value: Total portfolio value
            risk_tolerance: conservative, moderate, aggressive
            conviction: 1-10 conviction score
            sector_exposure: Current sector exposures
        
        Returns:
            Recommended allocation percentage
        """
        
        # Base allocation by risk tolerance
        base_allocations = {
            "conservative": 5.0,  # 5% for conservative
            "moderate": 8.0,      # 8% for moderate
            "aggressive": 12.0    # 12% for aggressive
        }
        
        base = base_allocations.get(risk_tolerance, 8.0)
        
        # Adjust based on conviction (±30%)
        conviction_factor = 0.7 + (conviction / 10) * 0.6  # Range: 0.7 to 1.3
        
        recommended = base * conviction_factor
        
        # Cap at reasonable limits
        return round(min(max(recommended, 3.0), 15.0), 1)

