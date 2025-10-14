#!/usr/bin/env python3
"""
User Management for isA Agent CLI
Integrates with User Service, Account Service, and Session Service
"""

import os
import json
import requests
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class UserProfile:
    """User profile data"""
    user_id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    account_id: Optional[str] = None
    wallet_id: Optional[str] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}

class UserManager:
    """Manages user authentication and profile for CLI"""
    
    def __init__(self, api_base_url: str = "http://localhost:8080"):
        self.api_base_url = api_base_url
        self.profile_file = Path.home() / ".isa_agent_profile.json"
        self.current_user: Optional[UserProfile] = None
        
    def get_user_profile_file(self) -> Path:
        """Get user profile file path"""
        return self.profile_file
    
    def load_user_profile(self) -> Optional[UserProfile]:
        """Load user profile from file"""
        if not self.profile_file.exists():
            return None
            
        try:
            with open(self.profile_file, 'r') as f:
                data = json.load(f)
            
            profile = UserProfile(**data)
            self.current_user = profile
            return profile
            
        except Exception as e:
            print(f"Error loading user profile: {e}")
            return None
    
    def save_user_profile(self, profile: UserProfile):
        """Save user profile to file"""
        try:
            self.profile_file.parent.mkdir(exist_ok=True)
            
            with open(self.profile_file, 'w') as f:
                json.dump(asdict(profile), f, indent=2)
            
            self.current_user = profile
            
        except Exception as e:
            print(f"Error saving user profile: {e}")
    
    def create_or_get_user(self, username: str, email: Optional[str] = None) -> Optional[UserProfile]:
        """Create or get user from User Service"""
        try:
            # Try to get existing user first
            existing_user = self.get_user_by_username(username)
            if existing_user:
                return existing_user
            
            # Create new user via Account Service (correct endpoint)
            user_data = {
                "user_id": f"cli_{username}_{uuid.uuid4().hex[:8]}",
                "email": email or f"{username}@isa-cli.local",
                "name": username.replace("_", " ").title(),
                "is_active": True
            }
            
            # Use account service port 8201 with correct endpoint
            account_service_url = self.api_base_url.replace(':8080', ':8201')
            response = requests.post(
                f"{account_service_url}/api/v1/accounts/ensure",
                json=user_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                profile = UserProfile(
                    user_id=user_data["user_id"],
                    username=username,
                    email=email,
                    full_name=user_data["name"],
                    account_id=result.get("account_id"),
                    wallet_id=result.get("wallet_id"),
                    created_at=datetime.now().isoformat(),
                    last_login=datetime.now().isoformat()
                )
                
                self.save_user_profile(profile)
                return profile
            else:
                print(f"Failed to create user: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating user: {e}")
            # Fallback to local user
            return self.create_local_user(username, email)
    
    def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        """Get user by username - Account service doesn't have username search, so use local only"""
        # Account service only supports lookup by user_id, not username
        # For CLI, we'll rely on local profile storage
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Get user by ID from Account Service"""
        try:
            account_service_url = self.api_base_url.replace(':8080', ':8201')
            response = requests.get(
                f"{account_service_url}/api/v1/accounts/profile/{user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return UserProfile(
                    user_id=data.get("user_id"),
                    username=data.get("username", "unknown"),
                    email=data.get("email"),
                    full_name=data.get("name"),
                    account_id=data.get("account_id"),
                    wallet_id=data.get("wallet_id"),
                    created_at=data.get("created_at"),
                    last_login=data.get("last_login"),
                    preferences=data.get("preferences", {})
                )
            
            return None
            
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    def create_local_user(self, username: str, email: Optional[str] = None) -> UserProfile:
        """Create local user as fallback"""
        profile = UserProfile(
            user_id=f"local_{username}_{uuid.uuid4().hex[:8]}",
            username=username,
            email=email,
            full_name=username.replace("_", " ").title(),
            created_at=datetime.now().isoformat(),
            last_login=datetime.now().isoformat(),
            preferences={"mode": "local"}
        )
        
        self.save_user_profile(profile)
        return profile
    
    def get_or_create_user_interactive(self) -> UserProfile:
        """Interactive user creation/login"""
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        
        console = Console()
        
        # Check for existing profile
        existing_profile = self.load_user_profile()
        if existing_profile:
            use_existing = Confirm.ask(
                f"Found existing user: [bold cyan]{existing_profile.username}[/bold cyan]. Use this profile?",
                default=True
            )
            if use_existing:
                # Update last login
                existing_profile.last_login = datetime.now().isoformat()
                self.save_user_profile(existing_profile)
                return existing_profile
        
        # Get user info
        console.print("\n🆔 [bold cyan]User Setup[/bold cyan]")
        username = Prompt.ask("Enter username", default=os.getenv("USER", "user"))
        
        # Optional email
        want_email = Confirm.ask("Would you like to provide an email?", default=False)
        email = None
        if want_email:
            email = Prompt.ask("Enter email (optional)", default="")
            if not email.strip():
                email = None
        
        # Create user
        console.print("🔧 Setting up user profile...")
        profile = self.create_or_get_user(username, email)
        
        if profile:
            console.print(f"✅ [bold green]User profile created: {profile.username}[/bold green]")
            console.print(f"   User ID: [dim]{profile.user_id}[/dim]")
            if profile.account_id:
                console.print(f"   Account ID: [dim]{profile.account_id}[/dim]")
            if profile.wallet_id:
                console.print(f"   Wallet ID: [dim]{profile.wallet_id}[/dim]")
        else:
            console.print("❌ [bold red]Failed to create user profile[/bold red]")
            # Create local fallback
            profile = self.create_local_user(username, email)
            console.print(f"🔄 [yellow]Created local profile: {profile.username}[/yellow]")
        
        return profile
    
    def update_last_login(self):
        """Update last login timestamp"""
        if self.current_user:
            self.current_user.last_login = datetime.now().isoformat()
            self.save_user_profile(self.current_user)
    
    def get_current_user(self) -> Optional[UserProfile]:
        """Get current user profile"""
        if not self.current_user:
            self.current_user = self.load_user_profile()
        return self.current_user
    
    def clear_user_profile(self):
        """Clear user profile (logout)"""
        if self.profile_file.exists():
            self.profile_file.unlink()
        self.current_user = None