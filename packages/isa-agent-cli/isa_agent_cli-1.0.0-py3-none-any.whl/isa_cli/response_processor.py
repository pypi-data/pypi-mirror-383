#!/usr/bin/env python3
"""
Response Processor for isA Agent CLI
Handles processing and formatting of different event types from streaming responses
"""

from typing import Dict, Any, List, Optional
from rich.text import Text
from rich.console import Console


class ResponseProcessor:
    """Processes and formats streaming response events"""
    
    def __init__(self, console: Console, config: Any):
        self.console = console
        self.config = config
    
    def should_show_event(self, event_type: str) -> bool:
        """Determine if event should be displayed based on configuration"""
        # If show_events is specified, only show those
        if self.config.show_events:
            return event_type in self.config.show_events
        
        # If hide_events is specified, hide those
        if self.config.hide_events:
            return event_type not in self.config.hide_events
        
        # Default: show all events except very technical ones
        hidden_by_default = ['node.enter']
        return event_type not in hidden_by_default
    
    def format_event(self, event: Dict[str, Any]) -> Optional[Text]:
        """Format event for display"""
        event_type = event.get('type', 'unknown')
        content = event.get('content', '')
        
        if not self.should_show_event(event_type):
            return None
        
        # Simple mode - hide technical details
        if self.config.simple_mode:
            if event_type in ['context.tools_ready', 'context.prompts_ready', 
                            'context.resources_ready', 'context.memory_ready', 
                            'context.knowledge_ready', 'memory.storing', 'memory.curating']:
                return None
        
        # Format based on event type
        if event_type == 'session.start':
            return Text("📡 Session started", style=self.config.color_scheme.get('info', 'cyan'))
        
        elif event_type.startswith('context.'):
            return Text(f"🔧 {content}", style=self.config.color_scheme.get('system', 'yellow'))
        
        elif event_type == 'content.thinking':
            if self.config.show_metadata:
                timestamp = event.get('timestamp', '')
                return Text(f"💭 {content} ({timestamp})", style=self.config.color_scheme.get('thinking', 'dim cyan'))
            return Text(f"💭 {content}", style=self.config.color_scheme.get('thinking', 'dim cyan'))
        
        elif event_type == 'content.token':
            # Don't prefix tokens, just return the content for streaming display
            return Text(content, style=self.config.color_scheme.get('agent', 'green'))
        
        elif event_type == 'content.complete':
            # Don't display complete events if we're showing tokens
            return None
        
        elif event_type == 'tool_calls':
            return Text(f"🔧 {content}", style=self.config.color_scheme.get('progress', 'magenta'))
        
        elif event_type == 'tool_result_msg':
            return Text(f"⚡ Tool result received", style=self.config.color_scheme.get('success', 'green'))
        
        elif event_type == 'progress':
            return Text(f"⚙️ {content}", style=self.config.color_scheme.get('progress', 'magenta'))
        
        elif event_type.startswith('task.'):
            return Text(f"📋 {content}", style=self.config.color_scheme.get('info', 'cyan'))
        
        elif event_type.startswith('memory.'):
            return Text(f"🧠 {content}", style=self.config.color_scheme.get('system', 'yellow'))
        
        elif event_type == 'system.billing':
            return Text(f"💳 {content}", style=self.config.color_scheme.get('info', 'cyan'))
        
        elif event_type == 'session.end':
            return Text("✅ Response complete", style=self.config.color_scheme.get('success', 'green'))
        
        elif event_type == 'session.paused':
            return Text("⏸️ Session paused - human input required", style=self.config.color_scheme.get('info', 'cyan'))
        
        elif event_type == 'hil.request':
            return Text("🤝 Human input requested", style=self.config.color_scheme.get('info', 'cyan'))
        
        elif event_type == 'node.exit':
            if self.config.show_metadata:
                node = event.get('metadata', {}).get('node', 'unknown')
                return Text(f"🔗 Node: {node} completed", style=self.config.color_scheme.get('system', 'yellow'))
            return None
        
        else:
            # Generic event display
            if self.config.show_metadata:
                return Text(f"📝 {event_type}: {content}", style=self.config.color_scheme.get('system', 'yellow'))
            return Text(f"ℹ️ {content}", style=self.config.color_scheme.get('info', 'cyan'))
    
    def process_streaming_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a list of streaming events and extract final response"""
        response_content = ""
        tool_results = []
        final_event = None
        
        for event in events:
            event_type = event.get('type', '')
            
            # Collect response content from token events
            if event_type == 'content.token':
                response_content += event.get('content', '')
            
            # Look for complete response content
            elif event_type == 'content.complete':
                node_type = event.get('metadata', {}).get('node', '')
                if node_type in ['AIMessage', 'format_response']:
                    complete_content = event.get('content', '')
                    if complete_content:
                        response_content = complete_content
            
            # Collect tool results
            elif event_type == 'tool_result_msg':
                tool_results.append(event.get('content', ''))
            
            # Track final event
            elif event_type == 'session.end':
                final_event = event
        
        return {
            "response": response_content,
            "tool_results": tool_results,
            "events": events,
            "success": len(events) > 0,
            "session_id": final_event.get('session_id') if final_event else None,
            "timestamp": final_event.get('timestamp') if final_event else None
        }