"""
Tool Implementations - Actual functions that get called
SIMPLIFIED: LLM handles ticker resolution
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from .registry import register_tool
from services.financial_datasets_client import FinancialDatasetsClient
from services.exa_client import ExaClient
from services.chart_service import ChartService
from services.screener_service import ScreenerService

# Initialize clients
fd_client = FinancialDatasetsClient()
exa_client = ExaClient()
chart_service = ChartService()
screener_service = ScreenerService()

@register_tool("get_stock_price")
async def get_stock_price(
    ticker: str,
    timeframe: str = "current",
    include_chart: bool = False
) -> Dict[str, Any]:
    """
    Get stock price for a ticker symbol.
    LLM converts company names to tickers (e.g., "Nvidia" -> "NVDA", "Infosys" -> "INFY", "Nifty 50" -> "^NSEI").
    """
    try:
        # Get price data
        if timeframe == "current":
            quote = await fd_client.get_quote(ticker)
            
            result = {
                "ticker": ticker,
                "price": quote["price"],
                "change": quote["change"],
                "change_percent": quote["change_percent"],
                "volume": quote["volume"],
                "market_cap": quote.get("market_cap"),
                "timestamp": quote["timestamp"]
            }
            
            if include_chart:
                # Get intraday prices for chart
                intraday = await fd_client.get_intraday_prices(ticker)
                result["chart_data"] = intraday
            
            return result
        else:
            # Historical prices
            prices = await fd_client.get_historical_prices(ticker, timeframe)
            return {
                "ticker": ticker,
                "timeframe": timeframe,
                "prices": prices,
                "start_date": prices[0]["date"] if prices else None,
                "end_date": prices[-1]["date"] if prices else None
            }
    except Exception as e:
        print(f"❌ Error fetching stock price: {e}")
        return {"error": str(e), "ticker": ticker}

@register_tool("get_financials")
async def get_financials(
    ticker: str,
    period: str = "quarterly"
) -> Dict[str, Any]:
    """
    Get financial statements and key metrics like EPS, revenue, margins.
    """
    try:
        # Get income statement for EPS, revenue, profit margins
        response = await fd_client.client.get(
            f"{fd_client.base_url}/financials/income-statements/",
            params={"ticker": ticker, "period": period, "limit": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("income_statements"):
                stmt = data["income_statements"][0]
                
                # Calculate key metrics
                revenue = stmt.get("revenue", 0)
                net_income = stmt.get("net_income", 0)
                profit_margin = (net_income / revenue * 100) if revenue else 0
                
                return {
                    "ticker": ticker,
                    "report_period": stmt.get("report_period"),
                    "fiscal_period": stmt.get("fiscal_period"),
                    "period": period,
                    "eps": stmt.get("earnings_per_share"),
                    "eps_diluted": stmt.get("earnings_per_share_diluted"),
                    "revenue": revenue,
                    "revenue_billions": revenue / 1e9,
                    "net_income": net_income,
                    "net_income_billions": net_income / 1e9,
                    "gross_profit": stmt.get("gross_profit"),
                    "operating_income": stmt.get("operating_income"),
                    "profit_margin_pct": round(profit_margin, 2),
                    "currency": stmt.get("currency", "USD")
                }
        
        return {"error": "Could not fetch financial data", "ticker": ticker}
    
    except Exception as e:
        print(f"❌ Error fetching financials: {e}")
        return {"error": str(e), "ticker": ticker}

@register_tool("get_balance_sheet")
async def get_balance_sheet(
    ticker: str,
    period: str = "quarterly"
) -> Dict[str, Any]:
    """
    Get balance sheet data for a company.
    """
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/financials/balance-sheets/",
            params={"ticker": ticker, "period": period, "limit": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("balance_sheets"):
                bs = data["balance_sheets"][0]
                return {
                    "ticker": ticker,
                    "report_period": bs.get("report_period"),
                    "total_assets": bs.get("total_assets"),
                    "total_assets_billions": bs.get("total_assets", 0) / 1e9,
                    "total_liabilities": bs.get("total_liabilities"),
                    "shareholders_equity": bs.get("shareholders_equity"),
                    "cash_and_equivalents": bs.get("cash_and_equivalents"),
                    "total_debt": bs.get("total_debt"),
                    "current_assets": bs.get("current_assets"),
                    "current_liabilities": bs.get("current_liabilities"),
                    "debt_to_equity": bs.get("total_debt", 0) / bs.get("shareholders_equity", 1) if bs.get("shareholders_equity") else 0
                }
        
        return {"error": "Could not fetch balance sheet", "ticker": ticker}
    except Exception as e:
        print(f"❌ Error fetching balance sheet: {e}")
        return {"error": str(e), "ticker": ticker}

@register_tool("get_cash_flow")
async def get_cash_flow(
    ticker: str,
    period: str = "quarterly"
) -> Dict[str, Any]:
    """
    Get cash flow statement for a company.
    """
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/financials/cash-flow-statements/",
            params={"ticker": ticker, "period": period, "limit": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("cash_flow_statements"):
                cf = data["cash_flow_statements"][0]
                return {
                    "ticker": ticker,
                    "report_period": cf.get("report_period"),
                    "operating_cash_flow": cf.get("net_cash_flow_from_operations"),
                    "investing_cash_flow": cf.get("net_cash_flow_from_investing"),
                    "financing_cash_flow": cf.get("net_cash_flow_from_financing"),
                    "free_cash_flow": cf.get("free_cash_flow"),
                    "free_cash_flow_billions": cf.get("free_cash_flow", 0) / 1e9,
                    "capital_expenditure": cf.get("capital_expenditure")
                }
        
        return {"error": "Could not fetch cash flow", "ticker": ticker}
    except Exception as e:
        print(f"❌ Error fetching cash flow: {e}")
        return {"error": str(e), "ticker": ticker}

@register_tool("get_financial_metrics")
async def get_financial_metrics(
    ticker: str,
    period: str = "ttm"
) -> Dict[str, Any]:
    """
    Get key financial ratios and metrics (P/E, ROE, margins, etc).
    """
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/financial-metrics/",
            params={"ticker": ticker, "period": period, "limit": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            # FDS returns metrics directly or in an array
            metrics = data if isinstance(data, dict) else data[0] if isinstance(data, list) and data else {}
            
            return {
                "ticker": ticker,
                "pe_ratio": metrics.get("price_to_earnings_ratio"),
                "pb_ratio": metrics.get("price_to_book_ratio"),
                "ps_ratio": metrics.get("price_to_sales_ratio"),
                "roe": metrics.get("return_on_equity"),
                "roa": metrics.get("return_on_assets"),
                "gross_margin": metrics.get("gross_margin"),
                "operating_margin": metrics.get("operating_margin"),
                "net_margin": metrics.get("net_margin"),
                "debt_to_equity": metrics.get("debt_to_equity"),
                "current_ratio": metrics.get("current_ratio"),
                "quick_ratio": metrics.get("quick_ratio")
            }
        
        return {"error": "Could not fetch financial metrics", "ticker": ticker}
    except Exception as e:
        print(f"❌ Error fetching financial metrics: {e}")
        return {"error": str(e), "ticker": ticker}

@register_tool("get_company_news")
async def get_company_news(
    ticker: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get recent news articles about a company.
    """
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/news/",
            params={"ticker": ticker, "limit": limit}
        )
        
        if response.status_code == 200:
            data = response.json()
            news_items = data.get("news", [])
            
            return {
                "ticker": ticker,
                "news_count": len(news_items),
                "news": [{
                    "title": item.get("title"),
                    "date": item.get("date"),
                    "source": item.get("source"),
                    "url": item.get("url"),
                    "sentiment": item.get("sentiment")
                } for item in news_items[:limit]]
            }
        
        return {"error": "Could not fetch news", "ticker": ticker}
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return {"error": str(e), "ticker": ticker}

@register_tool("get_insider_trades")
async def get_insider_trades(
    ticker: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get recent insider trading activity (buys/sells by executives).
    """
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/insider-trades/",
            params={"ticker": ticker, "limit": limit}
        )
        
        if response.status_code == 200:
            data = response.json()
            trades = data.get("insider_trades", [])
            
            return {
                "ticker": ticker,
                "trades_count": len(trades),
                "recent_trades": [{
                    "name": trade.get("name"),
                    "title": trade.get("title"),
                    "transaction_date": trade.get("transaction_date"),
                    "transaction_shares": trade.get("transaction_shares"),
                    "transaction_value": trade.get("transaction_value"),
                    "shares_owned_after": trade.get("shares_owned_after_transaction")
                } for trade in trades[:limit]]
            }
        
        return {"error": "Could not fetch insider trades", "ticker": ticker}
    except Exception as e:
        print(f"❌ Error fetching insider trades: {e}")
        return {"error": str(e), "ticker": ticker}

@register_tool("get_institutional_ownership")
async def get_institutional_ownership(
    ticker: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get institutional investors (hedge funds, mutual funds) holding this stock.
    """
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/institutional-ownership/",
            params={"ticker": ticker, "limit": limit}
        )
        
        if response.status_code == 200:
            data = response.json()
            holdings = data.get("institutional-ownership", [])
            
            return {
                "ticker": ticker,
                "holders_count": len(holdings),
                "top_holders": [{
                    "investor": holding.get("investor"),
                    "shares": holding.get("shares"),
                    "market_value": holding.get("market_value"),
                    "report_period": holding.get("report_period")
                } for holding in holdings[:limit]]
            }
        
        return {"error": "Could not fetch institutional ownership", "ticker": ticker}
    except Exception as e:
        print(f"❌ Error fetching institutional ownership: {e}")
        return {"error": str(e), "ticker": ticker}

@register_tool("search_stocks")
async def search_stocks(
    query: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search for stocks/ETFs matching criteria.
    Examples: "ETFs for Indian stocks", "Clean energy stocks", "Dividend aristocrats"
    """
    try:
        # Use Exa for semantic search of stocks
        results = await exa_client.search(
            query=f"stocks ETFs {query}",
            num_results=limit,
            category="financial report"
        )
        
        search_results = results.get("results", [])
        
        return {
            "query": query,
            "results_count": len(search_results),
            "matches": [{
                "title": r.get("title"),
                "description": r.get("text", "")[:200],
                "url": r.get("url")
            } for r in search_results]
        }
    except Exception as e:
        print(f"❌ Error searching stocks: {e}")
        return {"error": str(e), "query": query}

@register_tool("get_market_overview")
async def get_market_overview(
    include_indices: bool = True,
    include_sectors: bool = True,
    include_sentiment: bool = True
) -> Dict[str, Any]:
    """
    Get overall market conditions and sentiment.
    """
    result = {
        "timestamp": datetime.now().isoformat(),
        "market_status": "open"  # TODO: Check market hours
    }
    
    if include_indices:
        # Get major indices
        indices = {
            "S&P 500": "SPY",
            "Nasdaq": "QQQ",
            "Dow Jones": "DIA"
        }
        
        index_data = await asyncio.gather(*[
            fd_client.get_quote(ticker)
            for ticker in indices.values()
        ], return_exceptions=True)
        
        result["indices"] = {
            name: {
                "price": data["price"] if not isinstance(data, Exception) else 0,
                "change_percent": data["change_percent"] if not isinstance(data, Exception) else 0
            }
            for name, data in zip(indices.keys(), index_data)
        }
    
    if include_sectors:
        # Get sector performance
        sector_etfs = {
            "Technology": "XLK",
            "Healthcare": "XLV",
            "Financials": "XLF",
            "Energy": "XLE",
            "Consumer": "XLY"
        }
        
        sector_data = await asyncio.gather(*[
            fd_client.get_quote(ticker)
            for ticker in sector_etfs.values()
        ], return_exceptions=True)
        
        result["sectors"] = {
            name: {
                "change_percent": data["change_percent"] if not isinstance(data, Exception) else 0
            }
            for name, data in zip(sector_etfs.keys(), sector_data)
        }
        
        # Sort sectors
        sorted_sectors = sorted(
            result["sectors"].items(),
            key=lambda x: x[1]["change_percent"],
            reverse=True
        )
        result["top_sectors"] = sorted_sectors[:2]
        result["worst_sectors"] = sorted_sectors[-2:]
    
    if include_sentiment:
        # Get market sentiment from news
        news_sentiment = await exa_client.get_market_sentiment()
        
        result["sentiment"] = {
            "score": news_sentiment.get("score", 0),
            "label": news_sentiment.get("label", "neutral"),
            "drivers": news_sentiment.get("drivers", [])
        }
    
    return result

@register_tool("analyze_stock")
async def analyze_stock(
    ticker: str,
    depth: str = "standard",
    include_charts: bool = True
) -> Dict[str, Any]:
    """
    Comprehensive stock analysis using specialist agents.
    This is a heavy operation - imports the full system.
    """
    
    # Import here to avoid circular dependencies
    from agents.system import AlphaWealthSystem
    
    system = AlphaWealthSystem()
    
    result = await system.analyze_stock(
        ticker=ticker,
        depth=depth,
        include_charts=include_charts
    )
    
    return result

@register_tool("compare_stocks")
async def compare_stocks(
    tickers: List[str],
    metrics: List[str] = None
) -> Dict[str, Any]:
    """
    Compare multiple stocks side by side.
    """
    if not metrics:
        metrics = ["price", "pe_ratio", "market_cap", "revenue_growth"]
    
    # Get data for each ticker in parallel
    stock_data = await asyncio.gather(*[
        _get_comparison_data(ticker, metrics)
        for ticker in tickers
    ], return_exceptions=True)
    
    return {
        "tickers": tickers,
        "comparison": {
            ticker: data if not isinstance(data, Exception) else {"error": str(data)}
            for ticker, data in zip(tickers, stock_data)
        },
        "metrics": metrics
    }

async def _get_comparison_data(ticker: str, metrics: List[str]) -> Dict[str, Any]:
    """Helper to get comparison data for a ticker"""
    data = {}
    
    if "price" in metrics or "market_cap" in metrics:
        quote = await fd_client.get_quote(ticker)
        data["price"] = quote["price"]
        data["market_cap"] = quote.get("market_cap")
    
    if "pe_ratio" in metrics:
        metrics_data = await fd_client.get_financial_metrics(ticker)
        data["pe_ratio"] = metrics_data.get("pe_ratio")
    
    return data

@register_tool("research_topic")
async def research_topic(
    topic: str,
    depth: str = "standard"
) -> Dict[str, Any]:
    """
    Research a financial topic, concept, or strategy.
    Examples: "What are REITs?", "Explain P/E ratio", "How does DCF work?"
    """
    # Use Exa to search for educational content
    search_results = await exa_client.search(
        query=topic,
        num_results=10,
        category="research paper"
    )
    
    # Extract and synthesize information
    explanation = await _synthesize_explanation(topic, search_results)
    examples = await _find_examples(topic)
    
    return {
        "topic": topic,
        "explanation": explanation,
        "examples": examples,
        "sources": [
            {"title": r.get("title"), "url": r.get("url")}
            for r in search_results.get("results", [])[:5]
        ]
    }

@register_tool("analyze_portfolio")
async def analyze_portfolio(
    holdings: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze user's portfolio for risk, diversification, and optimization.
    holdings format: [{"ticker": "AAPL", "shares": 10, "cost_basis": 150}, ...]
    """
    if not holdings:
        return {"error": "No holdings provided"}
    
    # Get current prices for all holdings
    tickers = [h["ticker"] for h in holdings]
    quotes = await asyncio.gather(*[
        fd_client.get_quote(ticker)
        for ticker in tickers
    ], return_exceptions=True)
    
    total_value = 0
    positions = []
    
    for holding, quote in zip(holdings, quotes):
        if isinstance(quote, Exception):
            continue
            
        current_value = holding["shares"] * quote["price"]
        cost_basis = holding["shares"] * holding.get("cost_basis", quote["price"])
        
        positions.append({
            "ticker": holding["ticker"],
            "shares": holding["shares"],
            "current_price": quote["price"],
            "current_value": current_value,
            "cost_basis": cost_basis,
            "gain_loss": current_value - cost_basis,
            "gain_loss_pct": ((current_value - cost_basis) / cost_basis * 100) if cost_basis else 0
        })
        
        total_value += current_value
    
    # Calculate allocation percentages
    for pos in positions:
        pos["allocation_pct"] = (pos["current_value"] / total_value * 100) if total_value else 0
    
    return {
        "total_value": total_value,
        "positions": positions,
        "position_count": len(positions),
        "top_holdings": sorted(positions, key=lambda x: x["allocation_pct"], reverse=True)[:5]
    }

@register_tool("generate_chart")
async def generate_chart(
    ticker: str,
    timeframe: str = "1M",
    chart_type: str = "candlestick",
    include_volume: bool = True,
    indicators: List[str] = None
) -> Dict[str, Any]:
    """
    Generate interactive chart with technical indicators.
    
    Args:
        ticker: Stock ticker symbol
        timeframe: 1D (intraday), 1W, 1M, 3M, 6M, 1Y, 5Y
        chart_type: candlestick, line, area
        include_volume: Show volume bars
        indicators: Technical indicators to add (ma20, ma50, ma200, rsi, macd)
    
    Examples:
        - "Show me NVDA chart" → candlestick, 1M, with volume
        - "AAPL chart with moving averages" → adds ma20, ma50
        - "Compare NVDA and AMD" → uses generate_comparison_chart instead
    """
    try:
        chart_data = await chart_service.generate_price_chart(
            ticker=ticker,
            timeframe=timeframe,
            chart_type=chart_type,
            include_volume=include_volume,
            indicators=indicators or []
        )
        
        return {
            "success": True,
            "chart": chart_data,
            "ticker": ticker
        }
    
    except Exception as e:
        print(f"❌ Error generating chart: {e}")
        return {"error": str(e), "ticker": ticker}

@register_tool("generate_comparison_chart")
async def generate_comparison_chart(
    tickers: List[str],
    timeframe: str = "1Y"
) -> Dict[str, Any]:
    """
    Generate comparison chart showing multiple stocks normalized to 100 at start.
    Great for comparing relative performance.
    
    Examples:
        - "Compare NVDA and AMD"
        - "Show me AAPL vs MSFT vs GOOGL"
        - "Tech stocks comparison"
    """
    try:
        chart_data = await chart_service.generate_comparison_chart(
            tickers=tickers,
            timeframe=timeframe
        )
        
        return {
            "success": True,
            "chart": chart_data,
            "tickers": tickers
        }
    
    except Exception as e:
        print(f"❌ Error generating comparison chart: {e}")
        return {"error": str(e), "tickers": tickers}

@register_tool("generate_sector_heatmap")
async def generate_sector_heatmap() -> Dict[str, Any]:
    """
    Generate sector performance heatmap showing which sectors are hot/cold today.
    Use when user asks about sector performance or market rotation.
    
    Examples:
        - "Which sectors are performing well?"
        - "Show me sector performance"
        - "What's hot in the market?"
    """
    try:
        heatmap_data = await chart_service.generate_sector_heatmap()
        
        return {
            "success": True,
            "heatmap": heatmap_data
        }
    
    except Exception as e:
        print(f"❌ Error generating sector heatmap: {e}")
        return {"error": str(e)}

@register_tool("screen_stocks")
async def screen_stocks(
    criteria: str,
    universe: str = "sp500"
) -> Dict[str, Any]:
    """
    Screen stocks based on criteria. Use for finding stocks matching specific requirements.
    
    Criteria (natural language, will be parsed):
    - "high growth profitable tech stocks"
    - "value stocks with low PE ratios"
    - "dividend stocks"
    - "small cap growth"
    
    Universe: sp500, tech, growth, dividend
    
    Examples:
        - "Find me undervalued tech stocks"
        - "Show me high dividend stocks"
        - "What are the best growth stocks?"
    """
    try:
        # Parse natural language criteria into filters
        filters = _parse_screening_criteria(criteria)
        
        results = await screener_service.screen_stocks(
            criteria=filters,
            universe=universe
        )
        
        return {
            "success": True,
            "matches": len(results),
            "stocks": results[:10],  # Return top 10
            "criteria": criteria
        }
    
    except Exception as e:
        print(f"❌ Error screening stocks: {e}")
        return {"error": str(e)}

@register_tool("get_top_gainers")
async def get_top_gainers(limit: int = 10) -> Dict[str, Any]:
    """
    Get today's top gaining stocks. Use when user asks "what stocks are up today" or "top gainers".
    """
    try:
        gainers = await screener_service.get_top_gainers(limit)
        
        return {
            "success": True,
            "gainers": gainers,
            "count": len(gainers)
        }
    
    except Exception as e:
        print(f"❌ Error getting top gainers: {e}")
        return {"error": str(e)}

@register_tool("get_top_losers")
async def get_top_losers(limit: int = 10) -> Dict[str, Any]:
    """
    Get today's worst performing stocks. Use when user asks "what stocks are down" or "top losers".
    """
    try:
        losers = await screener_service.get_top_losers(limit)
        
        return {
            "success": True,
            "losers": losers,
            "count": len(losers)
        }
    
    except Exception as e:
        print(f"❌ Error getting top losers: {e}")
        return {"error": str(e)}

@register_tool("get_most_active")
async def get_most_active(limit: int = 10) -> Dict[str, Any]:
    """
    Get most actively traded stocks. Use when user asks "most active stocks" or "highest volume".
    """
    try:
        active = await screener_service.get_most_active(limit)
        
        return {
            "success": True,
            "stocks": active,
            "count": len(active)
        }
    
    except Exception as e:
        print(f"❌ Error getting most active stocks: {e}")
        return {"error": str(e)}

def _parse_screening_criteria(criteria_text: str) -> Dict[str, Any]:
    """Parse natural language screening criteria into filters"""
    criteria = {}
    text_lower = criteria_text.lower()
    
    # Value stocks
    if "value" in text_lower or "undervalued" in text_lower or "low pe" in text_lower:
        criteria["max_pe_ratio"] = 20
        criteria["min_profit_margin"] = 5
    
    # Growth stocks  
    if "growth" in text_lower or "high growth" in text_lower:
        criteria["min_profit_margin"] = 15
        criteria["min_market_cap"] = 5000000000
    
    # Dividend stocks
    if "dividend" in text_lower:
        # Will need dividend data from FDS
        pass
    
    # Size filters
    if "large cap" in text_lower:
        criteria["min_market_cap"] = 10000000000
    elif "mid cap" in text_lower:
        criteria["min_market_cap"] = 2000000000
        criteria["max_market_cap"] = 10000000000
    elif "small cap" in text_lower:
        criteria["max_market_cap"] = 2000000000
    
    # Profitability
    if "profitable" in text_lower:
        criteria["min_profit_margin"] = 0
    
    # Default sorting
    if not criteria.get("sort_by"):
        if "value" in text_lower:
            criteria["sort_by"] = "pe_ratio"
            criteria["sort_order"] = "asc"
        elif "growth" in text_lower:
            criteria["sort_by"] = "profit_margin"
            criteria["sort_order"] = "desc"
        else:
            criteria["sort_by"] = "market_cap"
            criteria["sort_order"] = "desc"
    
    criteria["limit"] = 10
    return criteria

async def _synthesize_explanation(topic: str, content: Any) -> str:
    """Synthesize explanation from search results"""
    # Placeholder - would use LLM to synthesize
    return f"Research on {topic} is being compiled from authoritative sources..."

@register_tool("exa_search")
async def exa_search(
    query: str,
    num_results: int = 10,
    category: str = None,
    include_text: bool = True
) -> Dict[str, Any]:
    """
    Search the web using Exa AI for financial news, research, and analysis.
    Great for finding recent articles, research papers, or specific information.
    """
    try:
        import httpx
        exa_api_key = os.getenv("EXA_API_KEY", "")
        
        if not exa_api_key:
            return {"error": "EXA_API_KEY not configured"}
        
        async with httpx.AsyncClient() as client:
            payload = {
                "query": query,
                "numResults": num_results,
                "type": "auto"
            }
            
            if category:
                payload["category"] = category
            
            if include_text:
                payload["text"] = True
            
            response = await client.post(
                "https://api.exa.ai/search",
                headers={
                    "x-api-key": exa_api_key,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                return {
                    "query": query,
                    "results_count": len(results),
                    "results": [{
                        "title": r.get("title"),
                        "url": r.get("url"),
                        "published_date": r.get("publishedDate"),
                        "author": r.get("author"),
                        "score": r.get("score"),
                        "text_snippet": r.get("text", "")[:500] if r.get("text") else None
                    } for r in results]
                }
            else:
                return {"error": f"Exa API returned {response.status_code}", "details": response.text[:200]}
    
    except Exception as e:
        print(f"❌ Error in exa_search: {e}")
        return {"error": str(e)}

@register_tool("exa_find_similar")
async def exa_find_similar(
    url: str,
    num_results: int = 10
) -> Dict[str, Any]:
    """
    Find web pages similar to a given URL using Exa AI.
    Useful for finding related research, similar companies, or comparable articles.
    """
    try:
        import httpx
        exa_api_key = os.getenv("EXA_API_KEY", "")
        
        if not exa_api_key:
            return {"error": "EXA_API_KEY not configured"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.exa.ai/findSimilar",
                headers={
                    "x-api-key": exa_api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "url": url,
                    "numResults": num_results,
                    "text": True
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                return {
                    "original_url": url,
                    "results_count": len(results),
                    "similar_pages": [{
                        "title": r.get("title"),
                        "url": r.get("url"),
                        "score": r.get("score"),
                        "author": r.get("author")
                    } for r in results]
                }
            else:
                return {"error": f"Exa API returned {response.status_code}"}
    
    except Exception as e:
        print(f"❌ Error in exa_find_similar: {e}")
        return {"error": str(e)}

@register_tool("exa_get_contents")
async def exa_get_contents(
    urls: List[str],
    include_text: bool = True,
    include_summary: bool = False
) -> Dict[str, Any]:
    """
    Get detailed content from specific URLs using Exa AI.
    Useful for extracting full text, summaries, or highlights from web pages.
    """
    try:
        import httpx
        exa_api_key = os.getenv("EXA_API_KEY", "")
        
        if not exa_api_key:
            return {"error": "EXA_API_KEY not configured"}
        
        async with httpx.AsyncClient() as client:
            payload = {"urls": urls}
            
            if include_text:
                payload["text"] = {"maxCharacters": 2000}
            
            if include_summary:
                payload["summary"] = {"query": "Key points and main ideas"}
            
            response = await client.post(
                "https://api.exa.ai/contents",
                headers={
                    "x-api-key": exa_api_key,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                return {
                    "urls_count": len(urls),
                    "contents": [{
                        "url": r.get("url"),
                        "title": r.get("title"),
                        "text": r.get("text"),
                        "summary": r.get("summary"),
                        "author": r.get("author"),
                        "published_date": r.get("publishedDate")
                    } for r in results]
                }
            else:
                return {"error": f"Exa API returned {response.status_code}"}
    
    except Exception as e:
        print(f"❌ Error in exa_get_contents: {e}")
        return {"error": str(e)}

@register_tool("exa_answer")
async def exa_answer(
    query: str
) -> Dict[str, Any]:
    """
    Get a direct answer to a question using Exa AI's answer endpoint.
    Exa searches the web and generates an answer with citations.
    Great for factual questions about markets, companies, or financial concepts.
    """
    try:
        import httpx
        exa_api_key = os.getenv("EXA_API_KEY", "")
        
        if not exa_api_key:
            return {"error": "EXA_API_KEY not configured"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.exa.ai/answer",
                headers={
                    "x-api-key": exa_api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "query": query,
                    "text": True
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "query": query,
                    "answer": data.get("answer"),
                    "citations": [{
                        "title": c.get("title"),
                        "url": c.get("url"),
                        "published_date": c.get("publishedDate"),
                        "author": c.get("author")
                    } for c in data.get("citations", [])]
                }
            else:
                return {"error": f"Exa API returned {response.status_code}"}
    
    except Exception as e:
        print(f"❌ Error in exa_answer: {e}")
        return {"error": str(e)}

async def _find_examples(topic: str) -> List[str]:
    """Find concrete examples for a topic"""
    # Placeholder
    return ["Example 1", "Example 2", "Example 3"]

def _get_start_date(timeframe: str) -> str:
    """Convert timeframe to start date"""
    now = datetime.now()
    if timeframe == "1h":
        start = now - timedelta(hours=1)
    elif timeframe == "24h":
        start = now - timedelta(days=1)
    elif timeframe == "1W":
        start = now - timedelta(weeks=1)
    else:  # 1M
        start = now - timedelta(days=30)
    
    return start.strftime("%Y-%m-%d")

