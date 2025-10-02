"""
Session Manager - Manages user sessions in memory
"""

from typing import Dict, Any
from datetime import datetime

class SessionManager:
    """Manages chat sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get or create session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "user_context": {}
            }
        
        return self.sessions[session_id]
    
    async def update_session(self, session_id: str, data: Dict[str, Any]):
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id].update(data)
        else:
            self.sessions[session_id] = data
    
    async def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]

