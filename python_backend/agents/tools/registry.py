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
    },
    {
        "type": "function",
        "function": {
            "name": "get_earnings_calendar",
            "description": """Get upcoming earnings dates. Use when user asks 'when is earnings', 'earnings date', 'earnings calendar'.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker (optional - if not provided, returns calendar for all stocks)"
                    },
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days to look ahead",
                        "default": 30
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_analyst_ratings",
            "description": """Get analyst ratings and price targets. Use when user asks 'what do analysts think', 'price target', 'analyst rating', 'consensus'.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_institutional_investor",
            "description": """Search for an institutional investor's holdings. Use when user asks about a specific fund/investor like 'What does Mithaq own', 'Berkshire holdings', 'Ark Invest portfolio', 'What's Mithaq's position in PLCE'.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "investor_name": {
                        "type": "string",
                        "description": "Name of the institutional investor (e.g., 'Mithaq Capital', 'Berkshire Hathaway', 'ARK Invest')"
                    },
                    "ticker": {
                        "type": "string",
                        "description": "Optional: specific ticker to check if this investor holds it"
                    }
                },
                "required": ["investor_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_dcf",
            "description": """Calculate DCF (Discounted Cash Flow) valuation. Use when user asks 'intrinsic value', 'fair value', 'DCF', 'what's it really worth'.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "growth_rate": {
                        "type": "number",
                        "description": "Expected growth rate (%)",
                        "default": 10
                    },
                    "discount_rate": {
                        "type": "number",
                        "description": "Discount rate/WACC (%)",
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
            "name": "get_earnings_history",
            "description": """Get historical earnings results and surprises. Use when user asks 'earnings history', 'how did they do last quarter', 'earnings beat'.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of quarters to return",
                        "default": 8
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_sec_filings",
            "description": "Search SEC filings (10-K, 10-Q, 8-K, 13F, etc.) for companies or investors using Exa AI. Use for finding SEC documents, annual reports, quarterly filings, and institutional holdings filings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_or_investor": {
                        "type": "string",
                        "description": "Company name or investor name (e.g., 'Mithaq Capital', 'Tesla', 'Berkshire Hathaway')"
                    },
                    "filing_type": {
                        "type": "string",
                        "enum": ["10-K", "10-Q", "8-K", "13F", "13D", "13G", "DEF 14A", "S-1", "all"],
                        "description": "Type of SEC filing to search for",
                        "default": "all"
                    },
                    "ticker": {
                        "type": "string",
                        "description": "Optional: stock ticker to narrow search"
                    }
                },
                "required": ["company_or_investor"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_institutional_positions",
            "description": "Search for institutional investor positions using Exa AI to find 13F filings, news, and holdings data. Use when user asks about hedge fund holdings, investor positions, or specific institutional stakes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "investor_name": {
                        "type": "string",
                        "description": "Name of institutional investor (e.g., 'Mithaq Capital', 'Berkshire Hathaway', 'Bridgewater')"
                    },
                    "ticker": {
                        "type": "string",
                        "description": "Optional: specific ticker to check position in"
                    },
                    "include_sec_filings": {
                        "type": "boolean",
                        "description": "Include SEC 13F filings in search",
                        "default": True
                    }
                },
                "required": ["investor_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_earnings_materials",
            "description": "Search for earnings call transcripts, presentations, and press releases using Exa AI. Use for finding earnings documents, investor presentations, and quarterly results materials.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_or_ticker": {
                        "type": "string",
                        "description": "Company name or ticker symbol"
                    },
                    "quarter": {
                        "type": "string",
                        "description": "Optional: specific quarter (e.g., 'Q3 2024', 'latest')",
                        "default": "latest"
                    }
                },
                "required": ["company_or_ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_reddit_sentiment",
            "description": "Scan Reddit (r/wallstreetbets, r/stocks, r/investing) for sentiment and discussion volume about a stock. Returns sentiment score, mention volume, top posts, and trending status. Use for gauging retail investor sentiment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'NVDA', 'TSLA')"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_twitter_sentiment",
            "description": "Scan Twitter/FinTwit for sentiment, influencer opinions, and discussion trends about a stock. Returns sentiment score, influencer takes, and trending status. Use for social media sentiment analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'AAPL', 'MSFT')"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_13f_changes",
            "description": "Track recent 13F filing CHANGES - new positions, increased stakes, decreased stakes, exits by institutional investors. Shows smart money movement and conviction changes. Use to see what hedge funds and institutions are buying or selling.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'GOOGL', 'META')"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_unusual_activity",
            "description": "Detect unusual activity: unusual options flow, large block trades, dark pool prints. Indicates smart money positioning. Use to find unusual call/put buying or large institutional orders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'AMZN', 'NFLX')"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_deep_research",
            "description": "🎯 KILLER FEATURE: Run comprehensive multi-source research with bull vs bear debate system. Returns high-conviction BUY/SELL/HOLD recommendation (1-10 conviction score) with detailed analysis. Use when user asks for investment recommendations, should I buy questions, or deep analysis. This is THE tool for generating stock recommendations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'NVDA', 'TSLA')"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["quick", "standard", "deep"],
                        "description": "Research depth: 'quick' (30s), 'standard' (60s, default), 'deep' (3min)",
                        "default": "standard"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "roast_portfolio",
            "description": "🔥 BRUTAL PORTFOLIO ROAST: Analyze user's portfolio with brutal honesty like Poke roasts emails. Identifies meme stocks, over-concentration, terrible performance, and calculates FIRE requirements. Use when user wants portfolio analysis or financial reality check.",
            "parameters": {
                "type": "object",
                "properties": {
                    "portfolio_data": {
                        "type": "object",
                        "description": "Portfolio data with positions, cash, etc. Optional - will use mock data if not provided"
                    },
                    "user_age": {
                        "type": "integer",
                        "description": "User's age for FIRE calculations",
                        "default": 30
                    },
                    "user_income": {
                        "type": "integer", 
                        "description": "User's annual income",
                        "default": 50000
                    },
                    "user_savings": {
                        "type": "integer",
                        "description": "User's current savings",
                        "default": 10000
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_fire",
            "description": "💀 BRUTAL FIRE CALCULATOR: Calculate Financial Independence Retire Early (FIRE) requirements with brutal honesty about reality. Shows exactly how much user needs to invest monthly to retire by target age. Use when user asks about FIRE, retirement planning, or financial independence.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_age": {
                        "type": "integer",
                        "description": "User's current age",
                        "default": 30
                    },
                    "current_savings": {
                        "type": "integer",
                        "description": "Current total savings/investments",
                        "default": 10000
                    },
                    "monthly_income": {
                        "type": "integer",
                        "description": "Monthly gross income",
                        "default": 5000
                    },
                    "monthly_expenses": {
                        "type": "integer",
                        "description": "Monthly expenses",
                        "default": 4000
                    },
                    "target_retirement_age": {
                        "type": "integer",
                        "description": "Desired retirement age",
                        "default": 45
                    },
                    "risk_tolerance": {
                        "type": "string",
                        "enum": ["conservative", "moderate", "aggressive"],
                        "description": "Investment risk tolerance",
                        "default": "moderate"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "negotiate_access",
            "description": "🤝 NEGOTIATION SYSTEM: User must convince AI to work with them and negotiate pricing. AI analyzes user profile and sets conditions. Use for initial onboarding conversation flow. Production-grade conversation with qualifying questions before pricing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_profile": {
                        "type": "object",
                        "description": "User profile with age, income, savings, experience, goals. Optional - will use mock data if not provided"
                    },
                    "initial_request": {
                        "type": "string",
                        "description": "User's initial request to use the service",
                        "default": "I want to use your financial advisor"
                    },
                    "conversation_stage": {
                        "type": "string",
                        "enum": ["initial", "qualifying", "assessment", "budget_negotiation", "final_agreement"],
                        "description": "Current stage in the negotiation conversation flow",
                        "default": "initial"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assess_risk_tolerance",
            "description": "🎯 RISK TOLERANCE ASSESSMENT: Comprehensive questionnaire to understand user's risk appetite and recommend appropriate investment strategies (index funds, ETFs, stocks, options). Use for onboarding to determine investment recommendations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_responses": {
                        "type": "object",
                        "description": "User's answers to risk assessment questions. Optional - will start questionnaire if not provided"
                    },
                    "conversation_stage": {
                        "type": "string",
                        "enum": ["initial", "risk_assessment"],
                        "description": "Current stage in risk assessment conversation",
                        "default": "initial"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "connect_brokerage",
            "description": "🏦 BROKERAGE CONNECTION: Connect user's Robinhood or other brokerage account via SnapTrade for real portfolio data analysis. Use when user wants to link their brokerage account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Unique user identifier. Optional - will generate if not provided"
                    },
                    "redirect_uri": {
                        "type": "string",
                        "description": "Redirect URI for OAuth callback",
                        "default": "http://localhost:8787/callback"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_real_portfolio",
            "description": "📊 REAL PORTFOLIO DATA: Fetch user's actual portfolio from connected brokerage for authentic portfolio roasting and FIRE calculations. Use after brokerage connection is established.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "SnapTrade user ID from brokerage connection"
                    },
                    "user_secret": {
                        "type": "string",
                        "description": "SnapTrade user secret from brokerage connection"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Specific account ID. Optional - uses first account if not provided"
                    }
                },
                "required": ["user_id", "user_secret"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_robinhood_portfolio",
            "description": "📊 ROBINHOOD PORTFOLIO ANALYSIS: Fetch and analyze user's actual Robinhood portfolio for authentic portfolio roasting and FIRE calculations using real data. Use when user has connected their Robinhood account via OAuth2.",
            "parameters": {
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "string",
                        "description": "Robinhood OAuth2 access token from connected account"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Specific Robinhood account ID. Optional - uses first account if not provided"
                    }
                },
                "required": ["access_token"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_portfolio_summary",
            "description": "📊 PORTFOLIO SUMMARY: Get comprehensive portfolio summary including positions, balances, and performance. Use when user asks about their portfolio, holdings, or account balance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "SnapTrade user ID from brokerage connection"
                    },
                    "user_secret": {
                        "type": "string",
                        "description": "SnapTrade user secret from brokerage connection"
                    }
                },
                "required": ["user_id", "user_secret"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_account_positions",
            "description": "📈 ACCOUNT POSITIONS: Get detailed positions for a specific account or all accounts. Use when user asks about their holdings, positions, or specific stocks they own.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "SnapTrade user ID from brokerage connection"
                    },
                    "user_secret": {
                        "type": "string",
                        "description": "SnapTrade user secret from brokerage connection"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Specific account ID. Optional - gets all accounts if not provided"
                    }
                },
                "required": ["user_id", "user_secret"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_trade_history",
            "description": "📋 TRADE HISTORY: Get transaction history for a specific account or all accounts. Use when user asks about their trading history, past trades, or transaction records.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "SnapTrade user ID from brokerage connection"
                    },
                    "user_secret": {
                        "type": "string",
                        "description": "SnapTrade user secret from brokerage connection"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Specific account ID. Optional - gets all accounts if not provided"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of transactions to return. Default: 50"
                    }
                },
                "required": ["user_id", "user_secret"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_portfolio_performance",
            "description": "📊 PORTFOLIO PERFORMANCE: Analyze portfolio performance including returns, risk metrics, and recommendations. Use when user asks about portfolio performance, returns, or investment analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "SnapTrade user ID from brokerage connection"
                    },
                    "user_secret": {
                        "type": "string",
                        "description": "SnapTrade user secret from brokerage connection"
                    }
                },
                "required": ["user_id", "user_secret"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_account_balances",
            "description": "💰 ACCOUNT BALANCES: Get account balances including cash, buying power, and equity. Use when user asks about their account balance, cash available, or buying power.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "SnapTrade user ID from brokerage connection"
                    },
                    "user_secret": {
                        "type": "string",
                        "description": "SnapTrade user secret from brokerage connection"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Specific account ID. Optional - gets all accounts if not provided"
                    }
                },
                "required": ["user_id", "user_secret"]
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

