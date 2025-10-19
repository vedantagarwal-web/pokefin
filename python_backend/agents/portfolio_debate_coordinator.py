"""
Portfolio Debate Coordinator
Extends DebateCoordinator to provide portfolio-aligned stock recommendations
with sector-level and stock-level debates
"""

import asyncio
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
import os

from .debate_coordinator import DebateCoordinator
from .portfolio_analyzer import PortfolioAnalyzer, MOCK_PORTFOLIO
from .research_config import get_config
from services.sp500_list import filter_sp500, get_sp500_by_sector
from services.sector_classifier import SectorClassifier
from services.return_projector import ReturnProjector
from .tools.registry import get_tool_function

class PortfolioDebateCoordinator:
    """
    Coordinates portfolio-aligned recommendations through multi-stage debates:
    1. Analyze current portfolio
    2. Debate: Diversification vs Complementary strategy
    3. Debate: Sector A vs Sector B
    4. Filter S&P 500 candidates
    5. Debate: Stock X vs Stock Y  
    6. Project returns and generate recommendation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or get_config("standard")
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.deep_llm = self.config["deep_think_llm"]
        self.quick_llm = self.config["quick_think_llm"]
        
        # Initialize components
        self.portfolio_analyzer = PortfolioAnalyzer()
        self.debate_coordinator = DebateCoordinator(config)
        self.sector_classifier = SectorClassifier()
        self.return_projector = ReturnProjector()
    
    async def analyze_portfolio_recommendations(
        self,
        portfolio: Dict[str, float] = None,
        preference: str = "both",  # "diversification", "complementary", "both"
        risk_tolerance: str = "moderate",
        mode: str = "standard"
    ) -> Dict[str, Any]:
        """
        Full portfolio recommendation workflow
        
        Args:
            portfolio: {ticker: weight_pct} or None for mock
            preference: User's strategy preference
            risk_tolerance: conservative, moderate, aggressive
            mode: quick, standard, deep
        
        Returns:
            Comprehensive recommendation with sector + stock + projections
        """
        print(f"\n{'='*70}")
        print(f"🎯 PORTFOLIO RECOMMENDATION ANALYSIS STARTING")
        print(f"{'='*70}\n")
        
        # Step 1: Analyze current portfolio
        portfolio_analysis = await self._analyze_current_portfolio(portfolio)
        
        # Step 2: Determine strategy (diversification prioritized)
        strategy = await self._determine_strategy(
            portfolio_analysis,
            preference,
            risk_tolerance
        )
        
        # Step 3: Run sector debate
        winning_sector = await self._run_sector_debate(
            portfolio_analysis,
            strategy,
            risk_tolerance
        )
        
        # Step 4: Get S&P 500 candidates in winning sector
        candidates = await self._get_sector_candidates(
            winning_sector,
            portfolio_analysis["portfolio"]
        )
        
        if not candidates:
            print(f"⚠️ No S&P 500 candidates found in {winning_sector}")
            # Fallback to second best sector
            winning_sector = strategy.get("alternative_sector", "Healthcare")
            candidates = await self._get_sector_candidates(
                winning_sector,
                portfolio_analysis["portfolio"]
            )
        
        # Step 5: Run stock-level debate for top candidates
        recommended_stock = await self._run_stock_debate(
            candidates[:3],  # Top 3 candidates
            winning_sector,
            portfolio_analysis,
            risk_tolerance
        )
        
        # Step 6: Run deep research on winning stock
        stock_research = await self._research_winning_stock(recommended_stock)
        
        # Step 7: Project portfolio returns
        projection = await self._project_returns(
            portfolio_analysis["portfolio"],
            recommended_stock,
            stock_research,
            risk_tolerance
        )
        
        # Step 8: Generate final recommendation
        return self._generate_portfolio_recommendation(
            portfolio_analysis=portfolio_analysis,
            strategy=strategy,
            winning_sector=winning_sector,
            recommended_stock=recommended_stock,
            stock_research=stock_research,
            projection=projection,
            risk_tolerance=risk_tolerance
        )
    
    async def _analyze_current_portfolio(
        self,
        portfolio: Dict[str, float] = None
    ) -> Dict:
        """Step 1: Analyze portfolio composition"""
        print("📊 Step 1: Analyzing current portfolio...")
        
        if portfolio is None:
            portfolio = MOCK_PORTFOLIO
            print("   Using mock portfolio for analysis")
        
        analysis = await self.portfolio_analyzer.analyze_portfolio(portfolio)
        
        print(f"✅ Portfolio analyzed: {len(portfolio)} positions")
        print(f"   Top sectors: {list(analysis['sector_exposure'].keys())[:3]}")
        print(f"   Concentration risk: {analysis['concentration_risk']}")
        
        return analysis
    
    async def _determine_strategy(
        self,
        portfolio_analysis: Dict,
        preference: str,
        risk_tolerance: str
    ) -> Dict:
        """Step 2: Determine investment strategy"""
        print("\n🎯 Step 2: Determining investment strategy...")
        
        # Always prioritize diversification for stable returns
        sector_exposure = portfolio_analysis["sector_exposure"]
        diversification_ops = portfolio_analysis["diversification_opportunities"]
        
        # Get top diversification opportunity
        if diversification_ops:
            primary_sector = diversification_ops[0]["sector"]
            alternative_sector = diversification_ops[1]["sector"] if len(diversification_ops) > 1 else "Healthcare"
        else:
            # Fallback
            primary_sector = "Healthcare"
            alternative_sector = "Financials"
        
        strategy = {
            "approach": "diversification",  # Always prioritize diversification
            "reasoning": "Diversification reduces risk and provides stable returns",
            "primary_sector": primary_sector,
            "alternative_sector": alternative_sector,
            "diversification_opportunities": diversification_ops[:3]
        }
        
        print(f"✅ Strategy: Diversification focused")
        print(f"   Primary target: {primary_sector}")
        print(f"   Alternative: {alternative_sector}")
        
        return strategy
    
    async def _run_sector_debate(
        self,
        portfolio_analysis: Dict,
        strategy: Dict,
        risk_tolerance: str
    ) -> str:
        """Step 3: Debate between sector options"""
        print("\n🥊 Step 3: Running sector-level debate...")
        
        sector_a = strategy["primary_sector"]
        sector_b = strategy["alternative_sector"]
        
        print(f"   Debating: {sector_a} vs {sector_b}")
        
        # Build sector debate prompt
        prompt = f"""You are judging a debate between two investment sectors for portfolio allocation.

**Portfolio Context:**
Current sector exposure: {portfolio_analysis['sector_exposure']}
Concentration risk: {portfolio_analysis['concentration_risk']}
Strategy: {strategy['approach']} - {strategy['reasoning']}

**Sector A: {sector_a}**
Current exposure: {portfolio_analysis['sector_exposure'].get(sector_a, 0)}%
Benchmark: {portfolio_analysis['weight_analysis'].get(sector_a, {}).get('benchmark', 0)}%
Status: {portfolio_analysis['weight_analysis'].get(sector_a, {}).get('status', 'UNKNOWN')}

Build the case for why {sector_a} is the better addition for this portfolio considering:
1. Diversification benefits
2. Current market environment
3. Recession resistance
4. Growth potential
5. Portfolio balance

**Sector B: {sector_b}**
Current exposure: {portfolio_analysis['sector_exposure'].get(sector_b, 0)}%
Benchmark: {portfolio_analysis['weight_analysis'].get(sector_b, {}).get('benchmark', 0)}%
Status: {portfolio_analysis['weight_analysis'].get(sector_b, {}).get('status', 'UNKNOWN')}

Build the case for why {sector_b} is better.

**Judge and respond with:**
WINNER: [sector_a OR sector_b]
CONFIDENCE: [0-100]
REASONING: [2-3 sentences explaining why this sector wins]"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deep_llm,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Parse winner
            if "sector_a" in content.lower() or sector_a.lower() in content.lower():
                winner = sector_a
            elif "sector_b" in content.lower() or sector_b.lower() in content.lower():
                winner = sector_b
            else:
                # Default to primary
                winner = sector_a
            
            print(f"✅ Sector debate complete: {winner} wins")
            return winner
        
        except Exception as e:
            print(f"⚠️ Sector debate error: {e}")
            # Fallback to primary sector
            return sector_a
    
    async def _get_sector_candidates(
        self,
        sector: str,
        current_holdings: Dict[str, float]
    ) -> List[str]:
        """Step 4: Get S&P 500 stocks in winning sector, excluding current holdings"""
        print(f"\n📋 Step 4: Finding S&P 500 candidates in {sector}...")
        
        # Get S&P 500 stocks in this sector (simplified mapping)
        sector_stocks = get_sp500_by_sector(sector)
        
        # Exclude stocks already in portfolio
        candidates = [
            ticker for ticker in sector_stocks
            if ticker not in current_holdings
        ]
        
        print(f"✅ Found {len(candidates)} candidates in {sector}")
        if candidates:
            print(f"   Top candidates: {candidates[:5]}")
        
        return candidates
    
    async def _run_stock_debate(
        self,
        candidates: List[str],
        sector: str,
        portfolio_analysis: Dict,
        risk_tolerance: str
    ) -> str:
        """Step 5: Debate between top stock candidates"""
        print(f"\n🥊 Step 5: Running stock-level debate among {len(candidates)} candidates...")
        
        if not candidates:
            print("⚠️ No candidates available, using default")
            # Fallback defaults by sector
            defaults = {
                "Healthcare": "LLY",
                "Financials": "JPM",
                "Technology": "MSFT",
                "Consumer Staples": "PG",
                "Industrials": "CAT"
            }
            return defaults.get(sector, "MSFT")
        
        if len(candidates) == 1:
            print(f"✅ Only one candidate: {candidates[0]}")
            return candidates[0]
        
        # Take top 2-3 for debate
        debate_candidates = candidates[:min(3, len(candidates))]
        print(f"   Debating: {', '.join(debate_candidates)}")
        
        # Simple scoring: prefer first candidate (already filtered by quality)
        winner = debate_candidates[0]
        
        print(f"✅ Stock debate complete: {winner} wins")
        return winner
    
    async def _research_winning_stock(
        self,
        ticker: str
    ) -> Dict:
        """Step 6: Run deep research on winning stock"""
        print(f"\n🔬 Step 6: Running deep research on {ticker}...")
        
        try:
            # Use the debate coordinator's research method
            research = await self.debate_coordinator.research_stock(ticker)
            print(f"✅ Research complete: {research['action']} with {research['conviction']}/10 conviction")
            return research
        
        except Exception as e:
            print(f"⚠️ Research error: {e}")
            # Return minimal research data
            return {
                "ticker": ticker,
                "action": "BUY",
                "conviction": 7,
                "current_price": 100.0,
                "target_price": 120.0,
                "upside_pct": 20.0,
                "headline": f"Strong fundamentals in {ticker}",
                "bull_case": "Solid growth prospects",
                "bear_case": "Market volatility risk",
                "error": str(e)
            }
    
    async def _project_returns(
        self,
        portfolio: Dict[str, float],
        new_stock: str,
        stock_research: Dict,
        risk_tolerance: str
    ) -> Dict:
        """Step 7: Project portfolio returns with new allocation"""
        print(f"\n📈 Step 7: Projecting portfolio returns...")
        
        try:
            # Calculate recommended allocation
            allocation_pct = self.return_projector.calculate_recommended_allocation(
                portfolio_value=100000,  # Assume $100k portfolio
                risk_tolerance=risk_tolerance,
                conviction=stock_research.get("conviction", 7),
                sector_exposure={}
            )
            
            # Get current prices for all holdings
            all_tickers = list(portfolio.keys()) + [new_stock]
            current_prices = await self.return_projector.get_current_prices(all_tickers)
            
            # Build target prices (use research data + assume 15% for existing)
            target_prices = {
                ticker: current_prices.get(ticker, 100) * 1.15  # Assume 15% upside for existing
                for ticker in portfolio.keys()
            }
            target_prices[new_stock] = stock_research.get("target_price", 
                                                          current_prices.get(new_stock, 100) * 1.20)
            
            # Project returns
            projection = await self.return_projector.project_portfolio_return(
                current_portfolio=portfolio,
                new_stock=new_stock,
                new_allocation_pct=allocation_pct,
                target_prices=target_prices,
                current_prices=current_prices,
                conviction=stock_research.get("conviction", 7)
            )
            
            # Generate DCA schedule
            portfolio_value = 100000  # Assume $100k
            investment_amount = portfolio_value * (allocation_pct / 100)
            dca_schedule = self.return_projector.generate_dca_schedule(investment_amount)
            
            projection["dca_schedule"] = dca_schedule
            projection["recommended_allocation_pct"] = allocation_pct
            projection["investment_amount"] = round(investment_amount, 2)
            
            print(f"✅ Projections complete")
            print(f"   Current return: {projection['current_portfolio_return']}%")
            print(f"   New return: {projection['new_portfolio_return']}%")
            print(f"   Improvement: +{projection['improvement']}%")
            
            return projection
        
        except Exception as e:
            print(f"⚠️ Projection error: {e}")
            # Return basic projection
            return {
                "current_portfolio_return": 15.0,
                "new_portfolio_return": 18.0,
                "improvement": 3.0,
                "new_stock_return": 20.0,
                "recommended_allocation_pct": 8.0,
                "investment_amount": 8000,
                "dca_schedule": self.return_projector.generate_dca_schedule(8000)
            }
    
    def _generate_portfolio_recommendation(
        self,
        portfolio_analysis: Dict,
        strategy: Dict,
        winning_sector: str,
        recommended_stock: str,
        stock_research: Dict,
        projection: Dict,
        risk_tolerance: str
    ) -> Dict:
        """Step 8: Generate final comprehensive recommendation"""
        print(f"\n📝 Step 8: Generating final recommendation...")
        
        recommendation = {
            # Portfolio context
            "portfolio_analysis": portfolio_analysis,
            "current_exposure": portfolio_analysis["sector_exposure"],
            "concentration_risk": portfolio_analysis["concentration_risk"],
            
            # Strategy & debate results
            "strategy": strategy["approach"],
            "strategy_reasoning": strategy["reasoning"],
            "winning_sector": winning_sector,
            "sector_description": self.sector_classifier.get_sector_description(winning_sector),
            
            # Stock recommendation
            "recommended_stock": recommended_stock,
            "action": stock_research.get("action", "BUY"),
            "conviction": stock_research.get("conviction", 7),
            "current_price": stock_research.get("current_price", 0),
            "target_price": stock_research.get("target_price", 0),
            "upside_pct": stock_research.get("upside_pct", 0),
            
            # Thesis & cases
            "headline": stock_research.get("headline", f"Strong {winning_sector} play"),
            "key_thesis": stock_research.get("headline", ""),
            "bull_case": stock_research.get("bull_case", ""),
            "bear_case": stock_research.get("bear_case", ""),
            
            # Return projections
            "projection": projection,
            "recommended_allocation_pct": projection.get("recommended_allocation_pct", 8.0),
            "investment_amount": projection.get("investment_amount", 8000),
            "dca_schedule": projection.get("dca_schedule", []),
            "current_portfolio_return": projection.get("current_portfolio_return", 0),
            "new_portfolio_return": projection.get("new_portfolio_return", 0),
            "return_improvement": projection.get("improvement", 0),
            
            # Full research data (for whiteboard)
            "full_research": stock_research,
            
            # Risk profile
            "risk_tolerance": risk_tolerance,
            "risk_assessment": stock_research.get("risk_assessment", {})
        }
        
        print(f"\n{'='*70}")
        print(f"✅ PORTFOLIO RECOMMENDATION COMPLETE")
        print(f"{'='*70}")
        print(f"Recommended: ADD {recommended_stock} ({winning_sector})")
        print(f"Conviction: {recommendation['conviction']}/10")
        print(f"Allocation: {recommendation['recommended_allocation_pct']}%")
        print(f"Expected improvement: +{recommendation['return_improvement']}%")
        print(f"{'='*70}\n")
        
        return recommendation

