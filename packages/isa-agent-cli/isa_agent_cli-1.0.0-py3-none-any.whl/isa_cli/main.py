#!/usr/bin/env python3
"""
isA Agent CLI - Interactive Command Line Interface for Agent Chat

Features:
- Interactive chat with real-time streaming
- Session management with persistence
- Rich console output with colors and formatting
- Event type filtering and display options
- Support for both streaming and sync modes
- Configuration management
- HIL (Human-in-Loop) interaction support

Usage:
  python cli.py                    # Interactive mode
  python cli.py "Hello, agent!"   # Single message mode
  python cli.py --sync "message"  # Sync mode
  python cli.py --config          # Show configuration
  python cli.py --sessions        # List sessions
"""

import asyncio
import json
import os
import uuid
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm

from .event_handler import EventStreamHandler
from .user_manager import UserManager, UserProfile
from .session_manager import SessionManager, SessionInfo
from .chat_client import ChatClient
from .response_processor import ResponseProcessor


@dataclass
class CLIConfig:
    """CLI configuration settings"""
    api_base_url: str = field(default_factory=lambda: os.getenv("CLI_API_BASE_URL", "http://localhost:8080"))
    api_key: str = "authenticated"  # Will be set by auth flow
    user_id: Optional[str] = None  # Will be set by user manager
    default_session_id: Optional[str] = None  # Will be set by session manager
    timeout: int = 60
    show_events: List[str] = field(default_factory=lambda: [])  # Empty = show all events
    hide_events: List[str] = field(default_factory=lambda: [
        # Default: Only hide very technical events
        "node.enter"  # Node entry events (too technical)
    ])
    show_timestamps: bool = False
    show_metadata: bool = False
    show_debug: bool = False
    simple_mode: bool = False  # False = verbose mode (show all events)
    # simple_mode: True = Claude Code style (hide technical details)
    color_scheme: Dict[str, str] = field(default_factory=lambda: {
        "user": "bold blue",
        "agent": "green",
        "thinking": "dim cyan", 
        "system": "yellow",
        "error": "bold red",
        "success": "bold green",
        "info": "cyan",
        "progress": "magenta"
    })

    def save(self, config_path: str = "~/.isa_agent_cli.json"):
        """Save configuration to file"""
        config_file = Path(config_path).expanduser()
        config_file.parent.mkdir(exist_ok=True)
        
        # Convert to dict and make serializable
        config_dict = {
            "api_base_url": self.api_base_url,
            "api_key": self.api_key,
            "user_id": self.user_id,
            "timeout": self.timeout,
            "show_events": self.show_events,
            "hide_events": self.hide_events,
            "show_timestamps": self.show_timestamps,
            "show_metadata": self.show_metadata,
            "show_debug": self.show_debug,
            "color_scheme": self.color_scheme
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)

    @classmethod
    def load(cls, config_path: str = "~/.isa_agent_cli.json") -> 'CLIConfig':
        """Load configuration from file"""
        config_file = Path(config_path).expanduser()
        
        if not config_file.exists():
            config = cls()
            config.save(config_path)
            return config
        
        try:
            with open(config_file, 'r') as f:
                config_dict = json.load(f)
            
            config = cls()
            for key, value in config_dict.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return cls()


class AgentChatCLI:
    """Interactive CLI for Agent Chat"""
    
    def __init__(self, config: CLIConfig):
        self.config = config
        self.console = Console()
        self.chat_history = []
        self.pending_hil_requests = {}
        
        # Initialize managers
        self.user_manager = UserManager(config.api_base_url)
        self.session_manager: Optional[SessionManager] = None
        self.current_user: Optional[UserProfile] = None
        self.current_session: Optional[SessionInfo] = None
        
        # Setup user and session
        self._setup_user_and_session()
        
        # Setup event stream handler
        self.event_handler = EventStreamHandler(
            self.console, 
            self.config, 
            session_id_getter=lambda: self.current_session.session_id if self.current_session else "unknown"
        )
        
        # Setup response processor
        self.response_processor = ResponseProcessor(self.console, self.config)
        
        # Setup chat client
        self.chat_client = ChatClient(
            api_base_url=self.config.api_base_url,
            api_key=self.config.api_key,
            timeout=self.config.timeout
        )
        
        # Setup HTTP client (kept for compatibility)
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),  # Shorter timeout for quick operations
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            follow_redirects=True
        )
    
    def _setup_user_and_session(self):
        """Setup user profile and session management"""
        try:
            # Check if user_id is already provided via command line
            if self.config.user_id:
                # Use the provided user_id, try to load existing profile first
                existing_profile = self.user_manager.load_user_profile()
                if existing_profile and existing_profile.user_id == self.config.user_id:
                    self.current_user = existing_profile
                else:
                    # Create user profile with provided user_id
                    username = self.config.user_id.split('_')[-1] if '_' in self.config.user_id else self.config.user_id
                    self.current_user = self.user_manager.create_local_user(username)
                    self.current_user.user_id = self.config.user_id  # Override with command line user_id
                    self.user_manager.save_user_profile(self.current_user)
            else:
                # Interactive user setup
                self.current_user = self.user_manager.get_or_create_user_interactive()
            
            if self.current_user:
                # Update config with user info
                self.config.user_id = self.current_user.user_id
                
                # Initialize session manager
                self.session_manager = SessionManager(
                    self.config.api_base_url,
                    self.current_user.user_id
                )
                
                # Create new session or use specified session
                if self.config.default_session_id:
                    # Try to get existing session
                    session = self.session_manager.get_session(self.config.default_session_id)
                    if session:
                        self.current_session = session
                        self.session_manager.set_current_session(session)
                    else:
                        self.console.print(f"⚠️ [yellow]Session {self.config.default_session_id} not found, creating new session[/yellow]")
                        self.current_session = self.session_manager.create_session()
                else:
                    # Create new session
                    self.current_session = self.session_manager.create_session()
                
                if self.current_session:
                    self.config.default_session_id = self.current_session.session_id
                    
        except Exception as e:
            self.console.print(f"❌ [bold red]Error setting up user/session: {e}[/bold red]")
            # Fallback to local mode
            self.config.user_id = f"cli_user_{uuid.uuid4().hex[:8]}"
            self.config.default_session_id = f"cli_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def print_banner(self):
        """Print CLI banner - Claude Code style"""
        # Simple, clean banner
        self.console.print()
        self.console.print("🤖 [bold cyan]isA Agent[/bold cyan] [dim]- AI Assistant[/dim]")
        
        # Show user and session info
        if self.current_user:
            user_info = f"👤 {self.current_user.username}"
            if self.current_session:
                session_info = f"📝 {self.current_session.title} ({self.current_session.message_count} msgs)"
                self.console.print(f"[dim]{user_info} | {session_info}[/dim]")
            else:
                self.console.print(f"[dim]{user_info}[/dim]")
        
        self.console.print("[dim]Type your message or 'help' for commands[/dim]")
        self.console.print()
    
    def should_show_event(self, event_type: str) -> bool:
        """Check if event type should be displayed"""
        if event_type in self.config.hide_events:
            return False
        if self.config.show_events and event_type not in self.config.show_events:
            return False
        return True
    
    def format_event(self, event: Dict[str, Any]) -> Optional[Text]:
        """Format event for display"""
        event_type = event.get('type', 'unknown')
        content = event.get('content', '')
        timestamp = event.get('timestamp', '')
        metadata = event.get('metadata', {})
        
        if not self.should_show_event(event_type):
            return None
        
        # Color coding based on event type
        if event_type.startswith('content.thinking'):
            style = self.config.color_scheme['thinking']
            prefix = "💭"
        elif event_type.startswith('content.token'):
            style = self.config.color_scheme['agent'] 
            prefix = ""  # No prefix for tokens, they combine to form the response
        elif event_type.startswith('tool_calls'):
            style = self.config.color_scheme['progress']
            prefix = "🔧"
        elif event_type.startswith('progress'):
            style = self.config.color_scheme['progress']
            prefix = "⚙️"
        elif event_type.startswith('session.'):
            style = self.config.color_scheme['system']
            prefix = "📡"
        elif event_type.startswith('context.'):
            style = self.config.color_scheme['info']
            prefix = "🔧"
        elif event_type.startswith('memory.'):
            style = self.config.color_scheme['info']
            prefix = "🧠"
        else:
            style = "white"
            prefix = "ℹ️"
        
        # Build display text
        text = Text()
        
        if self.config.show_timestamps and timestamp:
            text.append(f"[{timestamp}] ", style="dim")
        
        if prefix and not event_type.startswith('content.token'):
            text.append(f"{prefix} ", style=style)
        
        if event_type.startswith('content.token'):
            # For token events, just show the content without formatting
            text.append(content, style=style)
        else:
            text.append(content, style=style)
        
        if self.config.show_metadata and metadata:
            text.append(f" {metadata}", style="dim")
        
        return text
    
    async def send_message(self, message: str, output_format: str = "stream") -> Dict[str, Any]:
        """Send message to agent"""
        # Update session activity
        if self.session_manager and self.current_session:
            self.session_manager.update_session_activity()
            self.session_manager.increment_message_count()
        
        session_id = self.current_session.session_id if self.current_session else self.config.default_session_id
        
        if output_format == "json":
            # Synchronous mode - handle SSE events then extract final JSON
            async for result in self.chat_client.send_message(
                message=message,
                user_id=self.config.user_id,
                session_id=session_id,
                output_format=output_format
            ):
                return result  # Return the single result from sync mode
        else:
            # Streaming mode - process events in real-time
            result = {"response": "", "events": [], "success": False}
            events_received = []
            
            async for event in self.chat_client.send_message(
                message=message,
                user_id=self.config.user_id,
                session_id=session_id,
                output_format=output_format
            ):
                events_received.append(event)
                
                # Use event handler to process the event
                should_continue = self.event_handler.process_event(event)
                if not should_continue:
                    # Check if we're waiting for HIL authorization
                    if self.event_handler.hil_authorization_sent:
                        self.console.print("⏳ [dim]Still waiting for HIL processing, continuing stream...[/dim]")
                        continue  # Don't end stream, keep waiting
                    
                    # Stream ended by event handler
                    break
            
            # Get final response from event handler
            final_response = self.event_handler.get_response_text()
            result = {
                "response": final_response or "",
                "events": events_received,
                "success": len(events_received) > 0
            }
            
            return result
    
    async def send_message_with_files(self, message: str, file_paths: List[str], output_format: str = "stream") -> Dict[str, Any]:
        """Send message with file uploads to agent"""
        # Update session activity
        if self.session_manager and self.current_session:
            self.session_manager.update_session_activity()
            self.session_manager.increment_message_count()
        
        # Show file upload status
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists() and path.is_file():
                self.console.print(f"📎 [cyan]Uploading file: {path.name}[/cyan]")
        
        session_id = self.current_session.session_id if self.current_session else self.config.default_session_id
        
        if output_format == "json":
            # Synchronous mode - handle SSE events then extract final JSON
            async for result in self.chat_client.send_message_with_files(
                message=message,
                file_paths=file_paths,
                user_id=self.config.user_id,
                session_id=session_id,
                output_format=output_format
            ):
                # Show file upload success notification
                if result.get("success"):
                    for file_path in file_paths:
                        path = Path(file_path)
                        if path.exists():
                            self.console.print(f"✅ [bold green]Uploaded: {path.name}[/bold green]")
                
                return result  # Return the single result from sync mode
        else:
            # Streaming mode - process events in real-time
            result = {"response": "", "events": [], "success": False}
            events_received = []
            
            async for event in self.chat_client.send_message_with_files(
                message=message,
                file_paths=file_paths,
                user_id=self.config.user_id,
                session_id=session_id,
                output_format=output_format
            ):
                events_received.append(event)
                
                # Use event handler to process the event
                should_continue = self.event_handler.process_event(event)
                if not should_continue:
                    # Check if we're waiting for HIL authorization
                    if self.event_handler.hil_authorization_sent:
                        self.console.print("⏳ [dim]Still waiting for HIL processing, continuing stream...[/dim]")
                        continue  # Don't end stream, keep waiting
                    
                    # Stream ended by event handler
                    break
            
            # Show file upload success notification
            for file_path in file_paths:
                path = Path(file_path)
                if path.exists():
                    self.console.print(f"✅ [bold green]Uploaded: {path.name}[/bold green]")
            
            # Get final response from event handler
            final_response = self.event_handler.get_response_text()
            result = {
                "response": final_response or "",
                "events": events_received,
                "success": len(events_received) > 0
            }
            
            return result
    
    async def test_rag_functionality(self):
        """Test RAG functionality with example queries"""
        self.console.print("\n🧪 [bold cyan]Testing RAG Functionality[/bold cyan]")
        
        test_queries = [
            "What files do I have uploaded?",
            "Can you summarize the content of my files?",
            "Search for information about the main topic in my documents"
        ]
        
        for i, query in enumerate(test_queries, 1):
            self.console.print(f"\n[bold yellow]Test {i}:[/bold yellow] {query}")
            try:
                # Reset event handler buffers before new message
                self.event_handler.reset_buffers()
                result = await self.send_message(query)
                if not result.get('success'):
                    self.console.print("❌ [bold red]Test failed[/bold red]")
            except Exception as e:
                self.console.print(f"❌ [bold red]Test error: {e}[/bold red]")
        
        self.console.print("\n✅ [bold green]RAG testing completed[/bold green]")
    
    def handle_hil_resume(self, resume_payload: Dict[str, Any]):
        """Handle HIL resume request and start new streaming connection"""
        try:
            self.console.print("🔄 [cyan]Resuming execution with streaming...[/cyan]")
            
            # Start resume streaming synchronously
            self._resume_streaming_execution(resume_payload)
            
        except Exception as e:
            self.console.print(f"[red]❌ Error starting resume stream: {e}[/red]")
    
    def _resume_streaming_execution(self, resume_payload: Dict[str, Any]):
        """Resume execution with streaming response"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
            
            # Use execution resume-stream endpoint
            response = requests.post(
                f"{self.config.api_base_url}/api/v1/agents/execution/resume-stream",
                json=resume_payload,
                headers=headers,
                stream=True,
                timeout=(30, None)
            )
            
            response.raise_for_status()
            
            if 'text/event-stream' not in response.headers.get('content-type', ''):
                self.console.print("[yellow]⚠️ Resume response is not streaming[/yellow]")
                return
            
            # Reset event handler buffers for new stream
            self.event_handler.reset_buffers()
            
            # Process the resume stream
            buffer = ""
            # Use small chunk_size for real-time token streaming  
            for chunk in response.iter_content(chunk_size=64, decode_unicode=True):
                if not chunk:
                    continue
                    
                buffer += chunk
                
                # Process complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if not line or line.startswith(':'):
                        continue
                        
                    if line.startswith('data: '):
                        data_str = line[6:]
                        
                        if data_str.strip() == '[DONE]':
                            self.console.print("✅ [green]Resume execution completed[/green]")
                            return
                        
                        try:
                            event = json.loads(data_str)
                            should_continue = self.event_handler.process_event(event)
                            if not should_continue:
                                return
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            self.console.print(f"[red]❌ Resume streaming error: {e}[/red]")
    
    
    
    
    def send_hil_resume(self, approve: bool):
        """Send HIL resume request to continue execution"""
        import requests
        
        resume_payload = {
            "session_id": self.current_session_id,
            "user_id": self.config.user_id,
            "decision": "approve" if approve else "reject",
            "message": f"User {'approved' if approve else 'rejected'} tool execution from CLI"
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.config.api_base_url}/api/v1/agents/chat/resume",
                json=resume_payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                if approve:
                    self.console.print("✅ [green]Authorization sent - execution will continue[/green]")
                else:
                    self.console.print("❌ [red]Authorization rejected - execution stopped[/red]")
            else:
                self.console.print(f"[red]❌ Failed to send authorization: {response.status_code}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error sending authorization: {e}[/red]")
    
    async def handle_hil_request(self, event: Dict[str, Any]):
        """Handle Human-in-Loop request"""
        metadata = event.get('metadata', {})
        interrupt_data = metadata.get('interrupt_data', {})
        
        if interrupt_data.get('type') == 'batch_tool_authorization':
            message = interrupt_data.get('message', 'Authorization required')
            
            # Display authorization request
            self.console.print()
            self.console.print(Panel(
                message,
                title="🔐 Authorization Required",
                title_align="left",
                border_style="yellow"
            ))
            
            # Get user decision
            approve = Confirm.ask("Do you approve the execution of these tools?")
            
            # Send resume request
            resume_payload = {
                "session_id": self.current_session_id,
                "user_id": self.config.user_id,
                "decision": "approve" if approve else "reject",
                "message": "User decision from CLI"
            }
            
            try:
                resume_response = await self.client.post(
                    f"{self.config.api_base_url}/api/v1/agents/chat/resume",
                    json=resume_payload
                )
                resume_response.raise_for_status()
                
                if approve:
                    self.console.print("✅ [bold green]Tools approved - resuming execution...[/bold green]")
                else:
                    self.console.print("❌ [bold red]Tools rejected - execution stopped[/bold red]")
                
                # Continue streaming the resumed session
                await self.handle_streaming_response({
                    "message": "",  # Empty message for resume
                    "user_id": self.config.user_id,
                    "session_id": self.current_session_id
                })
                
            except httpx.HTTPError as e:
                self.console.print(f"❌ [bold red]Error resuming session: {e}[/bold red]")
    
    async def list_sessions(self):
        """List available sessions"""
        if not self.session_manager:
            self.console.print("❌ [bold red]Session manager not initialized[/bold red]")
            return
        
        try:
            sessions = self.session_manager.list_user_sessions(limit=20)
            
            if not sessions:
                self.console.print("📭 No sessions found")
                return
            
            table = Table(title="📋 Chat Sessions")
            table.add_column("Session ID", style="cyan", width=30)
            table.add_column("Title", style="white", width=25)
            table.add_column("Created", style="green", width=20)
            table.add_column("Status", style="yellow", width=10)
            table.add_column("Messages", style="magenta", justify="right", width=8)
            
            for session in sessions:
                # Format created date
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(session.created_at.replace('Z', '+00:00'))
                    created_str = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    created_str = session.created_at[:16] if session.created_at else "Unknown"
                
                # Truncate session ID for display
                session_display = session.session_id
                if len(session_display) > 28:
                    session_display = session_display[:25] + "..."
                
                # Truncate title
                title = session.title or "Untitled"
                if len(title) > 23:
                    title = title[:20] + "..."
                
                # Current session indicator
                if self.current_session and session.session_id == self.current_session.session_id:
                    session_display = f"→ {session_display}"
                    title = f"[bold]{title}[/bold]"
                
                table.add_row(
                    session_display,
                    title,
                    created_str,
                    session.status,
                    str(session.message_count)
                )
            
            self.console.print(table)
            
            # Show current session info
            if self.current_session:
                self.console.print(f"\n[dim]Current session: {self.current_session.session_id}[/dim]")
            
        except Exception as e:
            self.console.print(f"❌ [bold red]Error fetching sessions: {e}[/bold red]")
    
    async def check_health(self):
        """Check API health"""
        try:
            self.console.print(f"🔍 Checking health at: {self.config.api_base_url}/health")
            
            # Use requests for simple synchronous health check
            response = requests.get(
                f"{self.config.api_base_url}/health",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            response.raise_for_status()
            health = response.json()
            
            status = health.get('status', 'unknown')
            components = health.get('components', {})
            
            if status == 'healthy':
                self.console.print("✅ [bold green]API is healthy[/bold green]")
            else:
                self.console.print(f"⚠️  [bold yellow]API status: {status}[/bold yellow]")
            
            # Show component status
            if components:
                table = Table(title="🏥 Component Health")
                table.add_column("Component", style="cyan")
                table.add_column("Status", style="green")
                
                for component, component_status in components.items():
                    table.add_row(component, str(component_status))
                
                self.console.print(table)
            
        except requests.exceptions.ConnectionError as e:
            self.console.print(f"❌ [bold red]Connection failed: {e}[/bold red]")
            self.console.print(f"💡 Make sure the API server is running at {self.config.api_base_url}")
        except requests.exceptions.Timeout as e:
            self.console.print(f"❌ [bold red]Request timed out: {e}[/bold red]")
        except requests.exceptions.HTTPError as e:
            self.console.print(f"❌ [bold red]HTTP error {e.response.status_code}: {e.response.text}[/bold red]")
        except Exception as e:
            self.console.print(f"❌ [bold red]Unexpected error: {e}[/bold red]")
    
    def print_help(self):
        """Print help information"""
        help_text = """
[bold cyan]Available Commands:[/bold cyan]

[bold]Chat Commands:[/bold]
• Just type your message and press Enter to chat
• End line with [cyan]\\[/cyan] for multi-line input
• [cyan]upload <files> <message>[/cyan] - Upload files with message
• [cyan]test-rag[/cyan] - Test RAG functionality
• [cyan]quit[/cyan], [cyan]exit[/cyan], [cyan]/exit[/cyan] - Exit the CLI
• [cyan]clear[/cyan] - Clear the screen

[bold]User Management:[/bold]
• [cyan]user[/cyan] - Show current user profile
• [cyan]logout[/cyan] - Logout and clear profile

[bold]Session Management:[/bold]
• [cyan]new[/cyan] - Start a new session
• [cyan]sessions[/cyan] - List all chat sessions
• [cyan]session <session_id>[/cyan] - Switch to a session
• [cyan]session[/cyan] - Show current session info
• [cyan]history[/cyan] - Show conversation history

[bold]Information Commands:[/bold]  
• [cyan]help[/cyan] - Show this help
• [cyan]health[/cyan] - Check API health status
• [cyan]config[/cyan] - Show current configuration

[bold]Settings Commands:[/bold]
• [cyan]events show <types>[/cyan] - Set visible event types
• [cyan]events hide <types>[/cyan] - Set hidden event types  
• [cyan]timestamps on/off[/cyan] - Toggle timestamp display
• [cyan]metadata on/off[/cyan] - Toggle metadata display

[bold cyan]Examples:[/bold cyan]
• [dim]Hello, what can you help me with?[/dim]
• [dim]upload doc.pdf,image.jpg Tell me about these files[/dim]
• [dim]sessions[/dim] 
• [dim]session my_session_id[/dim]
• [dim]new[/dim] - Start new session
• [dim]user[/dim] - Show user profile
"""
        self.console.print(help_text)
    
    def print_config(self):
        """Print current configuration"""
        table = Table(title="⚙️  CLI Configuration")
        table.add_column("Setting", style="cyan", width=20)
        table.add_column("Value", style="green", width=40)
        
        table.add_row("API Base URL", self.config.api_base_url)
        
        # User information
        if self.current_user:
            table.add_row("User", f"{self.current_user.username} ({self.current_user.user_id})")
            if self.current_user.email:
                table.add_row("Email", self.current_user.email)
            if self.current_user.account_id:
                table.add_row("Account ID", self.current_user.account_id)
        else:
            table.add_row("User ID", self.config.user_id or "Not set")
        
        # Session information
        if self.current_session:
            table.add_row("Current Session", self.current_session.session_id)
            table.add_row("Session Title", self.current_session.title or "Untitled")
            table.add_row("Session Status", self.current_session.status)
            table.add_row("Message Count", str(self.current_session.message_count))
        else:
            table.add_row("Current Session", self.config.default_session_id or "Not set")
        
        table.add_row("Timeout", f"{self.config.timeout}s")
        table.add_row("Show Timestamps", str(self.config.show_timestamps))
        table.add_row("Show Metadata", str(self.config.show_metadata))
        
        # Event settings (truncated for display)
        visible_events = ", ".join(self.config.show_events[:3])
        if len(self.config.show_events) > 3:
            visible_events += f"... ({len(self.config.show_events)} total)"
        table.add_row("Visible Events", visible_events or "All events")
        
        hidden_events = ", ".join(self.config.hide_events[:3])
        if len(self.config.hide_events) > 3:
            hidden_events += f"... ({len(self.config.hide_events)} total)"
        table.add_row("Hidden Events", hidden_events or "None")
        
        self.console.print(table)
    
    async def process_command(self, input_text: str) -> bool:
        """Process user command. Returns False if should exit."""
        cmd = input_text.strip().lower()
        
        if cmd in ['quit', 'exit', '/exit', '/quit']:
            return False
        elif cmd == 'clear':
            self.console.clear()
        elif cmd == 'help':
            self.print_help()
        elif cmd == 'config':
            self.print_config()
        elif cmd == 'sessions':
            await self.list_sessions()
        elif cmd == 'health':
            await self.check_health()
        elif cmd == 'new':
            if self.session_manager:
                # End current session
                if self.current_session:
                    self.session_manager.end_session(self.current_session.session_id)
                
                # Create new session
                self.current_session = self.session_manager.create_session()
                if self.current_session:
                    self.config.default_session_id = self.current_session.session_id
                    self.event_handler.reset_buffers()  # Reset event handler buffers for new session
                    self.console.print(f"✨ [bold green]Started new session: {self.current_session.title}[/bold green]")
                    self.console.print(f"   Session ID: [dim]{self.current_session.session_id}[/dim]")
                else:
                    self.console.print("❌ [bold red]Failed to create new session[/bold red]")
            else:
                # Fallback to old behavior
                self.config.default_session_id = f"cli_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.event_handler.reset_buffers()
                self.console.print(f"✨ [bold green]Started new session: {self.config.default_session_id}[/bold green]")
        
        elif cmd.startswith('session '):
            session_id = cmd[8:].strip()
            if session_id and self.session_manager:
                # Try to get the session
                session = self.session_manager.get_session(session_id)
                if session:
                    # End current session
                    if self.current_session:
                        self.session_manager.end_session(self.current_session.session_id)
                    
                    # Switch to new session
                    self.current_session = session
                    self.session_manager.set_current_session(session)
                    self.config.default_session_id = session.session_id
                    self.event_handler.reset_buffers()  # Reset event handler buffers for session switch
                    self.console.print(f"🔄 [bold green]Switched to session: {session.title}[/bold green]")
                    self.console.print(f"   Session ID: [dim]{session.session_id}[/dim]")
                    self.console.print(f"   Messages: {session.message_count}")
                else:
                    self.console.print(f"❌ [bold red]Session not found: {session_id}[/bold red]")
            elif session_id:
                # Fallback without session manager
                self.config.default_session_id = session_id
                self.event_handler.reset_buffers()
                self.console.print(f"🔄 [bold green]Switched to session: {session_id}[/bold green]")
            else:
                if self.current_session:
                    self.console.print(f"📝 Current session: {self.current_session.title}")
                    self.console.print(f"   Session ID: [dim]{self.current_session.session_id}[/dim]")
                    self.console.print(f"   Messages: {self.current_session.message_count}")
                else:
                    self.console.print(f"📝 Current session: {self.config.default_session_id}")
        
        elif cmd == 'session':
            if self.current_session:
                self.console.print(f"📝 Current session: {self.current_session.title}")
                self.console.print(f"   Session ID: [dim]{self.current_session.session_id}[/dim]")
                self.console.print(f"   Messages: {self.current_session.message_count}")
                self.console.print(f"   Status: {self.current_session.status}")
            else:
                self.console.print(f"📝 Current session: {self.config.default_session_id}")
        elif cmd == 'history':
            self.show_conversation_history()
        elif cmd.startswith('events show '):
            events = cmd[12:].split(',')
            self.config.show_events = [e.strip() for e in events if e.strip()]
            self.console.print(f"👁️  [bold green]Now showing events: {', '.join(self.config.show_events)}[/bold green]")
        elif cmd.startswith('events hide '):
            events = cmd[12:].split(',')
            self.config.hide_events = [e.strip() for e in events if e.strip()]
            self.console.print(f"🙈 [bold green]Now hiding events: {', '.join(self.config.hide_events)}[/bold green]")
        elif cmd.startswith('upload '):
            # Handle file upload command
            parts = cmd[7:].split(' ', 1)
            if len(parts) >= 2:
                file_paths = parts[0].split(',')
                message = parts[1]
                try:
                    self.console.print(f"\n[bold blue]You:[/bold blue] {message}")
                    self.console.print(f"📎 [cyan]Files: {', '.join(file_paths)}[/cyan]")
                    # Reset event handler buffers before new message
                    self.event_handler.reset_buffers()
                    result = await self.send_message_with_files(message, file_paths)
                    if result.get('success'):
                        response_text = result.get('response', '')
                        self.chat_history.append({
                            "user": f"{message} (with files: {', '.join(file_paths)})",
                            "agent": response_text,
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        self.console.print("❌ [bold red]Failed to upload files or get response[/bold red]")
                except Exception as e:
                    self.console.print(f"❌ [bold red]Upload error: {e}[/bold red]")
            else:
                self.console.print("❌ [bold red]Usage: upload <file1,file2,...> <message>[/bold red]")
        elif cmd == 'test-rag':
            await self.test_rag_functionality()
        elif cmd in ['timestamps on', 'timestamps true']:
            self.config.show_timestamps = True
            self.console.print("⏰ [bold green]Timestamps enabled[/bold green]")
        elif cmd in ['timestamps off', 'timestamps false']:
            self.config.show_timestamps = False
            self.console.print("⏰ [bold green]Timestamps disabled[/bold green]")
        elif cmd in ['metadata on', 'metadata true']:
            self.config.show_metadata = True
            self.console.print("📊 [bold green]Metadata display enabled[/bold green]")
        elif cmd in ['metadata off', 'metadata false']:
            self.config.show_metadata = False
            self.console.print("📊 [bold green]Metadata display disabled[/bold green]")
        elif cmd == 'user':
            # Show current user info
            if self.current_user:
                self.console.print(f"👤 [bold cyan]Current User[/bold cyan]")
                self.console.print(f"   Username: {self.current_user.username}")
                self.console.print(f"   User ID: [dim]{self.current_user.user_id}[/dim]")
                if self.current_user.email:
                    self.console.print(f"   Email: {self.current_user.email}")
                if self.current_user.account_id:
                    self.console.print(f"   Account ID: [dim]{self.current_user.account_id}[/dim]")
                if self.current_user.last_login:
                    self.console.print(f"   Last Login: {self.current_user.last_login}")
            else:
                self.console.print("❌ [bold red]No user profile loaded[/bold red]")
        elif cmd == 'logout':
            # Logout current user
            if Confirm.ask("Are you sure you want to logout and clear your profile?"):
                if self.current_session and self.session_manager:
                    self.session_manager.end_session(self.current_session.session_id)
                self.user_manager.clear_user_profile()
                self.console.print("👋 [bold green]Logged out successfully[/bold green]")
                return False  # Exit CLI
        else:
            # Not a command, treat as chat message
            if input_text.strip():
                try:
                    self.console.print(f"\n[bold blue]You:[/bold blue] {input_text}")
                    # Reset event handler buffers before new message
                    self.event_handler.reset_buffers()
                    result = await self.send_message(input_text)
                    if result.get('success'):
                        response_text = result.get('response', '')
                        self.chat_history.append({
                            "user": input_text,
                            "agent": response_text,
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        self.console.print("❌ [bold red]Failed to get response[/bold red]")
                except Exception as e:
                    self.console.print(f"❌ [bold red]Error: {e}[/bold red]")
        
        return True
    
    def show_conversation_history(self):
        """Show conversation history for current session"""
        if not self.chat_history:
            self.console.print("📭 [dim]No conversation history in this session[/dim]")
            return
        
        self.console.print(f"\n[bold cyan]📜 Conversation History[/bold cyan] [dim]({len(self.chat_history)} exchanges)[/dim]")
        self.console.print(f"[dim]Session: {self.current_session_id}[/dim]\n")
        
        for i, exchange in enumerate(self.chat_history, 1):
            user_msg = exchange.get('user', '')
            agent_msg = exchange.get('agent', '')
            timestamp = exchange.get('timestamp', '')
            
            # Format timestamp
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = timestamp[:8] if len(timestamp) > 8 else timestamp
            else:
                time_str = ""
            
            # Show exchange
            self.console.print(f"[bold cyan]{i}.[/bold cyan] [dim]{time_str}[/dim]")
            self.console.print(f"  [bold blue]You:[/bold blue] {user_msg}")
            if agent_msg:
                # Truncate long responses for history view
                if len(agent_msg) > 200:
                    agent_msg = agent_msg[:200] + "..."
                self.console.print(f"  [bold green]Agent:[/bold green] {agent_msg}")
            self.console.print()
    
    async def interactive_chat(self):
        """Start interactive chat mode - like Claude Code"""
        self.print_banner()
        
        try:
            while True:
                try:
                    # Get user input with Claude Code-like interface
                    user_input = self.get_user_input()
                    
                    if not user_input.strip():
                        continue
                    
                    # Process command/message
                    should_continue = await self.process_command(user_input)
                    if not should_continue:
                        break
                        
                except KeyboardInterrupt:
                    if Confirm.ask("\n🤔 Do you want to exit?"):
                        break
                except EOFError:
                    break
                    
        finally:
            self.console.print("\n👋 [bold cyan]Goodbye![/bold cyan]")
    
    def get_user_input(self) -> str:
        """Get user input with Claude Code-like interface"""
        from rich.prompt import Prompt
        
        # Claude Code-like prompt
        self.console.print()
        
        # Check for multi-line input
        try:
            # Use Rich Prompt for better styling
            first_line = Prompt.ask("[bold cyan]>[/bold cyan]", console=self.console)
            
            # Check if user wants multi-line (ending with backslash)
            if first_line.endswith('\\'):
                lines = [first_line[:-1]]  # Remove backslash
                self.console.print("[dim]↳ Multi-line mode - empty line to send[/dim]")
                
                while True:
                    try:
                        line = input("  ")
                        if line.strip() == "":
                            break
                        lines.append(line)
                    except EOFError:
                        break
                        
                return '\n'.join(lines)
            else:
                return first_line
                
        except EOFError:
            # Handle EOF (Ctrl+D or piped input ending) by raising it
            # This will be caught in interactive_chat() and exit gracefully
            raise EOFError("End of input")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="isA Agent CLI - Interactive chat interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                           # Interactive mode
  python cli.py "Hello, agent!"          # Single message
  python cli.py --sync "What is 2+2?"    # Synchronous mode
  python cli.py --upload doc.pdf "Analyze this document"  # Upload files
  python cli.py --upload file1.txt,file2.pdf "Compare these" --test-rag  # Upload and test RAG
  python cli.py --config                 # Show configuration
  python cli.py --sessions               # List sessions
  python cli.py --health                 # Check API health
"""
    )
    
    parser.add_argument('message', nargs='?', help='Single message to send (non-interactive mode)')
    parser.add_argument('--sync', action='store_true', help='Use synchronous mode instead of streaming')
    parser.add_argument('--config', action='store_true', help='Show configuration and exit')
    parser.add_argument('--sessions', action='store_true', help='List sessions and exit')
    parser.add_argument('--health', action='store_true', help='Check API health and exit')
    parser.add_argument('--api-url', help='Override API base URL')
    parser.add_argument('--api-key', help='Override API key')
    parser.add_argument('--user-id', help='Override user ID')
    parser.add_argument('--session-id', help='Override session ID')
    parser.add_argument('--timeout', type=int, help='Request timeout in seconds')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all event types (verbose mode)')
    parser.add_argument('--simple', '-s', action='store_true', help='Simple mode - Claude Code style (hide technical details)')
    parser.add_argument('--upload', nargs='+', help='Upload files with message')
    parser.add_argument('--test-rag', action='store_true', help='Test RAG functionality after file upload')
    
    args = parser.parse_args()
    
    # Load configuration
    config = CLIConfig.load()
    
    # Apply command line overrides
    if args.api_url:
        config.api_base_url = args.api_url
    if args.api_key:
        config.api_key = args.api_key
    if args.user_id:
        config.user_id = args.user_id
    if args.session_id:
        config.default_session_id = args.session_id
    if args.timeout:
        config.timeout = args.timeout
    # Handle display modes
    if args.verbose:
        # Verbose mode - show ALL events
        config.show_events = []
        config.hide_events = []
        config.simple_mode = False
    elif args.simple:
        # Simple mode - Claude Code style (hide technical details)
        config.simple_mode = True
        config.hide_events = [
            "node.enter",
            "node.exit",
            "context.tools_ready",
            "context.prompts_ready",
            "context.resources_ready",
            "context.memory_ready",
            "context.knowledge_ready",
            "memory.storing",
            "memory.curating"
        ]
    # else: use default config (show most events)
    
    # Create CLI instance
    async with AgentChatCLI(config) as cli:
        
        # Handle non-interactive modes
        if args.config:
            cli.print_config()
            return
        
        if args.sessions:
            await cli.list_sessions()
            return
        
        if args.health:
            await cli.check_health()
            return
        
        if args.message:
            # Single message mode
            try:
                output_format = "json" if args.sync else "stream"
                
                # Check if files should be uploaded
                if args.upload:
                    result = await cli.send_message_with_files(args.message, args.upload, output_format)
                    
                    # Test RAG functionality if requested
                    if args.test_rag:
                        await cli.test_rag_functionality()
                else:
                    result = await cli.send_message(args.message, output_format)
                
                if args.sync:
                    console = Console()
                    console.print(f"\n[bold blue]You:[/bold blue] {args.message}")
                    console.print(f"[bold green]Agent:[/bold green] {result.get('response', 'No response')}")
                    if result.get('events_count'):
                        console.print(f"[dim]({result['events_count']} events processed)[/dim]")
                
            except Exception as e:
                console = Console()
                console.print(f"❌ [bold red]Error: {e}[/bold red]")
                exit(1)
        else:
            # Interactive mode
            await cli.interactive_chat()
    
    # Save configuration on exit
    config.save()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        exit(0)