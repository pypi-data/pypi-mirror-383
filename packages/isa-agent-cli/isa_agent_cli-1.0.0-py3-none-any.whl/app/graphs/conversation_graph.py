#!/usr/bin/env python3
"""
Conversation Graph Implementation

A simple, lightweight graph for conversational interactions without tools.
Optimized for fast response times and natural dialogue.
"""

import logging
from typing import Dict, Optional, List

from langgraph.graph import START, END
from .base_graph import BaseGraph

# Import nodes
from ..nodes.reason_node import ReasonNode
from ..nodes.response_node import ResponseNode

logger = logging.getLogger(__name__)


class ConversationGraph(BaseGraph):
    """
    Simple conversation graph without tools for fast, natural dialogue
    """
    
    def get_graph_name(self) -> str:
        return "conversation_graph"
    
    def get_graph_type(self) -> str:
        return "conversation"
    
    def get_description(self) -> str:
        return "Lightweight graph for natural conversation without tool usage"
    
    def _initialize_nodes(self):
        """Initialize minimal nodes for conversation"""
        # Minimal configuration for fast response
        self.max_graph_iterations = self.config.get("max_graph_iterations", 10)
        self.max_agent_loops = 0  # No agent loops
        self.max_tool_loops = 0   # No tool loops
        
        # Only essential nodes
        self.nodes["reason"] = ReasonNode()
        self.nodes["response"] = ResponseNode()
        
        logger.info(f"{self.graph_name}: Initialized minimal conversation nodes")
    
    def _build_workflow(self, workflow):
        """Build the simple conversation workflow"""
        
        # Add nodes
        workflow.add_node("converse", self._converse)
        workflow.add_node("format", self.nodes["response"].execute)
        
        # Simple linear flow
        workflow.add_edge(START, "converse")
        workflow.add_edge("converse", "format")
        workflow.add_edge("format", END)
        
        return workflow
    
    def _converse(self, state):
        """
        Simple conversation node that directly processes and responds
        """
        user_input = state.get("user_input", "")
        messages = state.get("messages", [])
        
        # Direct LLM conversation without tools
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Add user message
        if user_input:
            messages.append(HumanMessage(content=user_input))
        
        # Generate response (simplified - would use actual LLM)
        response = f"I understand you're saying: '{user_input}'. Let me help you with that."
        messages.append(AIMessage(content=response))
        
        state["messages"] = messages
        state["next_action"] = "end"
        
        logger.info("Conversation response generated")
        return state
    
    def get_node_list(self) -> List[str]:
        return ["converse", "format"]
    
    def get_features(self) -> List[str]:
        return [
            "fast_response",
            "natural_dialogue",
            "minimal_overhead",
            "no_tool_usage",
            "context_aware",
            "stateless_option"
        ]