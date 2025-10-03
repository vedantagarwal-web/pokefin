"""
Bull vs Bear Debate System
Inspired by TradingAgents' researcher team approach

This coordinator runs structured debates between bull and bear perspectives
to generate high-conviction stock recommendations.
"""

import asyncio
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
import os
import json

from .research_config import get_config
from .tools.registry import get_tool_function


class DebateCoordinator:
    """
    Coordinates multi-agent debates for stock research.
    
    Flow:
    1. Gather comprehensive signals (Reddit, Twitter, 13F, etc.)
    2. Run specialist analysis (Fundamental, Technical, Sentiment)
    3. Bull agent builds case for buying
    4. Bear agent builds case for avoiding
    5. Multi-round structured debate
    6. Calculate conviction score (1-10)
    7. Generate simple recommendation + detailed whiteboard
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or get_config("standard")
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.deep_llm = self.config["deep_think_llm"]
        self.quick_llm = self.config["quick_think_llm"]
        self.max_rounds = self.config["max_debate_rounds"]
    
    async def _call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Helper to call a tool function"""
        tool_func = get_tool_function(tool_name)
        if tool_func:
            try:
                return await tool_func(**args)
            except Exception as e:
                print(f"⚠️ Error calling {tool_name}: {e}")
                return {"error": str(e)}
        return {"error": f"Tool {tool_name} not found"}
    
    async def research_stock(self, ticker: str) -> Dict[str, Any]:
        """
        Full research workflow with debate.
        Returns comprehensive research report.
        """
        print(f"\n{'='*60}")
        print(f"🔬 DEEP RESEARCH STARTING: {ticker}")
        print(f"{'='*60}\n")
        
        # Step 1: Gather all signals
        signals = await self._gather_comprehensive_signals(ticker)
        
        # Step 2: Specialist analysis
        specialist_analysis = await self._run_specialist_analysis(ticker, signals)
        
        # Step 3: Build initial cases
        bull_case = await self._build_bull_case(ticker, signals, specialist_analysis)
        bear_case = await self._build_bear_case(ticker, signals, specialist_analysis)
        
        # Step 4: Run debate
        debate_result = await self._run_debate(ticker, bull_case, bear_case, signals)
        
        # Step 5: Calculate conviction
        conviction = self._calculate_conviction(debate_result, signals, specialist_analysis)
        
        # Step 6: Risk assessment
        risk_assessment = await self._assess_risks(ticker, conviction, signals, debate_result)
        
        # Step 7: Generate outputs
        return self._generate_research_report(
            ticker=ticker,
            signals=signals,
            specialist_analysis=specialist_analysis,
            bull_case=bull_case,
            bear_case=bear_case,
            debate_result=debate_result,
            conviction=conviction,
            risk_assessment=risk_assessment
        )
    
    async def _gather_comprehensive_signals(self, ticker: str) -> Dict[str, Any]:
        """Gather signals from all configured sources"""
        print(f"📡 Gathering signals for {ticker}...")
        
        # Parallel signal gathering
        signal_tasks = []
        
        # Always gather these - comprehensive data like TradingAgents
        signal_tasks.extend([
            self._call_tool("get_stock_price", {"ticker": ticker, "include_chart": False}),
            self._call_tool("get_financial_metrics", {"ticker": ticker}),
            self._call_tool("get_financials", {"ticker": ticker}),  # Add actual financial statements
            self._call_tool("get_company_news", {"ticker": ticker, "limit": 10}),
            self._call_tool("get_analyst_ratings", {"ticker": ticker}),  # Add analyst ratings
            self._call_tool("get_peer_comparison", {"ticker": ticker}),  # Add peer comparison
            self._call_tool("get_historical_financials", {"ticker": ticker, "periods": 8}),  # Historical trends
            self._call_tool("get_balance_sheet", {"ticker": ticker}),  # Balance sheet
            self._call_tool("get_cash_flow", {"ticker": ticker}),  # Cash flow statement
            self._call_tool("get_earnings_highlights", {"ticker": ticker}),  # Earnings insights
        ])
        
        # Conditional based on config
        if self.config.get("use_reddit"):
            signal_tasks.append(self._call_tool("get_reddit_sentiment", {"ticker": ticker}))
        
        if self.config.get("use_twitter"):
            signal_tasks.append(self._call_tool("get_twitter_sentiment", {"ticker": ticker}))
        
        if self.config.get("use_13f"):
            signal_tasks.append(self._call_tool("get_13f_changes", {"ticker": ticker}))
        
        if self.config.get("use_insider"):
            signal_tasks.append(self._call_tool("get_insider_trades", {"ticker": ticker, "limit": 10}))
        
        if self.config.get("use_options"):
            signal_tasks.append(self._call_tool("get_unusual_activity", {"ticker": ticker}))
        
        # Execute all in parallel
        results = await asyncio.gather(*signal_tasks, return_exceptions=True)
        
        # Organize results
        signals = {
            "ticker": ticker,
            "price": results[0] if len(results) > 0 else None,
            "financial_metrics": results[1] if len(results) > 1 else None,
            "financials": results[2] if len(results) > 2 else None,  # Actual financial statements
            "news": results[3] if len(results) > 3 else None,
            "analyst_ratings": results[4] if len(results) > 4 else None,
            "peer_comparison": results[5] if len(results) > 5 else None,
            "historical_financials": results[6] if len(results) > 6 else None,  # Historical trends
            "balance_sheet": results[7] if len(results) > 7 else None,  # Balance sheet
            "cash_flow": results[8] if len(results) > 8 else None,  # Cash flow
            "earnings_highlights": results[9] if len(results) > 9 else None,  # Earnings insights
        }
        
        # Add optional signals
        idx = 10  # Start after base signals
        if self.config.get("use_reddit") and idx < len(results):
            signals["reddit_sentiment"] = results[idx]
            idx += 1
        if self.config.get("use_twitter") and idx < len(results):
            signals["twitter_sentiment"] = results[idx]
            idx += 1
        if self.config.get("use_13f") and idx < len(results):
            signals["institutional_activity"] = results[idx]
            idx += 1
        if self.config.get("use_insider") and idx < len(results):
            signals["insider_trades"] = results[idx]
            idx += 1
        if self.config.get("use_options") and idx < len(results):
            signals["unusual_activity"] = results[idx]
            idx += 1
        
        print(f"✅ Gathered {len([k for k in signals.keys() if k != 'ticker'])} signal sources")
        return signals
    
    async def _run_specialist_analysis(self, ticker: str, signals: Dict) -> Dict[str, Any]:
        """Run quick specialist analysis"""
        print(f"🧠 Running specialist analysis...")
        
        # For now, return structured analysis based on signals
        # In the future, could call actual specialist agents
        return {
            "fundamental_score": self._quick_fundamental_score(signals),
            "technical_score": self._quick_technical_score(signals),
            "sentiment_score": self._quick_sentiment_score(signals),
        }
    
    def _quick_fundamental_score(self, signals: Dict) -> float:
        """Quick fundamental scoring (0-10)"""
        # Check both financial_metrics and financials
        financials = signals.get("financial_metrics", {}) or signals.get("financials", {})
        if not financials or "error" in financials:
            return 5.0
        
        score = 5.0  # Start neutral
        
        # Helper to safely get numeric values
        def safe_num(key, default=0):
            val = financials.get(key, default)
            return val if val is not None else default
        
        # Positive factors
        if safe_num("profit_margin") > 15:
            score += 1
        if safe_num("revenue_growth") > 20:
            score += 1
        if safe_num("eps") > 0:
            score += 0.5
        
        # Negative factors
        if safe_num("pe_ratio") > 40:
            score -= 1
        if safe_num("debt_to_equity") > 2:
            score -= 0.5
        
        return max(0, min(10, score))
    
    def _quick_technical_score(self, signals: Dict) -> float:
        """Quick technical scoring (0-10)"""
        # Simplified - would use actual technical analysis in production
        return 6.0  # Placeholder
    
    def _quick_sentiment_score(self, signals: Dict) -> float:
        """Quick sentiment scoring (0-10)"""
        score = 5.0  # Start neutral
        
        # Reddit sentiment
        reddit = signals.get("reddit_sentiment", {})
        if reddit and "sentiment_score" in reddit:
            score += (reddit["sentiment_score"] - 0.5) * 4  # -2 to +2
        
        # Twitter sentiment
        twitter = signals.get("twitter_sentiment", {})
        if twitter and "sentiment_score" in twitter:
            score += (twitter["sentiment_score"] - 0.5) * 4
        
        # Institutional activity
        institutional = signals.get("institutional_activity", {})
        if institutional:
            activity = institutional.get("activity_level", "NEUTRAL")
            if "STRONG BUYING" in activity:
                score += 2
            elif "NET BUYING" in activity:
                score += 1
            elif "NET SELLING" in activity:
                score -= 1
            elif "STRONG SELLING" in activity:
                score -= 2
        
        return max(0, min(10, score))
    
    async def _build_bull_case(self, ticker: str, signals: Dict, analysis: Dict) -> str:
        """Build comprehensive bull case"""
        print(f"🐂 Building bull case...")
        
        prompt = f"""You are a BULLISH analyst building the strongest possible case for buying {ticker}.

Analyze these signals and build a compelling argument for why this is a BUY:

**Market Data:**
{self._format_signals_for_prompt(signals)}

**Specialist Analysis:**
- Fundamental Score: {analysis['fundamental_score']}/10
- Technical Score: {analysis['technical_score']}/10
- Sentiment Score: {analysis['sentiment_score']}/10

Build your bull case with:
1. **Main Thesis** (one powerful sentence)
2. **Key Strengths** (top 3-5 bullish points with evidence)
3. **Catalysts** (upcoming events that could drive price higher)
4. **Price Target** (specific number with justification)

Be specific, cite the data, and make it compelling. This needs to be convincing!"""

        response = await self.client.chat.completions.create(
            model=self.deep_llm,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        bull_case = response.choices[0].message.content
        print(f"✅ Bull case complete ({len(bull_case)} chars)")
        return bull_case
    
    async def _build_bear_case(self, ticker: str, signals: Dict, analysis: Dict) -> str:
        """Build comprehensive bear case"""
        print(f"🐻 Building bear case...")
        
        prompt = f"""You are a BEARISH analyst building the strongest possible case for avoiding {ticker}.

Analyze these signals and build a compelling argument for why this is NOT a good buy:

**Market Data:**
{self._format_signals_for_prompt(signals)}

**Specialist Analysis:**
- Fundamental Score: {analysis['fundamental_score']}/10
- Technical Score: {analysis['technical_score']}/10
- Sentiment Score: {analysis['sentiment_score']}/10

Build your bear case with:
1. **Main Concern** (one critical sentence)
2. **Key Risks** (top 3-5 bearish points with evidence)
3. **Warning Signs** (red flags in the data)
4. **Downside Scenario** (what could go wrong)

Be specific, cite the data, and make it compelling. Play devil's advocate!"""

        response = await self.client.chat.completions.create(
            model=self.deep_llm,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        bear_case = response.choices[0].message.content
        print(f"✅ Bear case complete ({len(bear_case)} chars)")
        return bear_case
    
    async def _run_debate(
        self, 
        ticker: str, 
        bull_case: str, 
        bear_case: str, 
        signals: Dict
    ) -> Dict[str, Any]:
        """Run multi-round debate between bull and bear"""
        print(f"\n🥊 DEBATE STARTING ({self.max_rounds} rounds)...")
        
        debate_transcript = []
        
        for round_num in range(self.max_rounds):
            print(f"\n--- Round {round_num + 1}/{self.max_rounds} ---")
            
            # Bull responds to bear's points
            bull_response = await self._bull_rebuttal(
                ticker, bull_case, bear_case, debate_transcript
            )
            
            # Bear responds to bull's points
            bear_response = await self._bear_rebuttal(
                ticker, bear_case, bull_case, debate_transcript
            )
            
            debate_transcript.append({
                "round": round_num + 1,
                "bull": bull_response,
                "bear": bear_response
            })
            
            print(f"✅ Round {round_num + 1} complete")
        
        # Judge the debate
        winner = await self._judge_debate(ticker, bull_case, bear_case, debate_transcript, signals)
        
        return {
            "transcript": debate_transcript,
            "winner": winner["side"],  # "bull" or "bear"
            "winning_argument": winner["best_argument"],
            "confidence": winner["confidence"],  # 0-100
            "key_points": winner["key_points"]
        }
    
    async def _bull_rebuttal(self, ticker: str, bull_case: str, bear_case: str, transcript: List) -> str:
        """Bull agent responds to bear's concerns"""
        
        previous_debate = "\n".join([
            f"Round {r['round']} Bull: {r['bull']}\nRound {r['round']} Bear: {r['bear']}"
            for r in transcript
        ]) if transcript else "No previous rounds"
        
        prompt = f"""You are the BULL analyst for {ticker}. The bear has raised concerns.

**Your Original Case:**
{bull_case}

**Bear's Case:**
{bear_case}

**Previous Debate:**
{previous_debate}

Respond to the bear's strongest points. Be specific and use data. Acknowledge valid concerns but show why the bull case still wins."""

        response = await self.client.chat.completions.create(
            model=self.quick_llm,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    async def _bear_rebuttal(self, ticker: str, bear_case: str, bull_case: str, transcript: List) -> str:
        """Bear agent responds to bull's points"""
        
        previous_debate = "\n".join([
            f"Round {r['round']} Bull: {r['bull']}\nRound {r['round']} Bear: {r['bear']}"
            for r in transcript
        ]) if transcript else "No previous rounds"
        
        prompt = f"""You are the BEAR analyst for {ticker}. The bull has made strong arguments.

**Your Original Case:**
{bear_case}

**Bull's Case:**
{bull_case}

**Previous Debate:**
{previous_debate}

Respond to the bull's strongest points. Be specific and use data. Acknowledge strengths but show why the risks outweigh the rewards."""

        response = await self.client.chat.completions.create(
            model=self.quick_llm,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    async def _judge_debate(
        self, 
        ticker: str, 
        bull_case: str, 
        bear_case: str, 
        transcript: List, 
        signals: Dict
    ) -> Dict[str, Any]:
        """Judge who won the debate"""
        print(f"\n⚖️ Judging debate...")
        
        debate_summary = f"""
**Bull's Opening:**
{bull_case}

**Bear's Opening:**
{bear_case}

**Debate Rounds:**
{chr(10).join([f"Round {r['round']} - Bull: {r['bull']}\nRound {r['round']} - Bear: {r['bear']}" for r in transcript])}
"""
        
        prompt = f"""You are an impartial judge evaluating a stock debate for {ticker}.

{debate_summary}

**Actual Market Data:**
{self._format_signals_for_prompt(signals)}

Judge the debate and respond in this exact format:

WINNER: [bull/bear]
CONFIDENCE: [0-100 number only]
BEST_ARGUMENT: [one sentence of the winning side's strongest point]
KEY_POINT_1: [key point]
KEY_POINT_2: [key point]
KEY_POINT_3: [key point]

Be objective. Consider:
1. Strength of evidence
2. Data support
3. Logic of arguments
4. Risk/reward balance"""

        response = await self.client.chat.completions.create(
            model=self.deep_llm,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        
        # Parse response
        content = response.choices[0].message.content
        lines = content.strip().split('\n')
        
        winner = "bull"
        confidence = 50
        best_argument = ""
        key_points = []
        
        for line in lines:
            if line.startswith("WINNER:"):
                winner = line.split(":", 1)[1].strip().lower()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = int(line.split(":", 1)[1].strip())
                except:
                    confidence = 50
            elif line.startswith("BEST_ARGUMENT:"):
                best_argument = line.split(":", 1)[1].strip()
            elif line.startswith("KEY_POINT"):
                key_points.append(line.split(":", 1)[1].strip())
        
        print(f"✅ Winner: {winner.upper()} (Confidence: {confidence}%)")
        
        return {
            "side": winner,
            "confidence": confidence,
            "best_argument": best_argument,
            "key_points": key_points
        }
    
    def _calculate_conviction(
        self, 
        debate_result: Dict, 
        signals: Dict, 
        analysis: Dict
    ) -> int:
        """Calculate conviction score 1-10"""
        print(f"\n📊 Calculating conviction score...")
        
        # Base score from debate winner confidence
        base_score = debate_result["confidence"] / 10  # 0-10
        
        # Adjust based on signal strength
        signal_boost = 0
        
        # Strong social sentiment
        reddit = signals.get("reddit_sentiment", {})
        if reddit.get("sentiment_score", 0.5) > 0.75:
            signal_boost += 1
        elif reddit.get("sentiment_score", 0.5) < 0.25:
            signal_boost -= 1
        
        # Institutional activity
        institutional = signals.get("institutional_activity", {})
        if "STRONG BUYING" in institutional.get("activity_level", ""):
            signal_boost += 1.5
        elif "STRONG SELLING" in institutional.get("activity_level", ""):
            signal_boost -= 1.5
        
        # Unusual options activity
        unusual = signals.get("unusual_activity", {})
        if unusual.get("unusual_detected") and unusual.get("bias") == "BULLISH":
            signal_boost += 0.5
        elif unusual.get("unusual_detected") and unusual.get("bias") == "BEARISH":
            signal_boost -= 0.5
        
        # Combine scores
        conviction = base_score + signal_boost
        
        # Adjust for bear case wins (inverse the score)
        if debate_result["winner"] == "bear":
            conviction = 10 - conviction
        
        # Clamp to 1-10
        conviction = max(1, min(10, round(conviction)))
        
        print(f"✅ Conviction: {conviction}/10")
        return conviction
    
    async def _assess_risks(
        self, 
        ticker: str, 
        conviction: int, 
        signals: Dict, 
        debate_result: Dict
    ) -> Dict[str, Any]:
        """Assess risks"""
        print(f"⚠️ Assessing risks...")
        
        # Get calculated P/E from signals
        financials = signals.get("financials", {})
        metrics = signals.get("financial_metrics", {})
        price_info = signals.get("price", {})
        
        # Calculate annualized P/E
        eps = financials.get("eps") or metrics.get("eps")
        if eps and financials.get("period") == "quarterly":
            eps_annual = eps * 4
        else:
            eps_annual = eps
        
        pe_ratio = None
        if eps_annual and eps_annual > 0 and price_info.get("price"):
            pe_ratio = price_info["price"] / eps_annual
        
        # Better P/E risk thresholds
        # < 15: LOW, 15-30: MEDIUM, 30-50: HIGH, > 50: VERY HIGH, > 100: EXTREME
        valuation_risk = "LOW"
        if pe_ratio:
            if pe_ratio > 100:
                valuation_risk = "EXTREME"
            elif pe_ratio > 50:
                valuation_risk = "VERY HIGH"
            elif pe_ratio > 30:
                valuation_risk = "HIGH"
            elif pe_ratio > 15:
                valuation_risk = "MEDIUM"
        
        # Assess volatility from price change
        day_change_pct = abs(price_info.get("day_change_percent", 0) or 0)
        volatility_risk = "HIGH" if day_change_pct > 5 else "MEDIUM" if day_change_pct > 2 else "LOW"
        
        # Market risk - use conviction score
        market_risk = "HIGH" if conviction < 4 else "MEDIUM" if conviction < 7 else "LOW"
        
        risks = {
            "valuation_risk": valuation_risk,
            "pe_ratio": pe_ratio,  # Include actual P/E for reference
            "volatility_risk": volatility_risk,
            "market_risk": market_risk,
        }
        
        return risks
    
    def _generate_research_report(
        self,
        ticker: str,
        signals: Dict,
        specialist_analysis: Dict,
        bull_case: str,
        bear_case: str,
        debate_result: Dict,
        conviction: int,
        risk_assessment: Dict
    ) -> Dict[str, Any]:
        """Generate final research report"""
        print(f"\n📝 Generating research report...")
        
        # Determine action
        if conviction >= 8:
            action = "STRONG BUY"
        elif conviction >= 7:
            action = "BUY"
        elif conviction >= 4:
            action = "HOLD"
        elif conviction >= 2:
            action = "SELL"
        else:
            action = "STRONG SELL"
        
        # Simple headline
        headline = debate_result["winning_argument"]
        
        # Current price
        price_data = signals.get("price", {})
        current_price = price_data.get("price", 0)
        
        # Estimate target (simplified)
        if action in ["BUY", "STRONG BUY"]:
            target_price = current_price * 1.25  # +25% for buys
        elif action == "HOLD":
            target_price = current_price * 1.05  # +5% for holds
        else:
            target_price = current_price * 0.85  # -15% for sells
        
        upside = ((target_price - current_price) / current_price * 100) if current_price > 0 else 0
        
        # Extract complete data for display
        complete_data = self._extract_complete_data(signals)
        
        report = {
            "ticker": ticker,
            "recommendation": action,  # For compatibility
            "action": action,
            "conviction": conviction,
            "current_price": round(current_price, 2),
            "target_price": round(target_price, 2),
            "upside_pct": round(upside, 1),
            
            # Simple view
            "headline": headline,
            "key_thesis": headline,  # Alias for InteractionAgent
            
            # Comprehensive data (for InteractionAgent formatting)
            "complete_data": complete_data,
            "price_data": complete_data["price_data"],
            "fundamentals": complete_data["fundamentals"],
            "sentiment_data": complete_data["sentiment"],
            "institutional_data": complete_data["institutional"],
            "news_headlines": complete_data["news"],
            
            # Detailed view (whiteboard)
            "bull_case": bull_case,
            "bear_case": bear_case,
            "bull_case_highlights": bull_case,  # Alias
            "bear_case_considerations": bear_case,  # Alias
            "debate_transcript": debate_result["transcript"],
            "debate_winner": debate_result["winner"],
            "key_points": debate_result["key_points"],
            "signals": signals,
            "signal_summary": self._format_signal_summary(signals),
            "specialist_scores": specialist_analysis,
            "risk_assessment": risk_assessment,
        }
        
        print(f"\n{'='*60}")
        print(f"✅ RESEARCH COMPLETE: {ticker}")
        print(f"   Action: {action}")
        print(f"   Conviction: {conviction}/10 {'⭐' * conviction}")
        print(f"   Price: ${current_price:.2f} → ${target_price:.2f} ({upside:+.1f}%)")
        print(f"{'='*60}\n")
        
        return report
    
    def _format_signal_summary(self, signals: Dict) -> Dict[str, str]:
        """Format signal summary for output"""
        summary = {}
        
        # Reddit
        if "reddit_sentiment" in signals:
            reddit = signals["reddit_sentiment"]
            summary["Reddit"] = f"{reddit.get('sentiment_label', 'N/A')} ({int(reddit.get('sentiment_score', 0)*100)}% bullish, {reddit.get('mention_volume', 0)} mentions)"
        
        # Twitter
        if "twitter_sentiment" in signals:
            twitter = signals["twitter_sentiment"]
            summary["Twitter"] = f"{twitter.get('sentiment_label', 'N/A')} ({int(twitter.get('sentiment_score', 0)*100)}% bullish)"
        
        # 13F
        if "institutional_activity" in signals:
            inst = signals["institutional_activity"]
            summary["13F Filings"] = f"{inst.get('activity_level', 'N/A')}"
        
        # Unusual activity
        if "unusual_activity" in signals:
            unusual = signals["unusual_activity"]
            if unusual.get("unusual_detected"):
                summary["Unusual Activity"] = f"{unusual.get('bias', 'NEUTRAL')} - {', '.join(unusual.get('activity_type', []))}"
        
        return summary
    
    def _extract_complete_data(self, signals: Dict) -> Dict[str, Any]:
        """Extract ALL data from signals for comprehensive display"""
        data = {
            "price_data": {},
            "fundamentals": {},
            "sentiment": {},
            "institutional": {},
            "news": []
        }
        
        # Price & Volume data
        if "price" in signals and signals["price"]:
            price_info = signals["price"]
            data["price_data"] = {
                "current_price": price_info.get("price"),
                "day_change": price_info.get("day_change"),
                "day_change_pct": price_info.get("day_change_percent"),
                "volume": price_info.get("volume"),
                "market_cap": price_info.get("market_cap")
            }
        
        # Fundamentals from both sources - PRIORITIZE financials as metrics often returns None
        metrics = signals.get("financial_metrics") or {}
        financials = signals.get("financials") or {}
        price_data = data.get("price_data", {})
        
        # Calculate P/E if we have price and EPS
        pe_ratio = None
        eps = financials.get("eps") or metrics.get("eps")
        
        # Annualize EPS if quarterly data
        if eps and financials.get("period") == "quarterly":
            eps_annual = eps * 4
        else:
            eps_annual = eps
        
        if eps_annual and eps_annual > 0 and price_data.get("current_price"):
            pe_ratio = price_data["current_price"] / eps_annual
        
        data["fundamentals"] = {
            "pe_ratio": pe_ratio or metrics.get("pe_ratio"),
            "profit_margin": financials.get("profit_margin_pct") or metrics.get("profit_margin") or financials.get("net_margin"),
            "revenue_growth": metrics.get("revenue_growth") or financials.get("revenue_growth"),
            "debt_to_equity": metrics.get("debt_to_equity") or financials.get("debt_to_equity"),
            "roe": metrics.get("roe") or financials.get("roe"),
            "eps": eps_annual if eps_annual else eps,  # Store annualized EPS
            "eps_period": "TTM (est)" if financials.get("period") == "quarterly" else "Annual",
            "market_cap": price_data.get("market_cap") or metrics.get("market_cap"),
            "revenue": financials.get("revenue") or financials.get("revenue_billions") * 1e9 if financials.get("revenue_billions") else None,
            "net_income": financials.get("net_income") or financials.get("net_income_billions") * 1e9 if financials.get("net_income_billions") else None,
            "gross_profit": financials.get("gross_profit"),
            "operating_income": financials.get("operating_income"),
            "total_assets": financials.get("total_assets"),
            "total_debt": financials.get("total_debt"),
        }
        
        # Store full financial statements for whiteboard
        if financials:
            data["financial_statements"] = {
                "income_statement": financials.get("income_statement", {}),
                "balance_sheet": financials.get("balance_sheet", {}),
                "cash_flow": financials.get("cash_flow", {})
            }
        
        # Store analyst ratings
        if "analyst_ratings" in signals and signals["analyst_ratings"]:
            data["analyst_ratings"] = signals["analyst_ratings"]
        
        # Store peer comparison
        if "peer_comparison" in signals and signals["peer_comparison"]:
            data["peer_comparison"] = signals["peer_comparison"]
        
        # Store historical financials
        if "historical_financials" in signals and signals["historical_financials"]:
            data["historical_financials"] = signals["historical_financials"]
        
        # Store balance sheet
        if "balance_sheet" in signals and signals["balance_sheet"]:
            data["balance_sheet"] = signals["balance_sheet"]
        
        # Store cash flow
        if "cash_flow" in signals and signals["cash_flow"]:
            data["cash_flow"] = signals["cash_flow"]
        
        # Store earnings highlights
        if "earnings_highlights" in signals and signals["earnings_highlights"]:
            data["earnings_highlights"] = signals["earnings_highlights"]
        
        # Social sentiment
        if "reddit_sentiment" in signals:
            data["sentiment"]["reddit"] = signals["reddit_sentiment"]
        if "twitter_sentiment" in signals:
            data["sentiment"]["twitter"] = signals["twitter_sentiment"]
        
        # Institutional
        if "institutional_activity" in signals:
            data["institutional"]["13f"] = signals["institutional_activity"]
        if "insider_trades" in signals:
            data["institutional"]["insider"] = signals["insider_trades"]
        if "unusual_activity" in signals:
            data["institutional"]["unusual"] = signals["unusual_activity"]
        
        # News
        if "news" in signals and signals["news"]:
            news_data = signals["news"]
            if isinstance(news_data, dict) and "news" in news_data:
                data["news"] = news_data["news"][:5]  # Top 5
        
        return data
    
    def _format_signals_for_prompt(self, signals: Dict) -> str:
        """Format signals for LLM prompt"""
        parts = []
        
        # Price
        if "price" in signals:
            price = signals["price"]
            parts.append(f"Current Price: ${price.get('price', 'N/A')}")
        
        # Financials
        if "financials" in signals:
            fin = signals["financials"]
            parts.append(f"P/E Ratio: {fin.get('pe_ratio', 'N/A')}")
            parts.append(f"Profit Margin: {fin.get('profit_margin', 'N/A')}%")
            parts.append(f"Revenue Growth: {fin.get('revenue_growth', 'N/A')}%")
        
        # Social sentiment
        if "reddit_sentiment" in signals:
            reddit = signals["reddit_sentiment"]
            parts.append(f"Reddit Sentiment: {reddit.get('sentiment_label', 'N/A')} ({reddit.get('mention_volume', 0)} mentions)")
        
        if "twitter_sentiment" in signals:
            twitter = signals["twitter_sentiment"]
            parts.append(f"Twitter Sentiment: {twitter.get('sentiment_label', 'N/A')}")
        
        # Institutional
        if "institutional_activity" in signals:
            inst = signals["institutional_activity"]
            parts.append(f"13F Activity: {inst.get('activity_level', 'N/A')}")
        
        # Unusual activity
        if "unusual_activity" in signals:
            unusual = signals["unusual_activity"]
            if unusual.get("unusual_detected"):
                parts.append(f"Unusual Activity: {', '.join(unusual.get('activity_type', []))}")
        
        return "\n".join(parts)

