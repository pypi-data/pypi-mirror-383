#!/usr/bin/env python3
"""
Response Node - Final response generation with LLM streaming

Clean response node that:
1. Gets default_response_prompt from MCP
2. Summarizes conversation messages
3. Calls model with token streaming via base_node
4. Adds final AIMessage to state
"""

import logging
import time
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from ..types.agent_state import AgentState
from .base_node import BaseNode
from ..utils.logger import agent_logger

logger = agent_logger  # Use centralized logger for Loki integration


class ResponseNode(BaseNode):
    """Professional response generation node with MCP integration"""
    
    def __init__(self):
        super().__init__("ResponseNode")
    
    async def _execute_logic(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """
        Generate final response using MCP prompt and LLM streaming

        Args:
            state: Current agent state with conversation messages
            config: Runtime config with MCP service context

        Returns:
            Updated state with final AIMessage and end action
        """
        messages = state.get("messages", [])
        # Get session_id from config.configurable.thread_id (not from state!)
        session_id = config.get("configurable", {}).get("thread_id", "unknown") if config else "unknown"

        # Log incoming state for debugging
        message_types = [type(msg).__name__ for msg in messages]
        output_format_from_config = config.get("configurable", {}).get("output_format") if config else None
        state_log = (
            f"[PHASE:NODE_RESPONSE] state_received | "
            f"session_id={session_id} | "
            f"messages_count={len(messages)} | "
            f"message_types={message_types} | "
            f"output_format_from_config={output_format_from_config}"
        )
        print(f"[RESPONSE_NODE] {state_log}", flush=True)
        self.logger.info(state_log)

        if not messages:
            self.logger.warning(
                f"[PHASE:NODE_RESPONSE] response_warning | "
                f"session_id={session_id} | "
                f"reason=no_messages"
            )
            return self._create_error_response(state, "No conversation messages available")
        
        # 1. Create conversation summary
        conversation_summary = self._build_conversation_summary(messages)
        
        # 2. Get response prompt from MCP with conversation summary
        # Check if JSON output is requested via config
        output_format = config.get("configurable", {}).get("output_format") if config else None
        
        if output_format == "json":
            # Use JSON-specific prompt arguments
            prompt_args = {
                "conversation_summary": conversation_summary,
                "output_format": "json"
            }
            # Try to get JSON-specific prompt, fallback to default if not available
            response_prompt = await self.mcp_get_prompt("default_response_json_prompt", prompt_args, config)
            
            if not response_prompt:
                # Fallback: Add JSON instruction to default prompt
                default_prompt = await self.mcp_get_prompt("default_response_prompt", {"conversation_summary": conversation_summary}, config)
                if default_prompt:
                    response_prompt = f"{default_prompt}\n\nIMPORTANT: Please provide your response in valid JSON format. Structure your response as a JSON object with relevant fields."
                else:
                    response_prompt = f"Please provide a helpful response based on this conversation in valid JSON format:\n\n{conversation_summary}\n\nResponse should be a properly formatted JSON object."
        else:
            # Normal text response
            prompt_args = {"conversation_summary": conversation_summary}
            response_prompt = await self.mcp_get_prompt("default_response_prompt", prompt_args, config)
            
            if not response_prompt:
                # Fallback to simple response prompt
                response_prompt = f"Please provide a helpful response based on this conversation:\n\n{conversation_summary}"
        
        try:
            # 3. Check output format and call model accordingly
            response_start = time.time()
            # Get output_format from config (more reliable than state)
            output_format = config.get("configurable", {}).get("output_format") if config else None

            # Log LLM input for debugging
            conversation_preview = conversation_summary[:300] if conversation_summary else 'N/A'
            stream_tokens_flag = (output_format != "json")

            self.logger.info(
                f"[PHASE:NODE_RESPONSE] llm_input | "
                f"session_id={session_id} | "
                f"prompt_name=default_response_prompt | "
                f"conversation_summary_len={len(conversation_summary)} | "
                f"conversation_preview='{conversation_preview}' | "
                f"output_format={output_format or 'text'} | "
                f"stream_tokens={stream_tokens_flag}"
            )
            
            # Log complete LLM input for session context debugging
            self.logger.info(
                f"[PHASE:NODE_RESPONSE] llm_complete_input | "
                f"session_id={session_id} | "
                f"response_prompt={response_prompt} | "
                f"conversation_summary={conversation_summary}"
            )

            print(f"[DEBUG] ResponseNode llm_input | session_id={session_id} | stream_tokens={stream_tokens_flag} | output_format={output_format} | state_keys={list(state.keys())}", flush=True)

            # Use BaseNode's call_model
            if output_format == "json":
                # For JSON output, use OpenAI gpt-4.1-nano with response_format support
                response = await self.call_model(
                    messages=[HumanMessage(content=response_prompt)],
                    stream_tokens=False,  # Disable streaming for JSON
                    output_format="json",
                    provider="openai",
                    model="gpt-4.1-nano"
                )
            else:
                # For normal text output, use configured response model (gpt-5-nano by default)
                from ..config import settings
                response = await self.call_model(
                    messages=[HumanMessage(content=response_prompt)],
                    stream_tokens=stream_tokens_flag,
                    model=settings.response_model,
                    provider=settings.response_model_provider
                )

            print(f"[DEBUG] ResponseNode llm_output | session_id={session_id} | response_type={type(response).__name__} | has_content={hasattr(response, 'content')}", flush=True)

            response_duration = int((time.time() - response_start) * 1000)
            response_length = len(response.content) if hasattr(response, 'content') else 0
            response_preview = response.content[:300] if hasattr(response, 'content') else 'N/A'

            self.logger.info(
                f"[PHASE:NODE_RESPONSE] llm_output | "
                f"session_id={session_id} | "
                f"node=response | "
                f"duration_ms={response_duration} | "
                f"response_length={response_length} | "
                f"response_preview='{response_preview}' | "
                f"output_format={output_format or 'text'}"
            )

            # 5. Add final response to conversation (add_messages reducer handles appending)
            # Note: Response prompt already used in model call, just add the final response
            return {
                "messages": [response],
                "next_action": "end"
            }

        except Exception as e:
            self.logger.error(
                f"response_error | "
                f"session_id={session_id} | "
                f"node=response | "
                f"error={type(e).__name__} | "
                f"message={str(e)[:200]}",
                exc_info=True
            )
            return self._create_error_response(state, f"Response error: {str(e)}")
    
    def _build_conversation_summary(self, messages) -> str:
        """
        Build conversation summary with CLEAR instruction for ResponseNode
        
        ResponseNode's role: Format the reasoning layer's complete analysis into 
        a user-friendly final response. NOT to re-analyze or re-answer.

        Args:
            messages: List of conversation messages

        Returns:
            Formatted instruction with reasoning result for ResponseNode to format
        """
        # Strategy: Keep first HumanMessage and last AIMessage only
        # This gives ResponseNode the user's question and ReasonNode's final answer
        first_human = None
        last_ai = None

        for msg in messages:
            msg_type = type(msg).__name__

            if msg_type == 'HumanMessage' and first_human is None:
                first_human = getattr(msg, 'content', str(msg))
            elif msg_type == 'AIMessage':
                last_ai = getattr(msg, 'content', str(msg))

        # Truncate user query if too long
        if first_human and len(first_human) > 200:
            first_human = first_human[:200] + "..."
        
        # Keep reasoning result but limit to prevent token overflow
        if last_ai and len(last_ai) > 2000:
            last_ai = last_ai[:2000] + "..."

        # 🔑 KEY: Explicitly tell ResponseNode its job is formatting, not re-analyzing
        summary = f"""## RESPONSE FORMATTING TASK

The reasoning layer has completed its analysis. Your job is to format the final answer for the user.

### User's Original Question:
{first_human or "N/A"}

### Reasoning Layer's Complete Analysis:
{last_ai or "No analysis available"}

### YOUR TASK AS RESPONSE FORMATTER:
Take the reasoning analysis above and present it as a polished, user-friendly response:
- Extract key information and structure it clearly
- If web search results: present ALL findings in organized format
- If code/technical info: use proper formatting and code blocks
- If simple answer: present naturally and conversationally
- Maintain all factual content but improve readability and presentation

DO NOT re-analyze or re-answer the question. Your role is presentation, not reasoning.
"""
        
        return summary
    
    def _create_error_response(self, state: AgentState, error_message: str) -> AgentState:
        """Create error response and update state"""
        _ = state  # State parameter kept for API consistency
        error_response = AIMessage(content=f"I apologize, but I encountered an error: {error_message}")
        
        # Return state update using add_messages reducer
        return {
            "messages": [error_response],
            "next_action": "end"
        }