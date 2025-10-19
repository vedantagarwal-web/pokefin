"""
AlphaWealth - Main FastAPI Application
The world's best AI financial wealth manager
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
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
from services.robinhood_client import RobinhoodClient
# SnapTrade removed - using mock portfolio for recommendations
# from services.snaptrade_client import SnapTradeClient
from services.supabase_client import supabase_client

# Load environment variables
load_dotenv()

# Initialize services on startup
alpha_system = None
session_manager = None
robinhood_client = None
# snaptrade_client = None  # Removed

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global alpha_system, session_manager, robinhood_client  # snaptrade_client removed
    
    print("🚀 Starting AlphaWealth...")
    
    # Initialize the AI system
    alpha_system = AlphaWealthSystem()
    session_manager = SessionManager()
    
    # Initialize clients
    robinhood_client = RobinhoodClient()
    # snaptrade_client = SnapTradeClient()  # Removed - using mock portfolio
    
    # Check Supabase client
    if supabase_client.is_available():
        print("✅ Supabase client initialized")
    else:
        print("❌ Supabase client not available")
    
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

# SnapTrade Integration Endpoints - REMOVED
# All SnapTrade endpoints have been removed.
# Portfolio recommendations now use the mock portfolio system.
# See SNAPTRADE_REMOVED.md for details.

# OAuth2 Robinhood Integration Endpoints (Legacy - no longer publicly available)
# Note: Robinhood no longer provides public OAuth2 API access
# SnapTrade endpoints have been removed - see SNAPTRADE_REMOVED.md


@app.get("/api/robinhood/portfolio")
async def robinhood_portfolio(access_token: str, account_id: Optional[str] = None):
    """Get Robinhood portfolio summary"""
    try:
        result = await robinhood_client.get_portfolios(access_token, account_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
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

# Authentication Models
class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class SignInRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    user: Optional[Dict[str, Any]] = None
    session: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Authentication endpoints
@app.post("/api/auth/signup", response_model=AuthResponse)
async def sign_up(request: SignUpRequest):
    """Sign up a new user"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    result = await supabase_client.sign_up(
        email=request.email,
        password=request.password,
        user_metadata={"full_name": request.full_name} if request.full_name else None
    )
    
    if result["success"]:
        # Create profile
        profile_result = await supabase_client.create_profile(
            user_id=result["user"]["id"],
            email=request.email,
            full_name=request.full_name
        )
        
        if not profile_result["success"]:
            # Profile creation failed, but user was created
            pass
        
        # Convert session object to dict if it exists
        if result.get("session"):
            if hasattr(result["session"], 'model_dump'):
                result["session"] = result["session"].model_dump()
            elif hasattr(result["session"], 'dict'):
                result["session"] = result["session"].dict()
    
    return AuthResponse(**result)

@app.post("/api/auth/google")
async def sign_in_with_google():
    """Initiate Google OAuth sign-in"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    try:
        # Generate Google OAuth URL using Supabase client
        auth_url = await supabase_client.get_google_auth_url()
        
        if not auth_url:
            return {
                "success": False,
                "error": "Failed to generate Google OAuth URL"
            }
        
        return {
            "success": True,
            "auth_url": auth_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/auth/google/callback")
async def google_oauth_callback(code: str = None, error: str = None):
    """Handle Google OAuth callback"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    if error:
        return {
            "success": False,
            "error": f"Google OAuth error: {error}"
        }
    
    if not code:
        return {
            "success": False,
            "error": "No authorization code received"
        }
    
    try:
        # Exchange code for session using Supabase client
        result = await supabase_client.exchange_oauth_code(code)
        
        if result["success"]:
            # Convert session object to dict if it exists
            if result.get("session"):
                if hasattr(result["session"], 'model_dump'):
                    result["session"] = result["session"].model_dump()
                elif hasattr(result["session"], 'dict'):
                    result["session"] = result["session"].dict()
            
            return result
        else:
            return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/auth/signin", response_model=AuthResponse)
async def sign_in(request: SignInRequest):
    """Sign in an existing user"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    result = await supabase_client.sign_in(
        email=request.email,
        password=request.password
    )
    
    # Convert session object to dict if it exists
    if result.get("session"):
        if hasattr(result["session"], 'model_dump'):
            result["session"] = result["session"].model_dump()
        elif hasattr(result["session"], 'dict'):
            result["session"] = result["session"].dict()
    
    return AuthResponse(**result)

@app.post("/api/auth/signout")
async def sign_out(authorization: Optional[str] = None):
    """Sign out the current user"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    result = await supabase_client.sign_out(token)
    
    return result

@app.get("/api/auth/user")
async def get_current_user(authorization: Optional[str] = None):
    """Get current user information"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    result = await supabase_client.get_user(token)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result

# Profile endpoints
@app.get("/api/user/profile")
async def get_profile(authorization: Optional[str] = None):
    """Get user profile"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    # Get user first to verify token
    user_result = await supabase_client.get_user(token)
    if not user_result["success"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get profile
    profile_result = await supabase_client.get_profile(user_result["user"]["id"])
    
    if not profile_result["success"]:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile_result

@app.put("/api/user/profile")
async def update_profile(request: Dict[str, Any], authorization: Optional[str] = None):
    """Update user profile"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    # Get user first to verify token
    user_result = await supabase_client.get_user(token)
    if not user_result["success"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Update profile
    profile_result = await supabase_client.update_profile(user_result["user"]["id"], request)
    
    if not profile_result["success"]:
        raise HTTPException(status_code=400, detail=profile_result["error"])
    
    return profile_result

# Portfolio endpoints
@app.post("/api/portfolios")
async def create_portfolio(request: Dict[str, Any], authorization: Optional[str] = None):
    """Create a new portfolio"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    # Get user first to verify token
    user_result = await supabase_client.get_user(token)
    if not user_result["success"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Create portfolio
    portfolio_result = await supabase_client.create_portfolio(
        user_id=user_result["user"]["id"],
        name=request.get("name", "My Portfolio"),
        description=request.get("description")
    )
    
    if not portfolio_result["success"]:
        raise HTTPException(status_code=400, detail=portfolio_result["error"])
    
    return portfolio_result

@app.get("/api/portfolios")
async def get_portfolios(authorization: Optional[str] = None):
    """Get user portfolios"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    # Get user first to verify token
    user_result = await supabase_client.get_user(token)
    if not user_result["success"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get portfolios
    portfolios_result = await supabase_client.get_user_portfolios(user_result["user"]["id"])
    
    if not portfolios_result["success"]:
        raise HTTPException(status_code=400, detail=portfolios_result["error"])
    
    return portfolios_result

# 2FA/MFA Endpoints
@app.post("/api/auth/mfa/enroll")
async def enroll_mfa(authorization: Optional[str] = None):
    """Enroll a new MFA factor (TOTP)"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        result = await supabase_client.enroll_mfa(token)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/auth/mfa/verify")
async def verify_mfa(request: Dict[str, Any], authorization: Optional[str] = None):
    """Verify MFA challenge"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        result = await supabase_client.verify_mfa(
            token,
            request.get("factorId"),
            request.get("challengeId"),
            request.get("code")
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/auth/mfa/factors")
async def get_mfa_factors(authorization: Optional[str] = None):
    """Get user's MFA factors"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        result = await supabase_client.get_mfa_factors(token)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/auth/mfa/challenge")
async def create_mfa_challenge(request: Dict[str, Any], authorization: Optional[str] = None):
    """Create MFA challenge"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        result = await supabase_client.create_mfa_challenge(
            token,
            request.get("factorId")
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/auth/mfa/aal")
async def get_authenticator_assurance_level(authorization: Optional[str] = None):
    """Get authenticator assurance level"""
    if not supabase_client.is_available():
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        result = await supabase_client.get_authenticator_assurance_level(token)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

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

