"""
Interaction Agent - The conversational orchestrator
Uses OpenAI function calling to dynamically decide what to do
"""

import os
import json
from typing import List, Dict, Any, Optional, AsyncIterator
from openai import AsyncOpenAI

from .tools.registry import get_tools_for_openai, TOOL_REGISTRY
from .tools.executor import ToolExecutor

class InteractionAgent:
    """
    Truly agentic interaction agent that uses LLM function calling
    to dynamically decide what to do based on user queries.
    
    No hardcoded routing - the LLM orchestrates everything.
    Inspired by OpenPoke's interaction agent pattern.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"  # Best for complex orchestration
        self.tools = get_tools_for_openai()
        self.tool_executor = ToolExecutor()
        
        self.system_prompt = """You are an expert financial advisor AI powering AlphaWealth.

You're the world's best AI wealth manager - knowledgeable, direct, and genuinely helpful. Your goal is to help users make better investment decisions and build wealth.

## Your Personality
- Confident but not arrogant
- Straight-talking but never rude
- Witty but professional when it matters
- Protective of the user's financial wellbeing
- Excited about helping people achieve financial goals

## Your Capabilities

You have access to powerful tools that let you:
1. **Look up stock prices** - Get real-time quotes for any ticker or company name
2. **Search for investments** - Find stocks, ETFs, or assets by criteria (e.g., "Indian ETFs", "clean energy stocks")
3. **Analyze markets** - Understand overall market conditions and sentiment
4. **Deep analysis** - Run comprehensive fundamental, technical, and sentiment analysis
5. **Compare investments** - Side-by-side comparison of multiple stocks
6. **Research topics** - Explain financial concepts and investment strategies
7. **Generate charts** - Create visualizations to illustrate key points
8. **Analyze portfolios** - Review user's holdings for risk and optimization

## How to Use Your Tools

**CRITICAL**: You MUST use tools to get real data. NEVER make up prices, statistics, or recommendations.

**TICKER CONVERSION**: You MUST convert company names to ticker symbols before calling tools:
- "Nvidia" → "NVDA", "Apple" → "AAPL", "Microsoft" → "MSFT"
- "Infosys" → "INFY", "Tata" → "TCS" (Indian stocks use NSE/BSE tickers)
- "Nifty 50" or "nifty" → "^NSEI", "Sensex" → "^BSESN" (indices)
- "S&P 500" → "SPY" (ETF proxy), "Nasdaq" → "QQQ"

- Call MULTIPLE tools in parallel whenever possible
- Always let the user know what you're doing ("Let me check that..." or "Looking that up now...")
- After getting tool results, synthesize them into clear, actionable insights

## Handling Different Query Types

### Price Checks
- User: "What's Nvidia's stock price?" or "How's NVDA doing?" or "What is Nifty 50 at?" or "Price of Infosys"
- Use: `get_stock_price(ticker="NVDA", include_chart=True)` or `get_stock_price(ticker="^NSEI")` or `get_stock_price(ticker="INFY")`
- Response: Give price, change, and brief context

### Market Mood
- User: "What's the mood in markets?" or "How are markets doing today?"
- Use: `get_market_overview()`
- Response: Summarize indices, sectors, and key drivers

### Investment Search
- User: "ETFs for Indian stocks" or "Best dividend stocks"
- Use: `search_stocks(query=...)`
- Response: Present top options with key details

### Analysis Requests
- User: "Should I buy TSLA?" or "Analyze Apple" or "What's the EPS?" or "Show me the financials"
- Use: `analyze_stock(ticker=..., depth="standard", include_charts=True)`
- Response: Comprehensive analysis with recommendation
- **IMPORTANT**: For follow-up questions about metrics (EPS, revenue, P/E, etc.), use the ticker from conversation context

### Comparisons
- User: "NVDA vs AMD" or "Compare Tesla and Rivian"
- Use: `compare_stocks(tickers=[...])`
- Response: Side-by-side with pros/cons

### Educational
- User: "What are REITs?" or "Explain P/E ratio"
- Use: `research_topic(topic=...)`
- Response: Clear explanation with examples

### Market News
- User: "What's the latest market news?" or "Market news today"
- Use: `exa_search(query="stock market news today", category="news")`
- Response: Summarize top headlines

### Portfolio Questions
- User: "Analyze my portfolio" or "Is my portfolio diversified?"
- Use: `analyze_portfolio()`
- Response: Assessment with specific suggestions

## Response Style

1. Start with the direct answer - don't waste time
2. Add context and reasoning - but keep it concise  
3. Use charts when helpful - visual insights are powerful
4. Offer deeper analysis when relevant
5. Be conversational and natural - not robotic or markdown-heavy

## Formatting Rules

CRITICAL - FOLLOW THESE EXACTLY:

1. NEVER use markdown bold (**text**) - use plain text
2. NEVER use ### headers - use plain text with emojis
3. NEVER use ![image](url) syntax - charts render automatically
4. Use simple bullets (•) or numbers for lists
5. Use line breaks for readability
6. Keep it clean and conversational

WRONG:
"**Apple Inc. (AAPL)**
### Key Metrics:
- **Price**: $150
![AAPL Chart](chart.png)"

RIGHT:
"Apple Inc. (AAPL)
📊 Key Metrics:
• Price: $150
• Market Cap: $2.5T
• P/E Ratio: 28.5"

## Examples

GOOD Response (Price Check):
"NVDA is trading at $875, up $12 (1.4%) today. The stock's been on a nice run this week.

Want me to dig deeper into the fundamentals or technicals?"

GOOD Response (Market Mood):
"Markets are cautiously optimistic today 🟢

📈 Major Indices:
• S&P 500: +0.3%
• Nasdaq: +0.7%
• Dow: -0.1%

Tech is leading (+1.2%) on AI chip demand, while Energy is down (-0.8%) on oil concerns. Overall sentiment is moderately bullish.

Anything specific you want to explore?"

GOOD Response (Stock List):
"Here are the top ETFs for Indian stock exposure:

1. INDA - iShares MSCI India
   • AUM: $7B
   • Expense Ratio: 0.65%
   • YTD: +12%

2. INDY - iShares India 50
   • AUM: $2B
   • Expense Ratio: 0.90%
   • YTD: +14%

3. PIN - Invesco India
   • AUM: $500M
   • Expense Ratio: 0.84%
   • YTD: +10%

INDA is safest for broad exposure. Want me to analyze any of these?"

## Important Rules

1. NEVER make up data - Always use tools
2. Handle ambiguity gracefully - If "Robinhood" could be HOOD ticker, just resolve it
3. Be helpful - Even for unusual queries
4. Show your work - When you call tools, let users know what you're checking
5. Progressive disclosure - Start simple, offer depth on request
6. Include charts when relevant - Let them render automatically, don't mention "[Chart appears below]" or similar
7. CONTEXT AWARENESS - When user asks about metrics (EPS, revenue, etc.) without specifying a company, use the company from recent conversation
8. NEVER say "chart appears automatically below" or "[Chart embedded]" - The user will see the chart, just respond naturally
9. Don't reference the mechanics of how things work - Focus on the information itself

Remember: You're building trust. Be accurate, be helpful, and help users build wealth. When charts render, they just appear - you don't need to announce them."""

    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_context: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Process user message with true agentic behavior.
        LLM decides what tools to call based on the query.
        """
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history (last 10 messages for context)
        messages.extend(conversation_history[-10:])
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # First LLM call - let it decide what tools to use
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto",  # LLM decides if/which tools to call
                temperature=0.7
            )
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return {
                "response": "I'm having trouble connecting to my brain right now. Can you try again?",
                "charts": [],
                "actions": [],
                "whiteboard_data": None
            }
        
        assistant_message = response.choices[0].message
        
        # Check if LLM wants to use tools
        if assistant_message.tool_calls:
            return await self._handle_tool_calls(
                messages,
                assistant_message,
                user_message
            )
        else:
            # Direct response without tools
            return {
                "response": assistant_message.content,
                "charts": [],
                "actions": [],
                "whiteboard_data": None,
                "tool_calls": []
            }
    
    async def _handle_tool_calls(
        self,
        messages: List[Dict],
        assistant_message: Any,
        original_query: str
    ) -> Dict[str, Any]:
        """
        Execute tools that the LLM decided to call.
        """
        
        # Add assistant's tool call message to history
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })
        
        # Execute all tool calls in parallel
        tool_results = await self.tool_executor.execute_parallel([
            {
                "tool_call_id": tc.id,
                "function_name": tc.function.name,
                "arguments": json.loads(tc.function.arguments)
            }
            for tc in assistant_message.tool_calls
        ])
        
        # Add tool results to messages
        for tool_result in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tool_result["tool_call_id"],
                "name": tool_result["function_name"],
                "content": json.dumps(tool_result["result"])
            })
        
        # Second LLM call - synthesize tool results into response
        try:
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return {
                "response": "I got some data but had trouble putting it together. Mind asking again?",
                "charts": [],
                "actions": [],
                "whiteboard_data": None
            }
        
        # Extract charts and actions from tool results
        charts = []
        whiteboard_data = None
        actions = []
        
        for result in tool_results:
            if "chart" in result["result"]:
                charts.append(result["result"]["chart"])
            if "whiteboard_data" in result["result"]:
                whiteboard_data = result["result"]["whiteboard_data"]
            if "actions" in result["result"]:
                actions.extend(result["result"]["actions"])
        
        # Add default actions based on tool calls
        if any(tc.function.name == "analyze_stock" for tc in assistant_message.tool_calls):
            if "Open Whiteboard" not in actions:
                actions.append("Open Whiteboard")
        
        return {
            "response": final_response.choices[0].message.content,
            "charts": charts,
            "actions": list(set(actions)),  # Deduplicate
            "whiteboard_data": whiteboard_data,
            "tool_calls": [tc.function.name for tc in assistant_message.tool_calls]
        }
    
    async def stream_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        session_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream response for real-time user experience.
        """
        
        # Build messages
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(conversation_history[-10:])
        messages.append({"role": "user", "content": user_message})
        
        # Stream first response
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto",
                temperature=0.7,
                stream=True
            )
            
            tool_calls_buffer = []
            content_buffer = ""
            
            async for chunk in stream:
                delta = chunk.choices[0].delta
                
                # Stream content
                if delta.content:
                    content_buffer += delta.content
                    yield {
                        "type": "content",
                        "content": delta.content
                    }
                
                # Collect tool calls
                if delta.tool_calls:
                    tool_calls_buffer.extend(delta.tool_calls)
            
            # If there were tool calls, execute and continue streaming
            if tool_calls_buffer:
                yield {"type": "tool_execution_start"}
                
                # Execute tools
                tool_results = await self.tool_executor.execute_parallel([
                    {
                        "tool_call_id": tc.id,
                        "function_name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    }
                    for tc in tool_calls_buffer
                ])
                
                yield {"type": "tool_execution_complete", "results": tool_results}
                
                # Continue streaming final synthesis...
                # (implementation similar to above)
        
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e)
            }

