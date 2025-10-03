"""
Research Configuration System
Inspired by TradingAgents' flexible configuration approach
"""

RESEARCH_CONFIGS = {
    "quick": {
        "name": "Quick Research",
        "description": "Fast analysis with basic signals",
        "deep_think_llm": "gpt-4o-mini",
        "quick_think_llm": "gpt-4o-mini",
        "max_debate_rounds": 1,
        "signal_sources": [
            "price",
            "fundamentals",
            "news"
        ],
        "conviction_threshold": 6,
        "use_reddit": False,
        "use_twitter": False,
        "use_13f": False,
        "use_insider": True,
        "use_options": False,
        "max_research_time_seconds": 30
    },
    
    "standard": {
        "name": "Standard Research",
        "description": "Balanced analysis with multiple signals",
        "deep_think_llm": "gpt-4o",
        "quick_think_llm": "gpt-4o-mini",
        "max_debate_rounds": 2,
        "signal_sources": [
            "price",
            "fundamentals",
            "technical",
            "news",
            "sentiment",
            "insider"
        ],
        "conviction_threshold": 7,
        "use_reddit": True,
        "use_twitter": True,
        "use_13f": True,
        "use_insider": True,
        "use_options": False,
        "max_research_time_seconds": 60
    },
    
    "deep": {
        "name": "Deep Research",
        "description": "Exhaustive multi-source analysis",
        "deep_think_llm": "o1-mini",  # For complex reasoning
        "quick_think_llm": "gpt-4o",
        "max_debate_rounds": 3,
        "signal_sources": [
            "price",
            "fundamentals",
            "technical",
            "news",
            "sentiment",
            "reddit",
            "twitter",
            "13f",
            "insider",
            "options",
            "earnings",
            "analyst_ratings"
        ],
        "conviction_threshold": 8,
        "use_reddit": True,
        "use_twitter": True,
        "use_13f": True,
        "use_insider": True,
        "use_options": True,
        "max_research_time_seconds": 180
    }
}

# Default configuration
DEFAULT_RESEARCH_CONFIG = RESEARCH_CONFIGS["standard"]

def get_config(mode: str = "standard"):
    """Get research configuration by mode"""
    return RESEARCH_CONFIGS.get(mode, DEFAULT_RESEARCH_CONFIG).copy()

