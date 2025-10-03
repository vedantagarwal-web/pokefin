"""
AlphaWealth - Main FastAPI Application
The world's best AI financial wealth manager
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from agents.system import AlphaWealthSystem
from services.session_manager import SessionManager

# Load environment variables
load_dotenv()

# Initialize services on startup
alpha_system = None
session_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global alpha_system, session_manager
    
    print("🚀 Starting AlphaWealth...")
    
    # Initialize the AI system
    alpha_system = AlphaWealthSystem()
    session_manager = SessionManager()
    
    print("✅ AlphaWealth is ready!")
    
    yield
    
    print("👋 Shutting down AlphaWealth...")

# Create FastAPI app
app = FastAPI(
    title="AlphaWealth API",
    description="AI-powered financial wealth management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8787").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    session: str
    messages: List[Dict[str, str]]

class ChatResponse(BaseModel):
    response: str
    charts: List[Dict[str, Any]] = []
    actions: List[str] = []
    whiteboard_data: Optional[Dict[str, Any]] = None
    tool_calls: List[str] = []
    timestamp: str

class ChartRequest(BaseModel):
    ticker: str
    timeframe: str = "6M"
    chart_type: str = "candlestick"
    indicators: List[str] = []

# Health check
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "AlphaWealth",
        "version": "1.0.0",
        "message": "The world's best AI financial wealth manager"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Main chat endpoint
@app.post("/api/v2/chat/send")
async def chat_send(request: ChatRequest):
    """
    Main conversational endpoint with multi-agent orchestration
    """
    try:
        # Extract the latest user message
        if not request.messages or len(request.messages) == 0:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        user_message = request.messages[-1].get("content", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Empty message")
        
        # Get or create session
        session_data = await session_manager.get_session(request.session)
        
        # Process message through AlphaWealth system
        result = await alpha_system.process_message(
            message=user_message,
            history=request.messages[:-1],  # All messages except the last one
            session_id=request.session,
            user_context=session_data.get("user_context", {})
        )
        
        # Update session with new messages (including charts)
        all_messages = session_data.get("messages", [])
        all_messages.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        all_messages.append({
            "role": "assistant",
            "content": result["response"],
            "timestamp": datetime.now().isoformat(),
            "charts": result.get("charts", []),
            "actions": result.get("actions", []),
            "whiteboard_data": result.get("whiteboard_data")
        })
        
        await session_manager.update_session(
            request.session,
            {
                "messages": all_messages,
                "last_message": user_message,
                "last_response": result["response"],
                "updated_at": datetime.now().isoformat()
            }
        )
        
        return {
            "ok": True,
            "response": result["response"],
            "charts": result.get("charts", []),
            "actions": result.get("actions", []),
            "whiteboard_data": result.get("whiteboard_data"),
            "tool_calls": result.get("tool_calls", []),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )

# Chat history endpoint
@app.get("/api/v2/chat/history")
async def get_chat_history(session: str):
    """
    Get chat history for a session
    """
    try:
        session_data = await session_manager.get_session(session)
        messages = session_data.get("messages", [])
        
        return {
            "ok": True,
            "messages": messages
        }
    
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        return {"ok": True, "messages": []}

# Clear chat history
@app.delete("/api/v2/chat/history")
async def clear_chat_history(session: str):
    """
    Clear chat history for a session
    """
    try:
        await session_manager.delete_session(session)
        return {"ok": True, "message": "Chat history cleared"}
    
    except Exception as e:
        print(f"❌ Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chart data endpoint
@app.post("/api/v2/chart")
async def get_chart_data(request: ChartRequest):
    """
    Get chart data for embedding in chat
    """
    try:
        chart_data = await alpha_system.chart_agent.generate_chart(
            ticker=request.ticker,
            timeframe=request.timeframe,
            chart_type=request.chart_type,
            indicators=request.indicators
        )
        
        return chart_data
    
    except Exception as e:
        print(f"❌ Error generating chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket for streaming responses
@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    Real-time streaming chat via WebSocket
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            history = data.get("history", [])
            
            # Stream response
            async for chunk in alpha_system.stream_message(
                message=message,
                history=history,
                session_id=session_id
            ):
                await websocket.send_json(chunk)
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

# Quick stock price lookup
@app.get("/api/v2/price/{ticker}")
async def get_stock_price(ticker: str):
    """
    Quick stock price lookup
    """
    try:
        from agents.tools.implementations import get_stock_price
        
        result = await get_stock_price(
            query=ticker,
            timeframe="current",
            include_chart=False
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not find price for {ticker}")

# Market overview
@app.get("/api/v2/market/overview")
async def get_market_overview():
    """
    Get market overview and sentiment
    """
    try:
        from agents.tools.implementations import get_market_overview
        
        result = await get_market_overview(
            include_indices=True,
            include_sectors=True,
            include_sentiment=True
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Session management
@app.get("/api/v2/session/{session_id}")
async def get_session(session_id: str):
    """
    Get session data
    """
    session = await session_manager.get_session(session_id)
    return session

@app.delete("/api/v2/session/{session_id}")
async def delete_session(session_id: str):
    """
    Clear session data
    """
    await session_manager.delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}

# Research storage (in-memory for now, will move to Supabase)
research_store = {}

@app.post("/api/research/save")
async def save_research(data: dict):
    """Save research report for whiteboard access"""
    ticker = data.get("ticker")
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker required")
    
    research_store[ticker] = data
    return {"status": "saved", "ticker": ticker}

@app.get("/api/research/{ticker}")
async def get_research(ticker: str):
    """Get research report for whiteboard"""
    if ticker not in research_store:
        raise HTTPException(status_code=404, detail=f"No research found for {ticker}")
    
    return research_store[ticker]

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8788))
    
    print(f"""
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║          🚀 AlphaWealth 🚀            ║
    ║                                       ║
    ║   The World's Best AI Financial       ║
    ║        Wealth Manager                 ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
    
    Starting on http://localhost:{port}
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

