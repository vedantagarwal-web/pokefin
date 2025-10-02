"""
Research Coordinator - Synthesizes all analyses into final recommendation
"""

from typing import Dict, Any

class ResearchCoordinatorAgent:
    """Coordinates research and generates final recommendations"""
    
    async def synthesize(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize all analyses into recommendation"""
        
        # Calculate overall score
        scores = []
        if analysis.get("fundamental"):
            scores.append(analysis["fundamental"].get("score", 5))
        if analysis.get("technical"):
            scores.append(analysis["technical"].get("score", 5))
        if analysis.get("sentiment"):
            scores.append(analysis["sentiment"].get("score", 5))
        
        overall_score = sum(scores) / len(scores) if scores else 5.0
        
        # Determine recommendation
        if overall_score >= 7:
            recommendation = "BUY"
            color = "green"
        elif overall_score >= 5:
            recommendation = "HOLD"
            color = "yellow"
        else:
            recommendation = "SELL"
            color = "red"
        
        return {
            "recommendation": recommendation,
            "color": color,
            "overall_score": overall_score,
            "confidence": 0.75,
            "rationale": self._generate_rationale(analysis, recommendation)
        }
    
    def _generate_rationale(self, analysis: Dict[str, Any], recommendation: str) -> str:
        """Generate rationale for recommendation"""
        parts = []
        
        if analysis.get("fundamental"):
            parts.append(analysis["fundamental"].get("summary", ""))
        
        if analysis.get("technical"):
            parts.append(analysis["technical"].get("summary", ""))
        
        if analysis.get("sentiment"):
            parts.append(analysis["sentiment"].get("summary", ""))
        
        return " ".join(parts) if parts else f"Based on comprehensive analysis, {recommendation} is recommended."

