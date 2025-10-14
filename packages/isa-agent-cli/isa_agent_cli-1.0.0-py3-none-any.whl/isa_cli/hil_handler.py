"""
Human-in-Loop (HIL) request handler for isA Agent CLI
Handles interactive authorization and decision prompts
"""

import sys
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
import requests


class HILHandler:
    """Handles Human-in-Loop interactions"""
    
    def __init__(self, console: Console, config, resume_callback=None):
        self.console = console
        self.config = config
        self.resume_callback = resume_callback  # Callback to notify main program to continue streaming
    
    def handle_request(self, event: Dict[str, Any]):
        """Handle HIL request and user interaction"""
        content = event.get('content', '')
        metadata = event.get('metadata', {})
        interrupt_data = metadata.get('interrupt_data', {})
        
        self.console.print()
        self.console.print("🤖 [bold yellow]Human input required[/bold yellow]")
        
        if interrupt_data.get('type') == 'batch_tool_authorization':
            tools = interrupt_data.get('tools', [])
            message = interrupt_data.get('message', 'Authorization required')
            user_id = interrupt_data.get('user_id', 'unknown')
            
            # Enhanced tool authorization interface
            self._handle_enhanced_tool_authorization(tools, message, user_id)
                
        # Handle ask_human type (execution plan approval)
        elif interrupt_data.get('type') == 'ask_human':
            question = interrupt_data.get('question', 'Please provide input')
            
            # Display the question in a panel
            self.console.print(Panel(
                question,
                title="📋 Execution Plan Review",
                title_align="left", 
                border_style="cyan",
                expand=False
            ))
            
            # Handle user decision
            try:
                if sys.stdin.isatty():
                    while True:
                        try:
                            response = input("Your choice (approve/reject/modify): ").strip().lower()
                            if response in ['approve', 'a']:
                                decision = "approve"
                                break
                            elif response in ['reject', 'r']:
                                decision = "reject"
                                break
                            elif response in ['modify', 'm']:
                                decision = "modify"
                                break
                            else:
                                self.console.print("[yellow]Please enter 'approve', 'reject', or 'modify'[/yellow]")
                        except EOFError:
                            decision = "reject"
                            break
                else:
                    self.console.print("[yellow]Non-interactive mode detected. Defaulting to reject.[/yellow]")
                    decision = "reject"
                
                # Send resume request with user decision
                self._send_hil_resume_with_decision(decision)
                
            except KeyboardInterrupt:
                self.console.print("\n[red]❌ User cancelled[/red]")
                self._send_hil_resume_with_decision("reject")
            except Exception as e:
                self.console.print(f"[red]❌ Error getting user input: {e}[/red]")
                self.console.print("[yellow]Defaulting to reject.[/yellow]")
                self._send_hil_resume_with_decision("reject")
        
        # SCENARIO 2: Tool Authorization (supports both 'authorization' and 'tool_authorization' types)
        elif interrupt_data.get('type') in ['authorization', 'tool_authorization']:
            tool_name = interrupt_data.get('tool_name', 'unknown')
            security_level = interrupt_data.get('security_level', 'UNKNOWN')
            reason = interrupt_data.get('reason', 'No reason provided')
            question = interrupt_data.get('question', f"Authorize {tool_name}?")
            
            self.console.print(Panel(
                f"🔐 Tool: [bold]{tool_name}[/bold]\n"
                f"🛡️ Security Level: [bold red]{security_level}[/bold red]\n"
                f"📝 Reason: {reason}\n\n"
                f"{question}",
                title="🔒 Tool Authorization Required",
                title_align="left",
                border_style="red",
                expand=False
            ))
            
            self._handle_approve_reject_input()
        
        # SCENARIO 3: OAuth Authorization  
        elif interrupt_data.get('type') == 'oauth_authorization':
            provider = interrupt_data.get('provider', 'unknown')
            oauth_url = interrupt_data.get('oauth_url', '')
            scopes = interrupt_data.get('scopes', [])
            question = interrupt_data.get('question', f"Authorize {provider}?")
            
            self.console.print(Panel(
                f"🔗 Provider: [bold]{provider}[/bold]\n"
                f"🔑 Scopes: {', '.join(scopes) if scopes else 'default'}\n"
                f"🌐 OAuth URL: [link]{oauth_url}[/link]\n\n"
                f"{question}",
                title="🔐 OAuth Authorization Required",
                title_align="left",
                border_style="blue",
                expand=False
            ))
            
            self._handle_approve_reject_input()
        
        # SCENARIO 4a: Credential Usage Authorization
        elif interrupt_data.get('type') == 'credential_authorization':
            provider = interrupt_data.get('provider', 'unknown')
            credential_preview = interrupt_data.get('credential_preview', {})
            vault_id = credential_preview.get('vault_id', 'unknown')
            question = interrupt_data.get('question', f"Use stored credentials?")
            
            self.console.print(Panel(
                f"🔐 Provider: [bold]{provider}[/bold]\n"
                f"🗝️ Vault ID: {vault_id}\n"
                f"📅 Stored: {credential_preview.get('stored_at', 'unknown')}\n\n"
                f"{question}",
                title="🔑 Use Stored Credentials?",
                title_align="left",
                border_style="green",
                expand=False
            ))
            
            self._handle_approve_reject_input()
        
        # SCENARIO 4b: Manual Intervention
        elif interrupt_data.get('type') == 'manual_intervention':
            intervention_type = interrupt_data.get('intervention_type', 'unknown')
            provider = interrupt_data.get('provider', 'unknown')
            instructions = interrupt_data.get('instructions', 'Please complete the action manually')
            question = interrupt_data.get('question', 'Manual action required')
            
            self.console.print(Panel(
                f"🚨 Type: [bold]{intervention_type.upper()}[/bold]\n"
                f"🌐 Provider: {provider}\n"
                f"📋 Instructions: {instructions}\n\n"
                f"{question}",
                title="⚠️ Manual Intervention Required",
                title_align="left",
                border_style="yellow",
                expand=False
            ))
            
            self._handle_text_input()
        
        # SCENARIO 1: Collect User Input (using new scenario naming)
        elif interrupt_data.get('type') == 'collect_user_input':
            question = interrupt_data.get('question', 'Please provide information')
            validation_rules = interrupt_data.get('validation_rules')
            
            self.console.print(Panel(
                question,
                title="💬 Information Required",
                title_align="left",
                border_style="cyan",
                expand=False
            ))
            
            self._handle_text_input(validation_rules)
                
        else:
            # Other types of HIL requests
            self.console.print(f"[yellow]{content}[/yellow]")
            self.console.print(f"[dim]HIL type '{interrupt_data.get('type', 'unknown')}' not yet implemented[/dim]")
    
    def _send_hil_resume(self, approve: bool):
        """Send HIL resume request to continue execution"""
        # Get session_id from config or use current session
        session_id = getattr(self.config, 'current_session_id', self.config.default_session_id)
        
        resume_payload = {
            "session_id": session_id,
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
    
    def _handle_approve_reject_input(self):
        """Handle approve/reject input for authorization scenarios"""
        try:
            if sys.stdin.isatty():
                while True:
                    try:
                        response = input("Your choice (approve/reject) [a/r]: ").strip().lower()
                        if response in ['approve', 'a', 'yes', 'y']:
                            self._send_hil_resume_with_decision("approve")
                            break
                        elif response in ['reject', 'r', 'no', 'n']:
                            self._send_hil_resume_with_decision("reject")
                            break
                        else:
                            self.console.print("[yellow]Please enter 'approve' or 'reject'[/yellow]")
                    except EOFError:
                        self._send_hil_resume_with_decision("reject")
                        break
            else:
                self.console.print("[yellow]Non-interactive mode detected. Defaulting to reject.[/yellow]")
                self._send_hil_resume_with_decision("reject")
        except KeyboardInterrupt:
            self.console.print("\n[red]❌ User cancelled[/red]")
            self._send_hil_resume_with_decision("reject")
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
            self._send_hil_resume_with_decision("reject")
    
    def _handle_text_input(self, validation_rules=None):
        """Handle free-form text input for information collection"""
        try:
            if sys.stdin.isatty():
                while True:
                    try:
                        user_input = input("Your input: ").strip()
                        
                        # Validate if rules provided
                        if validation_rules:
                            # Simple validation (can be expanded)
                            if validation_rules.get('type') == 'int':
                                try:
                                    int(user_input)
                                except ValueError:
                                    self.console.print("[yellow]Please enter a valid number[/yellow]")
                                    continue
                            elif validation_rules.get('min') and len(user_input) < validation_rules['min']:
                                self.console.print(f"[yellow]Input too short (min: {validation_rules['min']})[/yellow]")
                                continue
                        
                        # Send the user's text input
                        self._send_hil_resume_with_text(user_input)
                        break
                    except EOFError:
                        self._send_hil_resume_with_text("")
                        break
            else:
                # In non-interactive mode, try to read one line
                try:
                    user_input = input().strip()
                    self._send_hil_resume_with_text(user_input)
                except EOFError:
                    self.console.print("[yellow]Non-interactive mode without input. Sending empty response.[/yellow]")
                    self._send_hil_resume_with_text("")
        except KeyboardInterrupt:
            self.console.print("\n[red]❌ User cancelled[/red]")
            self._send_hil_resume_with_text("")
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
            self._send_hil_resume_with_text("")
    
    def _handle_enhanced_tool_authorization(self, tools, message, user_id):
        """Enhanced tool authorization interface with detailed information"""
        
        # Display detailed tool information
        self._display_tool_authorization_details(tools, message, user_id)
        
        # Handle user interaction
        try:
            # Check for non-interactive mode first
            if not sys.stdin.isatty():
                # Try to read one line of input for non-interactive mode
                try:
                    response = input().strip().lower()
                    if response in ['y', 'yes', 'a', 'approve']:
                        self.console.print("✅ [green]Authorization approved via non-interactive input[/green]")
                        self._send_hil_resume_with_decision("approve")
                        return True
                    else:
                        self.console.print("❌ [red]Authorization rejected via non-interactive input[/red]")
                        self._send_hil_resume_with_decision("reject")
                        return False
                except EOFError:
                    self.console.print("[yellow]Non-interactive mode without input. Defaulting to reject for security.[/yellow]")
                    self._send_hil_resume_with_decision("reject")
                    return False
            
            # Interactive mode with enhanced options
            while True:
                try:
                    self.console.print("\n🤔 [bold cyan]What would you like to do?[/bold cyan]")
                    self.console.print("  [bold green][A][/bold green] Approve all tools")
                    self.console.print("  [bold red][D][/bold red] Deny all tools  ")
                    self.console.print("  [bold blue][V][/bold blue] View tool details")
                    self.console.print("  [bold yellow][H][/bold yellow] Help")
                    self.console.print()
                    
                    response = input("Choice [A/d/v/h]: ").strip().lower()
                    
                    if response in ['a', 'approve', 'y', 'yes']:
                        self.console.print("✅ [green]All tools approved[/green]")
                        self._send_hil_resume_with_decision("approve")
                        return True
                    elif response in ['d', 'deny', 'n', 'no', '']:
                        self.console.print("❌ [red]All tools denied[/red]")
                        self._send_hil_resume_with_decision("reject")
                        return False
                    elif response in ['v', 'view', 'details']:
                        self._show_detailed_tool_info(tools)
                        continue
                    elif response in ['h', 'help']:
                        self._show_help()
                        continue
                    else:
                        self.console.print("[yellow]Invalid choice. Please enter A, D, V, or H[/yellow]")
                        continue
                        
                except EOFError:
                    self.console.print("\n[yellow]No input received. Defaulting to reject for security.[/yellow]")
                    self._send_hil_resume_with_decision("reject")
                    return False
                    
        except KeyboardInterrupt:
            self.console.print("\n[red]❌ User cancelled authorization[/red]")
            self._send_hil_resume_with_decision("reject")
            return False
        except Exception as e:
            self.console.print(f"[red]❌ Error during authorization: {e}[/red]")
            self.console.print("[yellow]Defaulting to reject for security.[/yellow]")
            self._send_hil_resume_with_decision("reject")
            return False
    
    def _display_tool_authorization_details(self, tools, message, user_id):
        """Display detailed tool authorization information"""
        from rich.table import Table
        
        # Create main panel content
        panel_content = []
        panel_content.append(f"🎯 [bold]Context:[/bold] User requested an action requiring tool execution")
        panel_content.append(f"👤 [bold]User ID:[/bold] {user_id}")
        panel_content.append("")
        panel_content.append("📋 [bold]The following tools require authorization:[/bold]")
        panel_content.append("")
        
        # Create tool summary table
        tool_table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        tool_table.add_column("Tool", style="cyan", min_width=15)
        tool_table.add_column("Security", style="yellow", min_width=10)
        tool_table.add_column("Risk Level", style="red", min_width=12)
        
        security_colors = {
            "LOW": "green",
            "MEDIUM": "yellow", 
            "HIGH": "red",
            "CRITICAL": "bright_red"
        }
        
        risk_descriptions = {
            "LOW": "Minimal risk",
            "MEDIUM": "Moderate risk",
            "HIGH": "Significant risk", 
            "CRITICAL": "Maximum risk"
        }
        
        for tool_name, security_level in tools:
            color = security_colors.get(security_level, "white")
            risk_desc = risk_descriptions.get(security_level, "Unknown risk")
            
            tool_table.add_row(
                f"[bold]{tool_name}[/bold]",
                f"[{color}]{security_level}[/{color}]",
                f"[{color}]{risk_desc}[/{color}]"
            )
        
        # Display the authorization panel
        self.console.print(Panel(
            "\n".join(panel_content),
            title="🔐 Tool Authorization Request",
            title_align="left",
            border_style="yellow",
            expand=False
        ))
        
        self.console.print(tool_table)
        
        # Show the original message if it contains useful info
        if message and "Multiple tools require authorization" not in message:
            self.console.print(Panel(
                message,
                title="📝 Additional Information",
                title_align="left", 
                border_style="blue",
                expand=False
            ))
    
    def _show_detailed_tool_info(self, tools):
        """Show detailed information about each tool"""
        from rich.table import Table
        
        self.console.print("\n📊 [bold]Detailed Tool Information:[/bold]")
        
        for tool_name, security_level in tools:
            # Create detailed info for each tool
            details_table = Table(show_header=False, show_lines=False, pad_edge=False)
            details_table.add_column("Property", style="cyan", min_width=15)
            details_table.add_column("Value", style="white")
            
            details_table.add_row("🔧 Tool Name", f"[bold]{tool_name}[/bold]")
            details_table.add_row("🛡️ Security Level", f"[red]{security_level}[/red]")
            
            # Add tool-specific information
            tool_descriptions = {
                "get_weather": "Fetches current weather data from external API",
                "web_search": "Searches the web for information",
                "file_read": "Reads files from the local filesystem",
                "file_write": "Writes data to local files",
                "email_send": "Sends emails via configured email service"
            }
            
            tool_risks = {
                "get_weather": "Accesses external weather API, may expose IP address",
                "web_search": "Accesses external search services, may expose search queries", 
                "file_read": "Can access local files and data",
                "file_write": "Can modify or create local files",
                "email_send": "Can send emails on your behalf"
            }
            
            if tool_name in tool_descriptions:
                details_table.add_row("📝 Description", tool_descriptions[tool_name])
            if tool_name in tool_risks:
                details_table.add_row("⚠️ Potential Risks", f"[yellow]{tool_risks[tool_name]}[/yellow]")
            
            self.console.print(Panel(
                details_table,
                title=f"🔧 {tool_name}",
                title_align="left",
                border_style="cyan",
                expand=False
            ))
        
        self.console.print()
    
    def _show_help(self):
        """Show help information for tool authorization"""
        help_content = [
            "[bold]Tool Authorization Help[/bold]",
            "",
            "[bold green]Approve (A):[/bold green] Grant permission for all listed tools to execute",
            "[bold red]Deny (D):[/bold red] Reject permission - tools will not execute", 
            "[bold blue]View (V):[/bold blue] Show detailed information about each tool",
            "[bold yellow]Help (H):[/bold yellow] Show this help message",
            "",
            "[bold]Security Levels:[/bold]",
            "  🟢 [green]LOW[/green] - Safe operations with minimal risk",
            "  🟡 [yellow]MEDIUM[/yellow] - Moderate risk operations", 
            "  🔴 [red]HIGH[/red] - Significant risk - review carefully",
            "  🚨 [bright_red]CRITICAL[/bright_red] - Maximum risk - extreme caution",
            "",
            "[dim]Tip: Use 'V' to review tool details before making a decision[/dim]"
        ]
        
        self.console.print(Panel(
            "\n".join(help_content),
            title="❓ Help",
            title_align="left",
            border_style="blue", 
            expand=False
        ))
        self.console.print()

    def _send_hil_resume_with_decision(self, decision: str):
        """Send HIL authorization using correct format from hil_test.html"""
        # Get session_id from config or use current session
        session_id = getattr(self.config, 'current_session_id', self.config.default_session_id)
        
        # Use the exact format from hil_test.html
        resume_payload = {
            "session_id": session_id,
            "user_id": self.config.user_id,
            "resume_value": {
                "action": "approve" if decision == "approve" else "reject",
                "approved": decision == "approve",
                "message": f"User chose '{decision}' from CLI"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Send resume with streaming enabled (like hil_test.html)
            headers["Accept"] = "text/event-stream"
            headers["Cache-Control"] = "no-cache"
            headers["Connection"] = "keep-alive"
            
            response = requests.post(
                f"{self.config.api_base_url}/api/v1/agents/chat/resume",
                json=resume_payload,
                headers=headers,
                stream=True,
                timeout=(30, None)  # (connect, read) timeout
            )
            
            if response.status_code == 200:
                self.console.print(f"✅ [green]Authorization '{decision}' sent successfully[/green]")
                
                # Check if response is SSE stream for resumed execution
                if 'text/event-stream' in response.headers.get('content-type', ''):
                    self.console.print("🔄 [cyan]Receiving resumed execution stream...[/cyan]")
                    self._handle_resume_stream(response)
                
                # Notify the callback that authorization was sent
                if self.resume_callback:
                    try:
                        self.resume_callback()
                    except Exception as e:
                        self.console.print(f"[red]❌ Callback error: {e}[/red]")
            else:
                self.console.print(f"[red]❌ Failed to send authorization: {response.status_code} - {response.text}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error sending authorization: {e}[/red]")
    
    def _send_hil_resume_with_text(self, user_input: str):
        """Send HIL resume with user's text input"""
        # Get session_id from config or use current session
        session_id = getattr(self.config, 'current_session_id', self.config.default_session_id)
        
        # Send user's actual text input as resume value
        resume_payload = {
            "session_id": session_id,
            "user_id": self.config.user_id,
            "resume_value": user_input  # Direct text value
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        
        try:
            response = requests.post(
                f"{self.config.api_base_url}/api/v1/agents/chat/resume",
                json=resume_payload,
                headers=headers,
                stream=True,
                timeout=(30, None)
            )
            
            if response.status_code == 200:
                self.console.print(f"✅ [green]Input sent successfully[/green]")
                
                # Handle streaming response
                if 'text/event-stream' in response.headers.get('content-type', ''):
                    self.console.print("🔄 [cyan]Receiving resumed execution stream...[/cyan]")
                    self._handle_resume_stream(response)
                
                if self.resume_callback:
                    try:
                        self.resume_callback()
                    except Exception as e:
                        self.console.print(f"[red]❌ Callback error: {e}[/red]")
            else:
                self.console.print(f"[red]❌ Failed to send input: {response.status_code}[/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
    
    def _handle_resume_stream(self, response):
        """Handle the SSE stream from resume endpoint"""
        import json
        
        try:
            buffer = ""
            for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
                if not chunk:
                    continue
                    
                buffer += chunk
                
                # Process complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith(':'):
                        continue
                        
                    # Parse SSE format
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        
                        # Check for end of stream
                        if data_str.strip() == '[DONE]':
                            self.console.print("✅ [green]Resume execution completed[/green]")
                            return
                        
                        # Parse and display event
                        try:
                            event = json.loads(data_str)
                            self._display_resume_event(event)
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            self.console.print(f"[red]❌ Error processing resume stream: {e}[/red]")
    
    def _display_resume_event(self, event):
        """Display events from resume stream"""
        event_type = event.get('type', '')
        content = event.get('content', '')
        
        if event_type == 'content.token':
            # Display response tokens directly
            self.console.print(content, end='', style="white")
        elif event_type.startswith('tool'):
            self.console.print(f"🔧 {content}", style="cyan")
        elif event_type == 'session.end':
            self.console.print("\n📡 [bold blue]Session completed[/bold blue]")
        elif event_type == 'session.start':
            self.console.print("🔄 [cyan]Execution resumed[/cyan]")
        elif 'progress' in content or 'Completed' in content:
            self.console.print(f"⚙️ {content}", style="yellow")
        elif 'response_chunk' in content and event.get('response_chunk'):
            # Display final response tokens
            self.console.print(event['response_chunk'], end='', style="white")
        elif 'thinking_chunk' in content:
            # Skip individual thinking chunks for cleaner output
            pass
        elif content and not any(x in content for x in ['thinking_chunk', 'response_chunk', 'Resume custom']):
            self.console.print(f"📨 {content}", style="white")
    
    def _send_basic_resume_request(self, decision: str, session_id: str):
        """Fallback method for basic resume request (legacy behavior)"""
        resume_payload = {
            "session_id": session_id,
            "user_id": self.config.user_id,
            "decision": decision,
            "message": f"User chose '{decision}' for execution plan from CLI"
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
                self.console.print(f"✅ [green]Basic resume request sent[/green]")
            else:
                self.console.print(f"[red]❌ Failed to send basic resume: {response.status_code}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error sending basic resume: {e}[/red]")