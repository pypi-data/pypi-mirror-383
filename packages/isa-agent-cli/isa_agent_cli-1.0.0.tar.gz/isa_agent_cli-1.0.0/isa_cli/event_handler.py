"""
Event streaming handler for isA Agent CLI
Handles all SSE event processing and display logic
"""

from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel


class EventStreamHandler:
    """Handles streaming events from the isA Agent API"""
    
    def __init__(self, console: Console, config, session_id_getter=None):
        self.console = console
        self.config = config
        self.session_id_getter = session_id_getter
        self.thinking_buffer = []
        self.response_buffer = []
        self.events_received = []
        self.hil_authorization_sent = False  # Track if HIL authorization was sent
        self.events_after_authorization = 0  # Count events after authorization
        
    def reset_buffers(self):
        """Reset all buffers for new conversation"""
        self.thinking_buffer = []
        self.response_buffer = []
        self.events_received = []
        self.hil_authorization_sent = False
    
    def process_event(self, event: Dict[str, Any]) -> bool:
        """
        Process a single SSE event and display it appropriately
        Returns True if stream should continue, False if it should end
        """
        event_type = event.get('type', '')
        
        # Store event
        self.events_received.append(event)
        
        # Debug: Print all events to see what we're getting
        if hasattr(self.config, 'show_debug') and self.config.show_debug:
            content = event.get('content', '')[:50]  # First 50 chars
            self.console.print(f"[dim]DEBUG EVENT: {event_type} - {content}[/dim]")
        
        # Handle different event types
        if event_type == 'session.start':
            self._handle_session_start(event)
            
        elif event_type == 'session.end':
            self._handle_session_end(event)
            # Don't end stream immediately - wait for memory events that come after session.end
            return True  # Continue stream to receive memory events
            
        elif event_type == 'session.paused':
            self._handle_session_paused(event)
            # Only end stream if HIL authorization wasn't sent
            if hasattr(self.config, 'show_debug') and self.config.show_debug:
                self.console.print(f"[dim]DEBUG: session.paused - hil_authorization_sent={self.hil_authorization_sent}[/dim]")
            
            if not self.hil_authorization_sent:
                return False  # End stream
            else:
                # HIL authorization was sent, continue waiting for resumed execution
                self.console.print("🔄 [cyan]Continuing stream after HIL authorization...[/cyan]")
                self.console.print("⏳ [dim]Waiting for resume events... (this may take a moment)[/dim]")
                return True  # Continue stream
            
        elif event_type.startswith('context.'):
            self._handle_context_event(event)
            
        elif event_type == 'content.thinking':
            self._handle_thinking_token(event)
            
        elif event_type == 'content.complete':
            self._handle_content_complete(event)
            
        elif event_type == 'content.token':
            self._handle_response_token(event)
            
        elif event_type.startswith('tool'):
            self._handle_tool_event(event)
            
        elif event_type.startswith('progress'):
            # Check if this progress event contains HIL data
            if self._contains_hil_interrupt(event):
                self._handle_embedded_hil_request(event)
            else:
                self._handle_progress_event(event)
            
        elif event_type.startswith('system.billing'):
            self._handle_billing_event(event)
            
        elif event_type.startswith('memory.'):
            self._handle_memory_event(event)
            
        elif event_type.startswith('node.'):
            self._handle_node_event(event)
            
        elif event_type == 'hil.request':
            self._handle_hil_request(event)
            
        else:
            self._handle_unknown_event(event)
            
        return True  # Continue stream
    
    def _handle_session_start(self, _event: Dict[str, Any]):
        """Handle session start event"""
        self.console.print("📡 Session started", style="bold blue")
    
    def _handle_session_end(self, _event: Dict[str, Any]):
        """Handle session end event"""
        self.console.print("📡 Session ended", style="bold blue")
    
    def _handle_session_paused(self, _event: Dict[str, Any]):
        """Handle session paused event"""
        self.console.print("⏸️ [bold yellow]Session paused - waiting for human input[/bold yellow]")
    
    def _handle_context_event(self, event: Dict[str, Any]):
        """Handle context preparation events"""
        event_type = event.get('type', '')
        metadata = event.get('metadata', {})
        content = event.get('content', '')
        
        # Claude Code style - simpler display
        if self.config.simple_mode:
            # Only show loading and complete in simple mode
            if event_type == 'context.loading':
                self.console.print(f"⚙️  {content}", style="dim cyan")
            elif event_type == 'context.complete':
                # Just a checkmark, no duration
                self.console.print(f"✓ Ready", style="dim green")
        else:
            # Detailed mode - show all context events
            if event_type == 'context.loading' or event_type == 'context.tools_loading':
                self.console.print(f"🔧 ⚙️ {content}", style="blue")
            elif event_type == 'context.tools_ready':
                tools_count = metadata.get('tools_count', 0)
                self.console.print(f"🔧 ✅ Tools ready ({tools_count})", style="blue")
            elif event_type == 'context.prompts_ready':
                prompts_count = metadata.get('prompts_count', 0)
                self.console.print(f"📝 ✅ Prompts ready ({prompts_count})", style="blue")
            elif event_type == 'context.resources_ready':
                resources_count = metadata.get('resources_count', 0)
                self.console.print(f"📦 ✅ Resources ready ({resources_count})", style="blue")
            elif event_type == 'context.memory_ready':
                memory_length = metadata.get('memory_length', 0)
                self.console.print(f"🧠 ✅ Memory ready ({memory_length} chars)", style="blue")
            elif event_type == 'context.knowledge_ready':
                files_count = metadata.get('files_count', 0)
                self.console.print(f"📚 ✅ Knowledge ready ({files_count} files)", style="blue")
            elif event_type == 'context.complete':
                duration = metadata.get('duration_ms', metadata.get('preparation_ms', 0))
                self.console.print(f"✅ Context ready ({duration}ms)", style="bold blue")
    
    def _handle_thinking_token(self, event: Dict[str, Any]):
        """Handle thinking token - collect for expandable section"""
        content = event.get('content', '')
        self.thinking_buffer.append(content)
    
    def _handle_content_complete(self, event: Dict[str, Any]):
        """Handle content complete events"""
        metadata = event.get('metadata', {})
        node = metadata.get('node', '')
        
        if node == 'thinking_complete':
            # Show thinking section
            if self.thinking_buffer:
                thinking_text = ''.join(self.thinking_buffer)
                self._show_expandable_section("💭 Thinking", thinking_text, "yellow")
                self.thinking_buffer = []
        elif node == 'AIMessage':
            # Final response complete - ensure clean line break
            if self.response_buffer:
                self.console.print()  # Clean line break after response
    
    def _handle_response_token(self, event: Dict[str, Any]):
        """Handle response token - display inline with immediate flush (Claude Code style)"""
        content = event.get('content', '')
        self.response_buffer.append(content)
        
        # First token - add newline for clean separation
        if len(self.response_buffer) == 1:
            print()  # Clean line break before response
        
        # Display token immediately (like Claude Code streaming)
        import sys
        print(content, end='', flush=True)
    
    def _handle_tool_event(self, event: Dict[str, Any]):
        """Handle tool-related events"""
        event_type = event.get('type', '')
        content = event.get('content', '')
        metadata = event.get('metadata', {})
        
        if event_type == 'tool.call':
            # New format: tool.call with metadata
            tool_name = metadata.get('tool', 'unknown tool')
            args = metadata.get('args', {})
            query = args.get('query', '')
            if query:
                self.console.print(f"🔧 Calling {tool_name}: {query}", style="cyan")
            else:
                self.console.print(f"🔧 Calling {tool_name}", style="cyan")
        elif event_type == 'tool.result':
            # Tool result - show preview
            tool_name = metadata.get('tool', 'unknown')
            result_preview = metadata.get('result_preview', content)
            # Parse JSON result if possible
            try:
                import json
                if isinstance(result_preview, str) and result_preview.startswith('{'):
                    result_data = json.loads(result_preview)
                    status = result_data.get('status', 'unknown')
                    self.console.print(f"✅ {tool_name} completed (status: {status})", style="green")
                else:
                    preview = result_preview[:100]
                    self.console.print(f"✅ {tool_name} completed: {preview}", style="green")
            except:
                preview = str(result_preview)[:100]
                self.console.print(f"✅ {tool_name} completed: {preview}", style="green")
        elif event_type == 'tool.executing':
            # Tool execution progress
            if 'Starting execution' in content:
                self.console.print(f"⚙️ {content}", style="yellow")
            elif 'Completed' in content:
                self.console.print(f"✅ {content}", style="green")
            else:
                self.console.print(f"🔧 {content}", style="cyan")
        elif event_type == 'tool_calls':
            # Legacy format
            tool_calls = metadata.get('tool_calls', [])
            for tool_call in tool_calls:
                tool_name = tool_call.get('name', 'unknown tool')
                self.console.print(f"🔧 Calling tool: {tool_name}", style="cyan")
        else:
            # Other tool events
            self.console.print(f"🔧 {content}", style="cyan")
    
    def _handle_billing_event(self, event: Dict[str, Any]):
        """Handle billing events"""
        metadata = event.get('metadata', {})
        credits = metadata.get('credits', metadata.get('total_credits', 0))
        if credits:
            remaining = metadata.get('credits_remaining', 0)
            if remaining:
                self.console.print(f"💳 Used {credits} credits ({remaining} remaining)", style="magenta")
            else:
                self.console.print(f"💳 Used {credits} credits", style="magenta")
    
    def _handle_memory_event(self, event: Dict[str, Any]):
        """Handle memory management events"""
        event_type = event.get('type', '')
        metadata = event.get('metadata', {})
        
        if event_type == 'memory.storing':
            self.console.print("💾 Storing memories...", style="purple")
        elif event_type == 'memory.stored':
            count = metadata.get('memories_count', 0)
            self.console.print(f"💾 ✅ Stored {count} memories", style="purple")
        elif event_type == 'memory.curating':
            self.console.print("🎨 Curating memories...", style="purple")
        elif event_type == 'memory.curated':
            self.console.print("✨ Memory curation complete", style="purple")
    
    def _handle_node_event(self, event: Dict[str, Any]):
        """Handle node execution events"""
        event_type = event.get('type', '')
        metadata = event.get('metadata', {})
        
        if event_type == 'node.exit':
            node_name = metadata.get('node', 'unknown')
            next_action = metadata.get('next_action', '')
            
            # 使用不同的图标表示不同的节点
            node_icons = {
                'reason_model': '🧠',
                'call_tool': '🔧',
                'agent_executor': '⚙️',
                'format_response': '📝'
            }
            icon = node_icons.get(node_name, 'ℹ️')
            
            if next_action:
                self.console.print(f"{icon} Exiting {node_name} → {next_action}", style="dim cyan")
            else:
                self.console.print(f"{icon} Exiting {node_name}", style="dim cyan")
        elif event_type == 'node.enter':
            # 通常不显示node.enter，因为太详细了
            if self.config.show_debug:
                node_name = metadata.get('node', 'unknown')
                self.console.print(f"→ Entering {node_name}", style="dim")
    
    def _handle_hil_request(self, event: Dict[str, Any]):
        """Handle Human-in-Loop requests"""
        from .hil_handler import HILHandler
        # Create enhanced config with current session ID
        enhanced_config = self.config
        if self.session_id_getter:
            enhanced_config.current_session_id = self.session_id_getter()
        
        # Create simple callback that sets the authorization flag
        def hil_authorization_callback():
            self.hil_authorization_sent = True
            self.console.print("🔄 [cyan]Authorization sent - continuing to wait for execution results...[/cyan]")
        
        hil_handler = HILHandler(self.console, enhanced_config, resume_callback=hil_authorization_callback)
        hil_handler.handle_request(event)
    
    def _contains_hil_interrupt(self, event: Dict[str, Any]) -> bool:
        """Check if progress event contains HIL interrupt data"""
        content = event.get('content', '')
        return ('HIL validation error' in content and 
                'Interrupt(' in content and 
                'type' in content and 
                'ask_human' in content)
    
    def _handle_embedded_hil_request(self, event: Dict[str, Any]):
        """Extract and handle HIL request from progress event"""
        content = event.get('content', '')
        
        # Try to extract the interrupt data from the content
        try:
            # Look for the interrupt data in the content string
            import re
            import ast
            
            # Find the Interrupt(value={...}) part
            pattern = r"Interrupt\(value=(\{.*?\}), resumable=True"
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                interrupt_str = match.group(1)
                # Parse the interrupt data (it's a string representation of a dict)
                interrupt_data = ast.literal_eval(interrupt_str)
                
                # Create a synthetic HIL event
                hil_event = {
                    'type': 'hil.request',
                    'content': 'HIL request detected in progress event',
                    'metadata': {
                        'interrupt_data': interrupt_data
                    },
                    'session_id': event.get('session_id'),
                    'timestamp': event.get('timestamp')
                }
                
                self.console.print("🤖 [bold yellow]Human input required (detected in progress event)[/bold yellow]")
                self._handle_hil_request(hil_event)
                return True
                
        except Exception as e:
            self.console.print(f"[red]❌ Failed to parse HIL data from progress event: {e}[/red]")
        
        # Fallback: just show the progress content
        self._handle_progress_event(event)
        return False
    
    def _handle_progress_event(self, event: Dict[str, Any]):
        """Handle regular progress events"""
        content = event.get('content', '')
        
        if 'Starting execution' in content:
            self.console.print(f"⚙️ {content}", style="yellow")
        elif 'Completed' in content:
            self.console.print(f"✅ {content}", style="green")
        elif 'HIL validation error' in content:
            # This is a HIL-related progress event, show it with warning style
            self.console.print(f"🔧 {content}", style="red")
        else:
            self.console.print(f"🔧 {content}", style="cyan")
    
    def _handle_unknown_event(self, event: Dict[str, Any]):
        """Handle unknown event types"""
        event_type = event.get('type', '')
        content = event.get('content', '')
        
        if self.config.show_debug:
            self.console.print(f"[dim]DEBUG - Unknown event: {event_type}: {content}[/dim]")
        else:
            # Try to display with generic formatting
            self.console.print(f"ℹ️ {content}", style="white")
    
    def _show_expandable_section(self, title: str, content: str, style: str = "white"):
        """Show an expandable section like Claude Code"""
        # Clean up the content
        lines = content.strip().split('\n')
        
        # Show a condensed summary
        summary_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('-') and len(line) > 10:
                summary_lines.append(line)
                if len(summary_lines) >= 2:  # Max 2 lines for summary
                    break
        
        if summary_lines:
            summary = ' '.join(summary_lines)[:150]
            if len(content) > 150:
                summary += "..."
            self.console.print(f"{title}: {summary} [dim](expandable)[/dim]", style=style)
        
        # Show the full panel
        if len(lines) > 3:
            panel = Panel(
                content.strip(),
                title=title,
                title_align="left",
                border_style=style,
                expand=False
            )
            self.console.print(panel)
        else:
            # Short content, just show directly
            self.console.print(f"{title}: {content.strip()}", style=style)
    
    def get_response_text(self) -> str:
        """Get the complete response text"""
        return ''.join(self.response_buffer)
    
    def get_events_count(self) -> int:
        """Get the number of events processed"""
        return len(self.events_received)