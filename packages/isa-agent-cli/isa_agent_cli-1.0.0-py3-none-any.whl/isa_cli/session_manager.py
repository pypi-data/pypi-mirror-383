#!/usr/bin/env python3
"""
Session Management for isA Agent CLI
Integrates with Session Service for proper session lifecycle
"""

import requests
import uuid
from typing import Optional, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass

@dataclass
class SessionInfo:
    """Session information"""
    session_id: str
    user_id: str
    created_at: str
    last_activity: str
    status: str = "active"
    message_count: int = 0
    title: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class SessionManager:
    """Manages sessions via Session Service"""
    
    def __init__(self, api_base_url: str, user_id: str):
        self.api_base_url = api_base_url
        self.user_id = user_id
        self.current_session: Optional[SessionInfo] = None
    
    def create_session(self, title: Optional[str] = None) -> Optional[SessionInfo]:
        """Create new session via Session Service"""
        try:
            session_data = {
                "user_id": self.user_id,
                "title": title or f"CLI Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "metadata": {
                    "source": "cli",
                    "client": "isa_cli",
                    "version": "1.0.0"
                },
                "is_active": True
            }
            
            # Use session service port 8108 with correct endpoint
            session_service_url = self.api_base_url.replace(':8080', ':8108')
            response = requests.post(
                f"{session_service_url}/api/v1/sessions",
                json=session_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Session service may return data in different formats
                session_data_result = result.get("data", result)
                session = SessionInfo(
                    session_id=session_data_result.get("session_id") or session_data_result.get("id"),
                    user_id=self.user_id,
                    created_at=session_data_result.get("created_at", datetime.now().isoformat()),
                    last_activity=datetime.now().isoformat(),
                    status="active",
                    title=session_data["title"],
                    metadata=session_data["metadata"]
                )
                
                self.current_session = session
                return session
            else:
                print(f"Failed to create session: {response.status_code}")
                return self.create_local_session(title)
                
        except Exception as e:
            print(f"Error creating session: {e}")
            return self.create_local_session(title)
    
    def create_local_session(self, title: Optional[str] = None) -> SessionInfo:
        """Create local session as fallback"""
        session_id = f"cli_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        session = SessionInfo(
            session_id=session_id,
            user_id=self.user_id,
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            title=title or f"Local CLI Session",
            metadata={"mode": "local", "client": "isa_cli"}
        )
        
        self.current_session = session
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session by ID"""
        try:
            session_service_url = self.api_base_url.replace(':8080', ':8108')
            response = requests.get(
                f"{session_service_url}/api/v1/sessions/{session_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return SessionInfo(
                    session_id=data.get("session_id"),
                    user_id=data.get("user_id"),
                    created_at=data.get("created_at"),
                    last_activity=data.get("last_activity"),
                    status=data.get("status", "active"),
                    message_count=data.get("message_count", 0),
                    title=data.get("title"),
                    metadata=data.get("metadata", {})
                )
            
            return None
            
        except Exception as e:
            print(f"Error fetching session: {e}")
            return None
    
    def list_user_sessions(self, limit: int = 10) -> List[SessionInfo]:
        """List user sessions"""
        try:
            session_service_url = self.api_base_url.replace(':8080', ':8108')
            page = 1
            page_size = limit
            response = requests.get(
                f"{session_service_url}/api/v1/users/{self.user_id}/sessions",
                params={"page": page, "page_size": page_size},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                sessions = []
                
                for session_data in data.get("sessions", []):
                    session = SessionInfo(
                        session_id=session_data.get("session_id"),
                        user_id=session_data.get("user_id"),
                        created_at=session_data.get("created_at"),
                        last_activity=session_data.get("last_activity"),
                        status=session_data.get("status", "active"),
                        message_count=session_data.get("message_count", 0),
                        title=session_data.get("title"),
                        metadata=session_data.get("metadata", {})
                    )
                    sessions.append(session)
                
                return sessions
            
            return []
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def update_session_activity(self, session_id: Optional[str] = None):
        """Update session last activity"""
        if not session_id and self.current_session:
            session_id = self.current_session.session_id
        
        if not session_id:
            return
        
        try:
            update_data = {
                "last_activity": datetime.now().isoformat()
            }
            
            session_service_url = self.api_base_url.replace(':8080', ':8108')
            response = requests.put(
                f"{session_service_url}/api/v1/sessions/{session_id}",
                json=update_data,
                timeout=10
            )
            
            # Update local session info
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session.last_activity = update_data["last_activity"]
                
        except Exception as e:
            # Silent fail for activity updates
            pass
    
    def end_session(self, session_id: Optional[str] = None):
        """End/close session"""
        if not session_id and self.current_session:
            session_id = self.current_session.session_id
        
        if not session_id:
            return
        
        try:
            # Session service uses DELETE to end sessions
            session_service_url = self.api_base_url.replace(':8080', ':8108')
            response = requests.delete(
                f"{session_service_url}/api/v1/sessions/{session_id}",
                timeout=10
            )
            
            # Clear current session if it's the one being ended
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
                
        except Exception as e:
            print(f"Error ending session: {e}")
    
    def get_current_session(self) -> Optional[SessionInfo]:
        """Get current active session"""
        return self.current_session
    
    def set_current_session(self, session: SessionInfo):
        """Set current session"""
        self.current_session = session
        self.update_session_activity(session.session_id)
    
    def increment_message_count(self):
        """Increment message count for current session"""
        if self.current_session:
            self.current_session.message_count += 1