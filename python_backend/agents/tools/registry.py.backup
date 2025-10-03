"""
Tool Registry - Defines all tools available to the interaction agent
Uses OpenAI function calling format
"""

from typing import List, Dict, Any

# Tool definitions for OpenAI function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": """Get current or historical stock price for a ticker. Use when user asks about price.
            
            CRITICAL: You MUST convert company names to ticker symbols:
            - "Nvidia" -> "NVDA", "Apple" -> "AAPL", "Infosys" -> "INFY"
            - "Nifty 50" or "nifty" -> "^NSEI", "Sensex" -> "^BSESN"
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'NVDA', 'AAPL', 'INFY', '^NSEI' for indices)"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["current", "1D", "1W", "1M", "3M", "6M", "1Y", "5Y"],
                        "description": "Time period for price data"
                    },
                    "include_chart": {
                        "type": "boolean",
                        "description": "Whether to include a price chart"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financials",
            "description": """Get financial statements and metrics like EPS, revenue, profit margins. Use when user asks about EPS, earnings, revenue, income, or financial performance.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["quarterly", "annual", "ttm"],
                        "description": "Financial reporting period",
                        "default": "quarterly"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_stocks",
            "description": """Search for stocks by criteria or theme. Use for queries like: "ETFs for Indian stocks", "Best tech stocks under $50", "Dividend aristocrats", "Clean energy companies", "Stocks similar to Tesla".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search criteria or theme"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_market_overview",
            "description": """Get overall market sentiment and conditions. Use for queries like: "What's the mood in the markets today?", "How are markets doing?", "Market sentiment", "What's happening in the market?".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_indices": {
                        "type": "boolean",
                        "description": "Include major indices (S&P 500, Nasdaq, Dow)",
                        "default": True
                    },
                    "include_sectors": {
                        "type": "boolean",
                        "description": "Include sector performance",
                        "default": True
                    },
                    "include_sentiment": {
                        "type": "boolean",
                        "description": "Include market sentiment analysis",
                        "default": True
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_balance_sheet",
            "description": """Get balance sheet data (assets, liabilities, equity, debt). Use when user asks about: "balance sheet", "assets", "liabilities", "debt", "cash position".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["quarterly", "annual"],
                        "description": "Reporting period",
                        "default": "quarterly"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cash_flow",
            "description": """Get cash flow statement (operating, investing, financing cash flows, FCF). Use when user asks about: "cash flow", "free cash flow", "FCF", "capital expenditure".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["quarterly", "annual"],
                        "description": "Reporting period",
                        "default": "quarterly"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_metrics",
            "description": """Get key financial ratios and valuation metrics (P/E, ROE, margins, ratios). Use when user asks about: "P/E ratio", "ROE", "valuation", "margins", "ratios", "profitability".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["quarterly", "annual", "ttm"],
                        "description": "Reporting period",
                        "default": "ttm"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_news",
            "description": """Get recent news articles about a company. Use when user asks about: "news", "recent updates", "what's happening with", "latest news".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of news articles to return",
                        "default": 10
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_insider_trades",
            "description": """Get recent insider trading activity (buys/sells by executives and directors). Use when user asks about: "insider trading", "insider buys", "executive trades", "who's buying/selling".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of trades to return",
                        "default": 10
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_institutional_ownership",
            "description": """Get institutional investors (hedge funds, mutual funds) holding this stock. Use when user asks about: "institutional ownership", "who owns", "largest shareholders", "hedge funds holding".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of holders to return",
                        "default": 10
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "exa_search",
            "description": """Search the web for financial news, research, and analysis using Exa AI. Use when you need: recent market news, research on topics, information about trends, general financial knowledge not specific to one stock.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 10
                    },
                    "category": {
                        "type": "string",
                        "enum": ["company", "research paper", "news", "financial report", "tweet"],
                        "description": "Optional category filter"
                    },
                    "include_text": {
                        "type": "boolean",
                        "description": "Include full text content",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "exa_answer",
            "description": """Get a direct answer to a factual question using Exa AI. Great for questions like: "What is the latest valuation of SpaceX?", "Who is the CEO of Tesla?", "What happened in the market today?".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to answer"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_stock",
            "description": """Perform comprehensive stock analysis using specialist agents. Use when user wants deep analysis or investment recommendation. Automatically runs fundamental, technical, and sentiment analysis.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["quick", "standard", "deep"],
                        "description": "Analysis depth",
                        "default": "standard"
                    },
                    "include_charts": {
                        "type": "boolean",
                        "default": True
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_stocks",
            "description": """Compare multiple stocks across various metrics. Use when user wants to compare options or asks "X vs Y".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of ticker symbols to compare"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["1M", "3M", "6M", "1Y", "5Y"],
                        "default": "1Y"
                    },
                    "include_chart": {
                        "type": "boolean",
                        "default": True
                    }
                },
                "required": ["tickers"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "research_topic",
            "description": """Research a financial topic using AI. Use for educational queries or market research: "What are growth stocks?", "Explain options trading", "How does the Fed rate affect stocks?", "What is a REIT?".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to research"
                    },
                    "include_examples": {
                        "type": "boolean",
                        "default": True
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": """Get recent financial news and analysis. Use for queries about company news, market news, sector news, or economic events.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for news (ticker, company name, or topic)"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["1h", "24h", "1W", "1M"],
                        "default": "24h"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_similar_stocks",
            "description": """Find stocks similar to a given ticker. Use when user asks "stocks like X" or "alternatives to X".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Reference ticker"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 5
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_chart",
            "description": """Generate interactive price chart with technical indicators. Use when user asks to see a chart, wants visual analysis, or mentions technical indicators.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["1D", "1W", "1M", "3M", "6M", "1Y", "5Y"],
                        "description": "Chart timeframe",
                        "default": "1M"
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["candlestick", "line", "area"],
                        "description": "Chart style",
                        "default": "candlestick"
                    },
                    "include_volume": {
                        "type": "boolean",
                        "description": "Show volume bars",
                        "default": True
                    },
                    "indicators": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["ma20", "ma50", "ma200", "rsi", "macd"]
                        },
                        "description": "Technical indicators to add"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_comparison_chart",
            "description": """Generate comparison chart for multiple stocks. Use when user wants to compare performance of different stocks.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of ticker symbols to compare"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["1W", "1M", "3M", "6M", "1Y", "5Y"],
                        "description": "Comparison timeframe",
                        "default": "1Y"
                    }
                },
                "required": ["tickers"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_sector_heatmap",
            "description": """Generate sector performance heatmap. Use when user asks about sector performance, market rotation, or which sectors are hot/cold.""",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "screen_stocks",
            "description": """Screen stocks based on criteria. Use when user wants to find stocks matching specific requirements like 'value stocks', 'growth stocks', 'tech stocks', etc.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "criteria": {
                        "type": "string",
                        "description": "Natural language criteria: 'high growth', 'value stocks', 'dividend stocks', etc."
                    },
                    "universe": {
                        "type": "string",
                        "enum": ["sp500", "tech", "growth", "dividend"],
                        "description": "Stock universe to search",
                        "default": "sp500"
                    }
                },
                "required": ["criteria"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_gainers",
            "description": """Get today's top gaining stocks. Use when user asks 'what stocks are up', 'top gainers', 'biggest winners'.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of stocks to return",
                        "default": 10
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_losers",
            "description": """Get today's worst performing stocks. Use when user asks 'what stocks are down', 'top losers', 'biggest losers'.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of stocks to return",
                        "default": 10
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_most_active",
            "description": """Get most actively traded stocks. Use when user asks 'most active stocks', 'highest volume', 'most traded'.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of stocks to return",
                        "default": 10
                    }
                }
            }
        }
    }
]

# Registry mapping function names to implementations
TOOL_REGISTRY = {}

def register_tool(name: str):
    """Decorator to register tool implementations"""
    def decorator(func):
        TOOL_REGISTRY[name] = func
        return func
    return decorator

def get_tools_for_openai() -> List[Dict[str, Any]]:
    """Get tools in OpenAI function calling format"""
    return TOOL_DEFINITIONS

def get_tool_function(name: str):
    """Get tool implementation by name"""
    return TOOL_REGISTRY.get(name)

