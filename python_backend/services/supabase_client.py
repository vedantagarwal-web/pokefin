"""
Supabase client service for authentication and database operations
"""
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client
from postgrest import APIError

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase client for authentication and database operations"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.anon_key:
            logger.error("Supabase credentials not found in environment variables")
            self.client = None
            return
            
        try:
            self.client: Client = create_client(self.url, self.anon_key)
            logger.info("✅ Supabase client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Supabase client is available"""
        return self.client is not None
    
    # Authentication methods
    async def sign_up(self, email: str, password: str, user_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Sign up a new user"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            
            if response.user:
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "created_at": response.user.created_at
                    },
                    "session": response.session
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create user"
                }
                
        except APIError as e:
            logger.error(f"Supabase sign up error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected sign up error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "created_at": response.user.created_at
                    },
                    "session": response.session
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to sign in"
                }
                
        except APIError as e:
            logger.error(f"Supabase sign in error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected sign in error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Sign out a user"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            self.client.auth.set_session(access_token, "")
            response = self.client.auth.sign_out()
            
            return {
                "success": True,
                "message": "Successfully signed out"
            }
                
        except APIError as e:
            logger.error(f"Supabase sign out error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected sign out error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """Get current user from access token"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            self.client.auth.set_session(access_token, "")
            user = self.client.auth.get_user()
            
            if user:
                return {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "created_at": user.created_at,
                        "user_metadata": user.user_metadata
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "User not found"
                }
                
        except APIError as e:
            logger.error(f"Supabase get user error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected get user error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Profile management
    async def create_profile(self, user_id: str, email: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a user profile"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.table("profiles").insert({
                "id": user_id,
                "email": email,
                "full_name": full_name or email.split("@")[0]
            }).execute()
            
            if response.data:
                return {
                    "success": True,
                    "profile": response.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create profile"
                }
                
        except APIError as e:
            logger.error(f"Supabase create profile error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected create profile error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).execute()
            
            if response.data:
                return {
                    "success": True,
                    "profile": response.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "Profile not found"
                }
                
        except APIError as e:
            logger.error(f"Supabase get profile error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected get profile error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.table("profiles").update(updates).eq("id", user_id).execute()
            
            if response.data:
                return {
                    "success": True,
                    "profile": response.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update profile"
                }
                
        except APIError as e:
            logger.error(f"Supabase update profile error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected update profile error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Portfolio management
    async def create_portfolio(self, user_id: str, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new portfolio"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.table("portfolios").insert({
                "user_id": user_id,
                "name": name,
                "description": description
            }).execute()
            
            if response.data:
                return {
                    "success": True,
                    "portfolio": response.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create portfolio"
                }
                
        except APIError as e:
            logger.error(f"Supabase create portfolio error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected create portfolio error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_portfolios(self, user_id: str) -> Dict[str, Any]:
        """Get all portfolios for a user"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.table("portfolios").select("*").eq("user_id", user_id).execute()
            
            return {
                "success": True,
                "portfolios": response.data or []
            }
                
        except APIError as e:
            logger.error(f"Supabase get portfolios error: {e}")
            return {
                "success": False,
                "error": str(e),
                "portfolios": []
            }
        except Exception as e:
            logger.error(f"Unexpected get portfolios error: {e}")
            return {
                "success": False,
                "error": str(e),
                "portfolios": []
            }
    
    # Brokerage connections
    async def create_brokerage_connection(self, user_id: str, brokerage_name: str, 
                                        connection_type: str, external_id: str, 
                                        connection_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a brokerage connection"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.table("brokerage_connections").insert({
                "user_id": user_id,
                "brokerage_name": brokerage_name,
                "connection_type": connection_type,
                "external_id": external_id,
                "connection_data": connection_data or {}
            }).execute()
            
            if response.data:
                return {
                    "success": True,
                    "connection": response.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create brokerage connection"
                }
                
        except APIError as e:
            logger.error(f"Supabase create brokerage connection error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected create brokerage connection error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_brokerage_connections(self, user_id: str) -> Dict[str, Any]:
        """Get all brokerage connections for a user"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.table("brokerage_connections").select("*").eq("user_id", user_id).execute()
            
            return {
                "success": True,
                "connections": response.data or []
            }
                
        except APIError as e:
            logger.error(f"Supabase get brokerage connections error: {e}")
            return {
                "success": False,
                "error": str(e),
                "connections": []
            }
        except Exception as e:
            logger.error(f"Unexpected get brokerage connections error: {e}")
            return {
                "success": False,
                "error": str(e),
                "connections": []
            }
    
    # AI Sessions
    async def create_ai_session(self, user_id: str, title: Optional[str] = None, 
                              session_type: str = "chat", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new AI session"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.table("ai_sessions").insert({
                "user_id": user_id,
                "title": title,
                "session_type": session_type,
                "metadata": metadata or {}
            }).execute()
            
            if response.data:
                return {
                    "success": True,
                    "session": response.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create AI session"
                }
                
        except APIError as e:
            logger.error(f"Supabase create AI session error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected create AI session error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_ai_message(self, session_id: str, role: str, content: str, 
                           tool_calls: Optional[Dict] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add a message to an AI session"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.table("ai_messages").insert({
                "session_id": session_id,
                "role": role,
                "content": content,
                "tool_calls": tool_calls,
                "metadata": metadata or {}
            }).execute()
            
            if response.data:
                return {
                    "success": True,
                    "message": response.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to add AI message"
                }
                
        except APIError as e:
            logger.error(f"Supabase add AI message error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected add AI message error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_ai_session_messages(self, session_id: str) -> Dict[str, Any]:
        """Get all messages for an AI session"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.table("ai_messages").select("*").eq("session_id", session_id).order("created_at").execute()
            
            return {
                "success": True,
                "messages": response.data or []
            }
                
        except APIError as e:
            logger.error(f"Supabase get AI messages error: {e}")
            return {
                "success": False,
                "error": str(e),
                "messages": []
            }
        except Exception as e:
            logger.error(f"Unexpected get AI messages error: {e}")
            return {
                "success": False,
                "error": str(e),
                "messages": []
            }

    # Google OAuth methods
    async def get_google_auth_url(self) -> str:
        """Generate Google OAuth URL"""
        if not self.client:
            return None
        
        try:
            response = self.client.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": "http://localhost:8788/api/auth/google/callback"
                }
            })
            return response.url if hasattr(response, 'url') else None
        except Exception as e:
            logger.error(f"Error generating Google auth URL: {e}")
            return None

    async def exchange_oauth_code(self, code: str) -> Dict[str, Any]:
        """Exchange OAuth code for session"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            response = self.client.auth.exchange_code_for_session(code)
            
            if response.user:
                return {
                    "success": True,
                    "user": response.user.model_dump(),
                    "session": response.session
                }
            else:
                return {"success": False, "error": "Failed to exchange code for session"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 2FA/MFA methods
    async def enroll_mfa(self, token: str) -> Dict[str, Any]:
        """Enroll a new MFA factor"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            # Set the session for this request
            self.client.auth.set_session(access_token=token, refresh_token="")
            
            # Enroll TOTP factor
            response = await self.client.auth.mfa.enroll({"factor_type": "totp"})
            
            if response.data:
                return {
                    "success": True,
                    "factor_id": response.data.id,
                    "qr_code": response.data.totp.qr_code,
                    "secret": response.data.totp.secret
                }
            else:
                return {"success": False, "error": "Failed to enroll MFA factor"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_mfa_challenge(self, token: str, factor_id: str) -> Dict[str, Any]:
        """Create MFA challenge"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            # Set the session for this request
            self.client.auth.set_session(access_token=token, refresh_token="")
            
            # Create challenge
            response = await self.client.auth.mfa.challenge({"factor_id": factor_id})
            
            if response.data:
                return {
                    "success": True,
                    "challenge_id": response.data.id
                }
            else:
                return {"success": False, "error": "Failed to create challenge"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def verify_mfa(self, token: str, factor_id: str, challenge_id: str, code: str) -> Dict[str, Any]:
        """Verify MFA challenge"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            # Set the session for this request
            self.client.auth.set_session(access_token=token, refresh_token="")
            
            # Verify the MFA code
            response = await self.client.auth.mfa.verify({
                "factor_id": factor_id,
                "challenge_id": challenge_id,
                "code": code
            })
            
            if response.data:
                return {
                    "success": True,
                    "session": response.data
                }
            else:
                return {"success": False, "error": "Invalid MFA code"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_mfa_factors(self, token: str) -> Dict[str, Any]:
        """Get user's MFA factors"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            # Set the session for this request
            self.client.auth.set_session(access_token=token, refresh_token="")
            
            # Get MFA factors
            response = await self.client.auth.mfa.list_factors()
            
            if response.data:
                return {
                    "success": True,
                    "factors": {
                        "totp": [{"id": f.id, "status": f.status, "created_at": f.created_at} for f in response.data.totp],
                        "phone": [{"id": f.id, "status": f.status, "created_at": f.created_at} for f in response.data.phone]
                    }
                }
            else:
                return {"success": False, "error": "Failed to get MFA factors"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_authenticator_assurance_level(self, token: str) -> Dict[str, Any]:
        """Get authenticator assurance level"""
        if not self.client:
            return {"success": False, "error": "Supabase client not initialized"}
        
        try:
            # Set the session for this request
            # Set the session for this request
            self.client.auth.set_session(access_token=token, refresh_token="")
            
            # Get AAL
            response = await self.client.auth.mfa.get_authenticator_assurance_level()
            
            if response.data:
                return {
                    "success": True,
                    "current_level": response.data.current_level,
                    "next_level": response.data.next_level
                }
            else:
                return {"success": False, "error": "Failed to get AAL"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance
supabase_client = SupabaseClient()
