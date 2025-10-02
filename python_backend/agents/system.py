"""
AlphaWealth System - Main orchestrator for all agents
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .interaction_agent import InteractionAgent
from .specialist_agents import (
    FundamentalAnalysisAgent,
    TechnicalAnalysisAgent,
    SentimentAnalysisAgent,
    RiskAssessmentAgent
)
from .chart_agent import ChartGeneratorAgent
from .research_coordinator import ResearchCoordinatorAgent

class AlphaWealthSystem:
    """
    Main system that coordinates all AI agents
    Inspired by OpenPoke's multi-agent architecture + TradingAgents' specialist approach
    """
    
    def __init__(self):
        print("🤖 Initializing AlphaWealth AI agents...")
        
        # Core agents
        self.interaction_agent = InteractionAgent()
        self.fundamental_agent = FundamentalAnalysisAgent()
        self.technical_agent = TechnicalAnalysisAgent()
        self.sentiment_agent = SentimentAnalysisAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.chart_agent = ChartGeneratorAgent()
        self.research_coordinator = ResearchCoordinatorAgent()
        
        print("✅ All agents initialized")
    
    async def process_message(
        self,
        message: str,
        history: List[Dict[str, str]],
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point - process user message through interaction agent
        
        The interaction agent uses OpenAI function calling to dynamically decide:
        1. What tools to call
        2. Which specialist agents to invoke
        3. What analysis to perform
        4. What visualizations to show
        
        This is truly agentic - no hardcoded routing!
        """
        try:
            # Process through interaction agent (the orchestrator)
            result = await self.interaction_agent.process_message(
                user_message=message,
                conversation_history=history,
                user_context=user_context or {},
                session_id=session_id
            )
            
            return result
        
        except Exception as e:
            print(f"❌ Error in AlphaWealth system: {e}")
            return {
                "response": "I hit a snag analyzing that. Mind rephrasing or trying a different question?",
                "charts": [],
                "actions": [],
                "whiteboard_data": None,
                "error": str(e)
            }
    
    async def stream_message(
        self,
        message: str,
        history: List[Dict[str, str]],
        session_id: str
    ):
        """
        Stream response in real-time via WebSocket
        """
        async for chunk in self.interaction_agent.stream_response(
            user_message=message,
            conversation_history=history,
            session_id=session_id
        ):
            yield chunk
    
    async def analyze_stock(
        self,
        ticker: str,
        depth: str = "standard",
        include_charts: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive stock analysis (called by interaction agent)
        """
        # Run specialist agents in parallel
        analyses = await asyncio.gather(
            self.fundamental_agent.analyze(ticker, depth=depth),
            self.technical_agent.analyze(ticker),
            self.sentiment_agent.analyze(ticker),
            self.risk_agent.analyze(ticker),
            return_exceptions=True
        )
        
        fundamental, technical, sentiment, risk = analyses
        
        # Handle any errors gracefully
        result = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "fundamental": fundamental if not isinstance(fundamental, Exception) else None,
            "technical": technical if not isinstance(technical, Exception) else None,
            "sentiment": sentiment if not isinstance(sentiment, Exception) else None,
            "risk": risk if not isinstance(risk, Exception) else None
        }
        
        # Generate charts if requested
        if include_charts and isinstance(technical, dict):
            result["charts"] = await self.chart_agent.generate_charts_for_analysis(result)
        
        # Coordinate final recommendation
        result["recommendation"] = await self.research_coordinator.synthesize(result)
        
        # Generate whiteboard data
        result["whiteboard_data"] = self._generate_whiteboard_data(result)
        
        return result
    
    def _generate_whiteboard_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed whiteboard view data
        """
        return {
            "ticker": analysis["ticker"],
            "timestamp": analysis["timestamp"],
            "sections": {
                "overview": self._create_overview_section(analysis),
                "fundamental": analysis.get("fundamental"),
                "technical": analysis.get("technical"),
                "sentiment": analysis.get("sentiment"),
                "risk": analysis.get("risk"),
                "recommendation": analysis.get("recommendation")
            }
        }
    
    def _create_overview_section(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create overview section for whiteboard"""
        return {
            "ticker": analysis["ticker"],
            "analysis_date": analysis["timestamp"],
            "overall_score": self._calculate_overall_score(analysis),
            "key_takeaways": self._extract_key_takeaways(analysis)
        }
    
    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall score from all analyses"""
        scores = []
        
        if analysis.get("fundamental"):
            scores.append(analysis["fundamental"].get("score", 5))
        if analysis.get("technical"):
            scores.append(analysis["technical"].get("score", 5))
        if analysis.get("sentiment"):
            scores.append(analysis["sentiment"].get("score", 5))
        
        return sum(scores) / len(scores) if scores else 5.0
    
    def _extract_key_takeaways(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract key takeaways from all analyses"""
        takeaways = []
        
        if analysis.get("fundamental"):
            takeaways.append(analysis["fundamental"].get("summary", ""))
        if analysis.get("technical"):
            takeaways.append(analysis["technical"].get("summary", ""))
        if analysis.get("sentiment"):
            takeaways.append(analysis["sentiment"].get("summary", ""))
        
        return [t for t in takeaways if t]

