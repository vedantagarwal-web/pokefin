"""
Tool Implementations - Actual functions that get called
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from .registry import register_tool
from services.financial_datasets_client import FinancialDatasetsClient
from services.exa_client import ExaClient

# Initialize clients
fd_client = FinancialDatasetsClient()
exa_client = ExaClient()

@register_tool("get_stock_price")
async def get_stock_price(
    ticker: str,
    timeframe: str = "current",
    include_chart: bool = False
) -> Dict[str, Any]:
    """
    Get stock price for a ticker symbol.
    LLM should convert company names to tickers (e.g., "Nvidia" -> "NVDA", "Infosys" -> "INFY").
    """
    
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
            # Get intraday data for chart
            intraday_data = await fd_client.get_intraday_prices(ticker)
            result["chart"] = {
                "type": "line",
                "ticker": ticker,
                "data": intraday_data,
                "timeframe": "1D"
            }
        
        return result
    
    else:
        # Historical data
        historical_data = await fd_client.get_historical_prices(ticker, timeframe=timeframe)
        
        result = {
            "ticker": ticker,
            "company_name": company_name,
            "timeframe": timeframe,
            "start_price": historical_data[0]["close"],
            "end_price": historical_data[-1]["close"],
            "return_pct": ((historical_data[-1]["close"] - historical_data[0]["close"]) / historical_data[0]["close"]) * 100
        }
        
        if include_chart:
            result["chart"] = {
                "type": "candlestick",
                "ticker": ticker,
                "data": historical_data,
                "timeframe": timeframe
            }
        
        return result

@register_tool("get_financials")
async def get_financials(
    ticker: str,
    period: str = "quarterly"
) -> Dict[str, Any]:
    """
    Get financial statements and key metrics like EPS, revenue, margins.
    """
    
    # Resolve ticker if needed
    resolution = await ticker_resolver.resolve(ticker)
    if not resolution.get("ticker"):
        return {"error": f"Could not find ticker for {ticker}"}
    
    ticker = resolution["ticker"]
    
    try:
        # Get income statement for EPS, revenue, profit margins
        response = await fd_client.client.get(
            f"{fd_client.base_url}/financials/income-statements",
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
                    "company_name": resolution.get("company_name"),
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
    resolution = await ticker_resolver.resolve(ticker)
    if not resolution.get("ticker"):
        return {"error": f"Could not find ticker for {ticker}"}
    
    ticker = resolution["ticker"]
    
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/financials/balance-sheets",
            params={"ticker": ticker, "period": period, "limit": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("balance_sheets"):
                bs = data["balance_sheets"][0]
                return {
                    "ticker": ticker,
                    "company_name": resolution.get("company_name"),
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
    resolution = await ticker_resolver.resolve(ticker)
    if not resolution.get("ticker"):
        return {"error": f"Could not find ticker for {ticker}"}
    
    ticker = resolution["ticker"]
    
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/financials/cash-flow-statements",
            params={"ticker": ticker, "period": period, "limit": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("cash_flow_statements"):
                cf = data["cash_flow_statements"][0]
                return {
                    "ticker": ticker,
                    "company_name": resolution.get("company_name"),
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
    resolution = await ticker_resolver.resolve(ticker)
    if not resolution.get("ticker"):
        return {"error": f"Could not find ticker for {ticker}"}
    
    ticker = resolution["ticker"]
    
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/financial-metrics",
            params={"ticker": ticker, "period": period, "limit": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            # FDS returns metrics directly or in an array
            metrics = data if isinstance(data, dict) else data[0] if isinstance(data, list) and data else {}
            
            return {
                "ticker": ticker,
                "company_name": resolution.get("company_name"),
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
    resolution = await ticker_resolver.resolve(ticker)
    if not resolution.get("ticker"):
        return {"error": f"Could not find ticker for {ticker}"}
    
    ticker = resolution["ticker"]
    
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/news",
            params={"ticker": ticker, "limit": limit}
        )
        
        if response.status_code == 200:
            data = response.json()
            news_items = data.get("news", [])
            
            return {
                "ticker": ticker,
                "company_name": resolution.get("company_name"),
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
    resolution = await ticker_resolver.resolve(ticker)
    if not resolution.get("ticker"):
        return {"error": f"Could not find ticker for {ticker}"}
    
    ticker = resolution["ticker"]
    
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/insider-trades",
            params={"ticker": ticker, "limit": limit}
        )
        
        if response.status_code == 200:
            data = response.json()
            trades = data.get("insider_trades", [])
            
            return {
                "ticker": ticker,
                "company_name": resolution.get("company_name"),
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
    resolution = await ticker_resolver.resolve(ticker)
    if not resolution.get("ticker"):
        return {"error": f"Could not find ticker for {ticker}"}
    
    ticker = resolution["ticker"]
    
    try:
        response = await fd_client.client.get(
            f"{fd_client.base_url}/institutional-ownership",
            params={"ticker": ticker, "limit": limit}
        )
        
        if response.status_code == 200:
            data = response.json()
            holdings = data.get("institutional-ownership", [])
            
            return {
                "ticker": ticker,
                "company_name": resolution.get("company_name"),
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
    Search for stocks by criteria.
    """
    
    # Use Exa AI for semantic search
    search_results = await exa_client.search(
        query=f"{query} stock ticker invest",
        num_results=limit * 2
    )
    
    # Extract tickers from results
    tickers = await _extract_tickers_from_search(search_results)
    
    # Get details for each ticker
    ticker_details = []
    for ticker in tickers[:limit]:
        try:
            profile = await fd_client.get_company_profile(ticker)
            ticker_details.append(profile)
        except:
            continue
    
    return {
        "query": query,
        "results": [
            {
                "ticker": detail["symbol"],
                "name": detail["name"],
                "sector": detail.get("sector"),
                "industry": detail.get("industry"),
                "market_cap": detail.get("market_cap"),
                "description": detail.get("description", "")[:200]
            }
            for detail in ticker_details
        ],
        "count": len(ticker_details)
    }

@register_tool("get_market_overview")
async def get_market_overview(
    include_indices: bool = True,
    include_sectors: bool = True,
    include_sentiment: bool = True
) -> Dict[str, Any]:
    """
    Get overall market overview and sentiment.
    """
    
    result = {}
    
    if include_indices:
        # Get major indices
        indices = await asyncio.gather(
            fd_client.get_quote("SPY"),   # S&P 500
            fd_client.get_quote("QQQ"),   # Nasdaq
            fd_client.get_quote("DIA"),   # Dow
            return_exceptions=True
        )
        
        result["indices"] = {
            "sp500": {
                "price": indices[0]["price"] if not isinstance(indices[0], Exception) else None,
                "change_percent": indices[0]["change_percent"] if not isinstance(indices[0], Exception) else 0
            },
            "nasdaq": {
                "price": indices[1]["price"] if not isinstance(indices[1], Exception) else None,
                "change_percent": indices[1]["change_percent"] if not isinstance(indices[1], Exception) else 0
            },
            "dow": {
                "price": indices[2]["price"] if not isinstance(indices[2], Exception) else None,
                "change_percent": indices[2]["change_percent"] if not isinstance(indices[2], Exception) else 0
            }
        }
    
    if include_sectors:
        # Get sector performance via sector ETFs
        sector_etfs = {
            "Technology": "XLK",
            "Healthcare": "XLV",
            "Financials": "XLF",
            "Energy": "XLE",
            "Consumer Discretionary": "XLY",
        }
        
        sector_data = await asyncio.gather(*[
            fd_client.get_quote(etf)
            for etf in sector_etfs.values()
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
    
    return {
        **result,
        "actions": ["Open Whiteboard", "Add to Watchlist"]
    }

@register_tool("compare_stocks")
async def compare_stocks(
    tickers: List[str],
    timeframe: str = "1Y",
    include_chart: bool = True
) -> Dict[str, Any]:
    """
    Compare multiple stocks.
    """
    
    # Get data for all tickers in parallel
    comparisons = await asyncio.gather(*[
        _get_stock_comparison_data(ticker, timeframe)
        for ticker in tickers
    ])
    
    result = {
        "tickers": tickers,
        "timeframe": timeframe,
        "comparisons": [
            comp for comp in comparisons if comp is not None
        ]
    }
    
    if include_chart:
        # Create comparison chart
        result["chart"] = {
            "type": "multi_line",
            "tickers": tickers,
            "timeframe": timeframe,
            "data": await _create_comparison_chart_data(tickers, timeframe)
        }
    
    return result

@register_tool("research_topic")
async def research_topic(
    topic: str,
    include_examples: bool = True
) -> Dict[str, Any]:
    """
    Research a financial topic using Exa AI.
    """
    
    # Use Exa to search for authoritative content
    results = await exa_client.search(
        query=f"{topic} investing finance explained",
        num_results=5,
        category="financial_education"
    )
    
    # Get detailed content
    content = await exa_client.get_contents([r["id"] for r in results.results])
    
    # Synthesize explanation
    explanation = await _synthesize_explanation(topic, content)
    
    result = {
        "topic": topic,
        "explanation": explanation,
        "sources": [
            {
                "title": r["title"],
                "url": r["url"]
            }
            for r in results.results
        ]
    }
    
    if include_examples:
        result["examples"] = await _find_examples(topic)
    
    return result

@register_tool("get_news")
async def get_news(
    query: str,
    timeframe: str = "24h"
) -> Dict[str, Any]:
    """
    Get recent financial news.
    """
    
    # Search for news using Exa
    news_results = await exa_client.search(
        query=f"{query} stock news",
        num_results=10,
        type="news",
        start_published_date=_get_start_date(timeframe)
    )
    
    return {
        "query": query,
        "timeframe": timeframe,
        "articles": [
            {
                "title": r["title"],
                "url": r["url"],
                "published": r.get("published_date"),
                "summary": r.get("text", "")[:200]
            }
            for r in news_results.results
        ],
        "count": len(news_results.results)
    }

@register_tool("find_similar_stocks")
async def find_similar_stocks(
    ticker: str,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Find stocks similar to a given ticker.
    """
    
    # Get company profile
    profile = await fd_client.get_company_profile(ticker)
    
    # Search for similar companies
    search_query = f"{profile['sector']} {profile['industry']} stocks similar to {ticker}"
    similar = await exa_client.search(search_query, num_results=limit * 2)
    
    # Extract and validate tickers
    similar_tickers = await _extract_tickers_from_search(similar)
    similar_tickers = [t for t in similar_tickers if t != ticker][:limit]
    
    # Get details
    details = await asyncio.gather(*[
        fd_client.get_company_profile(t)
        for t in similar_tickers
    ])
    
    return {
        "reference_ticker": ticker,
        "similar_stocks": [
            {
                "ticker": d["symbol"],
                "name": d["name"],
                "sector": d.get("sector"),
                "market_cap": d.get("market_cap")
            }
            for d in details if d
        ]
    }

# Helper functions

async def _extract_tickers_from_search(search_results) -> List[str]:
    """Extract ticker symbols from search results"""
    # Placeholder - would use NER or pattern matching
    # For now, return some popular tickers based on search
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"][:5]

async def _get_stock_comparison_data(ticker: str, timeframe: str) -> Optional[Dict[str, Any]]:
    """Get comparison data for a single stock"""
    try:
        quote = await fd_client.get_quote(ticker)
        historical = await fd_client.get_historical_prices(ticker, timeframe)
        
        return {
            "ticker": ticker,
            "current_price": quote["price"],
            "return_pct": ((historical[-1]["close"] - historical[0]["close"]) / historical[0]["close"]) * 100,
            "volatility": _calculate_volatility(historical),
            "market_cap": quote.get("market_cap")
        }
    except:
        return None

async def _create_comparison_chart_data(tickers: List[str], timeframe: str):
    """Create normalized comparison chart data"""
    all_data = await asyncio.gather(*[
        fd_client.get_historical_prices(ticker, timeframe)
        for ticker in tickers
    ])
    
    # Normalize to 100 at start
    normalized = []
    for ticker, data in zip(tickers, all_data):
        if data:
            start_price = data[0]["close"]
            normalized.append({
                "ticker": ticker,
                "data": [
                    {
                        "time": d["date"],
                        "value": (d["close"] / start_price) * 100
                    }
                    for d in data
                ]
            })
    
    return normalized

def _calculate_volatility(price_data: List[Dict]) -> float:
    """Calculate annualized volatility"""
    # Simplified calculation
    if len(price_data) < 2:
        return 0
    
    returns = []
    for i in range(1, len(price_data)):
        ret = (price_data[i]["close"] - price_data[i-1]["close"]) / price_data[i-1]["close"]
        returns.append(ret)
    
    import math
    variance = sum((r - sum(returns)/len(returns))**2 for r in returns) / len(returns)
    return math.sqrt(variance * 252) * 100  # Annualized

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

