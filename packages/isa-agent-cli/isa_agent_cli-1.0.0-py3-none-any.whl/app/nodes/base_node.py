"""
Base Node for all LangGraph nodes with dependency injection
"""
from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, Optional, List
from langgraph.config import get_stream_writer
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt, Command

# LangSmith tracing via centralized service
from ..components.tracing_service import traceable_if_enabled

from ..types.agent_state import AgentState
from ..components.mcp_service import MCPService
from ..components.billing_service import track_model_call, track_tool_call
from ..graphs.utils.context_schema import ContextSchema
from ..utils.logger import agent_logger


class BaseNode(ABC):
    """
    Base class for all LangGraph nodes with dependency injection
    
    Features:
    - Dependency injection management (MCP service, session manager, etc.)
    - Unified logging and error handling
    - Streaming updates support
    - Runtime context management
    """
    
    def __init__(self, node_name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize base node

        Args:
            node_name: Node name for logging and streaming updates
            logger: Optional logger instance
        """
        self.node_name = node_name
        self.logger = logger or agent_logger
        
        # Cache dependency services to avoid repeated retrieval
        self._mcp_service_cache = None
    
    def get_runtime_context(self, config: RunnableConfig) -> Dict[str, Any]:
        """
        Extract runtime context from config
        
        Args:
            config: LangGraph RunnableConfig with configurable context
            
        Returns:
            Runtime context dictionary
        """
        return config.get("configurable", {})
    
    def get_user_id(self, config: RunnableConfig) -> str:
        """Get user ID from config context"""
        return config.get("configurable", {}).get("user_id", "")
    
    def get_thread_id(self, config: RunnableConfig) -> str:
        """Get thread ID from config context"""
        return config.get("configurable", {}).get("thread_id", "")
    
    def get_mcp_service(self, config: RunnableConfig) -> Optional[MCPService]:
        """Get MCP service from config context"""
        return config.get("configurable", {}).get("mcp_service")
    
    def get_session_manager(self, config: RunnableConfig) -> Any:
        """Get session manager from config context"""
        return config.get("configurable", {}).get("session_manager")
    
    def get_default_prompts(self, config: RunnableConfig) -> Dict[str, str]:
        """Get default prompts from config context"""
        return config.get("configurable", {}).get("default_prompts", {})
    
    def get_default_tools(self, config: RunnableConfig) -> List[Dict[str, Any]]:
        """Get default tools from config context"""
        return config.get("configurable", {}).get("default_tools", [])
    
    def get_default_resources(self, config: RunnableConfig) -> List[Dict[str, Any]]:
        """Get default resources from config context"""
        return config.get("configurable", {}).get("default_resources", [])
    
    def get_default_prompt(self, config: RunnableConfig, prompt_key: str, fallback: str = "") -> str:
        """
        Get default prompt from config context
        
        Args:
            config: LangGraph RunnableConfig
            prompt_key: Key for the prompt (e.g., 'entry_node_prompt', 'reason_node_prompt')
            fallback: Fallback text if prompt not found
            
        Returns:
            Default prompt text or fallback
        """
        default_prompts = self.get_default_prompts(config)
        return default_prompts.get(prompt_key, fallback)
    
    async def get_initialized_mcp_service(self, config: RunnableConfig) -> Optional[MCPService]:
        """
        Get MCP service from config context with automatic initialization
        
        Args:
            config: LangGraph RunnableConfig
            
        Returns:
            Initialized MCPService instance or None if not available
        """
        mcp_service = self.get_mcp_service(config)
        if not mcp_service:
            return None
        
        # Initialize if needed
        if not mcp_service.session:
            await mcp_service.initialize()
        
        return mcp_service
    
    # ==================== SEARCH OPERATIONS ====================
    
    async def mcp_search_all(self, query: str, config: RunnableConfig, user_id: Optional[str] = None, 
                            filters: Optional[Dict] = None, max_results: int = 10) -> Dict[str, Any]:
        """
        Search across all MCP capabilities (tools, prompts, resources)
        
        Args:
            query: Search query
            config: LangGraph RunnableConfig
            user_id: Optional user ID for access control (defaults to config user_id)
            filters: Optional search filters
            max_results: Maximum number of results
            
        Returns:
            Search results with all capability types
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        if not mcp_service:
            return {"results": [], "result_count": 0}
            
        user_id = user_id or self.get_user_id(config)
        
        try:
            return await mcp_service.search_all(query, user_id, filters, max_results)
        except Exception as e:
            self.logger.error(f"Universal search failed: {e}")
            return {"results": [], "result_count": 0}
    
    async def mcp_search_tools(self, query: str, config: RunnableConfig, user_id: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tools using MCP service
        
        Args:
            query: Search query for tools
            runtime: LangGraph Runtime object
            user_id: Optional user ID for access control (defaults to runtime user_id)
            max_results: Maximum number of results
            
        Returns:
            List of matching tools
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        user_id = user_id or self.get_user_id(config)
        
        try:
            return await mcp_service.search_tools(query, user_id, max_results)
        except Exception as e:
            self.logger.error(f"Tool search failed: {e}")
            return []
    
    async def mcp_search_prompts(self, query: str, config: RunnableConfig, user_id: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for prompts using MCP service
        
        Args:
            query: Search query for prompts
            runtime: LangGraph Runtime object
            user_id: Optional user ID for access control (defaults to runtime user_id)
            max_results: Maximum number of results
            
        Returns:
            List of matching prompts
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        user_id = user_id or self.get_user_id(config)
        
        try:
            return await mcp_service.search_prompts(query, user_id, max_results)
        except Exception as e:
            self.logger.error(f"Prompt search failed: {e}")
            return []
    
    async def mcp_search_resources(self, user_id: str, config: RunnableConfig, query: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for user resources using MCP service
        
        Args:
            user_id: User ID (required for resource access)
            runtime: LangGraph Runtime object
            query: Optional search query (if None, returns all user resources)
            max_results: Maximum number of results
            
        Returns:
            List of matching resources
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        if not mcp_service:
            return []
        
        try:
            return await mcp_service.search_resources(user_id, query, max_results)
        except Exception as e:
            self.logger.error(f"Resource search failed: {e}")
            return []
    
    # ==================== SECURITY LEVEL OPERATIONS ====================
    
    async def mcp_get_tool_security_levels(self, config: RunnableConfig, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get security levels for all available tools
        
        Args:
            config: LangGraph RunnableConfig
            user_id: Optional user ID for access control (defaults to config user_id)
            
        Returns:
            Dict with tools and their security levels
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        if not mcp_service:
            return {"tools": {}, "metadata": {}}
        
        user_id = user_id or self.get_user_id(config)
        
        try:
            return await mcp_service.get_tool_security_levels(user_id)
        except Exception as e:
            self.logger.error(f"Failed to get tool security levels: {e}")
            return {"tools": {}, "metadata": {}}
    
    async def mcp_search_tools_by_security_level(self, security_level: str, config: RunnableConfig, 
                                                query: Optional[str] = None, user_id: Optional[str] = None, 
                                                max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tools by security level
        
        Args:
            security_level: Security level (LOW, MEDIUM, HIGH, CRITICAL)
            config: LangGraph RunnableConfig
            query: Optional search query to filter tools
            user_id: Optional user ID for access control (defaults to config user_id)
            max_results: Maximum number of results
            
        Returns:
            List of tools matching the security level and query
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        if not mcp_service:
            return []
        
        user_id = user_id or self.get_user_id(config)
        
        try:
            return await mcp_service.search_tools_by_security_level(security_level, query, user_id, max_results)
        except Exception as e:
            self.logger.error(f"Security level search failed: {e}")
            return []
    
    async def mcp_get_tool_security_level(self, tool_name: str, config: RunnableConfig, 
                                        user_id: Optional[str] = None) -> Optional[str]:
        """
        Get security level for a specific tool
        
        Args:
            tool_name: Name of the tool
            config: LangGraph RunnableConfig
            user_id: Optional user ID for access control (defaults to config user_id)
            
        Returns:
            Security level string (LOW, MEDIUM, HIGH, CRITICAL) or None if not found
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        if not mcp_service:
            return None
        
        user_id = user_id or self.get_user_id(config)
        
        try:
            return await mcp_service.get_tool_security_level(tool_name, user_id)
        except Exception as e:
            self.logger.error(f"Failed to get tool security level: {e}")
            return None
    
    async def mcp_check_tool_security_authorized(self, tool_name: str, required_level: str, config: RunnableConfig, 
                                               user_id: Optional[str] = None) -> bool:
        """
        Check if a tool meets the required security level
        
        Args:
            tool_name: Name of the tool
            required_level: Required security level (LOW, MEDIUM, HIGH, CRITICAL)
            config: LangGraph RunnableConfig
            user_id: Optional user ID for access control (defaults to config user_id)
            
        Returns:
            True if tool meets or exceeds required security level
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        if not mcp_service:
            return False
        
        user_id = user_id or self.get_user_id(config)
        
        try:
            return await mcp_service.check_tool_security_authorized(tool_name, required_level, user_id)
        except Exception as e:
            self.logger.error(f"Security authorization check failed: {e}")
            return False
    
    # ==================== EXECUTE OPERATIONS ====================
    
    @track_tool_call("MCP")
    @traceable_if_enabled
    async def mcp_call_tool(self, tool_name: str, arguments: Dict[str, Any], config: RunnableConfig) -> str:
        """
        Execute tool using MCP service
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            runtime: LangGraph Runtime object
            
        Returns:
            Tool execution result
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        if not mcp_service:
            return "Error: MCP service not available"
        
        try:
            return await mcp_service.call_tool(tool_name, arguments)
        except Exception as e:
            error_msg = f"Tool execution failed: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    @traceable_if_enabled
    async def mcp_get_prompt(self, prompt_name: str, arguments: Dict[str, Any], config: RunnableConfig) -> Optional[str]:
        """
        Get assembled prompt from MCP service
        
        Args:
            prompt_name: Name of prompt template
            arguments: Prompt arguments for template substitution
            runtime: LangGraph Runtime object
            
        Returns:
            Assembled prompt text or None if failed
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        if not mcp_service:
            return None
        
        try:
            return await mcp_service.get_prompt(prompt_name, arguments)
        except Exception as e:
            self.logger.error(f"Prompt retrieval failed: {e}")
            return None
    
    @traceable_if_enabled
    async def mcp_get_resource(self, uri: str, config: RunnableConfig) -> Optional[Dict[str, Any]]:
        """
        Get resource content from MCP service
        
        Args:
            uri: Resource URI to read
            runtime: LangGraph Runtime object
            
        Returns:
            Resource data with contents and metadata, or None if failed
        """
        mcp_service = await self.get_initialized_mcp_service(config)
        if not mcp_service:
            return None
        
        try:
            return await mcp_service.get_resource(uri)
        except Exception as e:
            self.logger.error(f"Resource retrieval failed: {e}")
            return None
    
    def stream_custom(self, data: Dict[str, Any]) -> None:
        """
        Unified streaming method for both LLM tokens and tool progress
        
        Support two types of streaming:
        
        1. LLM Token Streaming (based on LangGraph example):
           writer({"custom_llm_chunk": chunk})
           
        2. Tool Progress Streaming (based on LangGraph example):
           writer({"data": "Retrieved 0/100 records", "type": "progress"})
        
        Args:
            data: Streaming data - can be:
                  - {"custom_llm_chunk": "token"} for LLM tokens
                  - {"data": "progress info", "type": "progress"} for tool progress
                  - Any other custom streaming data
        """
        writer = get_stream_writer()
        if writer:
            writer(data)
    
    @track_model_call("BaseNode")
    @traceable_if_enabled
    async def call_model(self, messages, tools=None, model=None, provider=None, stream_tokens=True, output_format=None):
        """
        Call model with optional token streaming and output format

        Args:
            messages: List of LangChain messages
            tools: Optional tools for model
            model: Optional model override (e.g., "gpt-5", "gpt-oss-120b")
            provider: Optional provider override (e.g., "yyds", "cerebras", "openai")
            stream_tokens: Whether to stream tokens via stream_custom (default: True)
            output_format: "json" for structured JSON output, None for normal streaming

        Returns:
            Final AIMessage response
        """
        import time
        call_start = time.time()

        from ..components.model_service import get_model_service

        service_start = time.time()
        model_service = await get_model_service()
        service_duration = int((time.time() - service_start) * 1000)

        print(f"[TIMING] base_node_get_model_service | node={self.node_name} | duration_ms={service_duration}", flush=True)
        self.logger.info(
            f"base_node_get_model_service | "
            f"node={self.node_name} | "
            f"duration_ms={service_duration}"
        )
        
        # Handle JSON output mode
        print(f"[DEBUG] BaseNode call_model | output_format={output_format} | stream_tokens={stream_tokens}", flush=True)
        if output_format == "json":
            print(f"[DEBUG] BaseNode entering JSON mode", flush=True)
            try:
                # Use ISA Model Client for JSON output
                from isa_model.client import ISAModelClient
                client = ISAModelClient()
                
                # Convert messages to prompt string for ISA client
                prompt = self._messages_to_prompt(messages)
                
                result = await client.invoke(
                    input_data=prompt,
                    task="chat",
                    service_type="text",
                    stream=False,  # Disable streaming for JSON
                    response_format={"type": "json_object"}  # Enable JSON mode
                )

                if result.get("success"):
                    from langchain_core.messages import AIMessage
                    # result["result"] is either a string or AIMessage
                    content = result["result"]
                    if isinstance(content, AIMessage):
                        return content
                    else:
                        return AIMessage(content=str(content))
                else:
                    raise Exception(f"ISA Model call failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.logger.error(f"JSON model call failed: {e}")
                from langchain_core.messages import AIMessage
                return AIMessage(content=f"JSON output error: {str(e)}")
        
        # Normal streaming mode (existing logic)
        token_callback = None
        first_token_time = None

        if stream_tokens:
            print(f"[DEBUG] base_node stream_tokens=True | node={self.node_name} | setting up token_callback", flush=True)

            def token_callback(data):
                nonlocal first_token_time
                if 'token' in data:
                    if first_token_time is None:
                        first_token_time = time.time()
                        ttft = int((first_token_time - call_start) * 1000)
                        with open('/tmp/node_timing.log', 'a') as f:
                            f.write(f"[TIMING] base_node_first_token | node={self.node_name} | time_to_first_token_ms={ttft}\n")
                        print(f"[TIMING] base_node_first_token | node={self.node_name} | time_to_first_token_ms={ttft}", flush=True)
                        self.logger.info(
                            f"base_node_first_token | "
                            f"node={self.node_name} | "
                            f"time_to_first_token_ms={ttft}"
                        )

                    # Different chunk types based on node
                    if self.node_name == "ReasonNode":
                        self.stream_custom({"thinking_chunk": data['token']})
                    elif self.node_name == "ResponseNode":
                        self.stream_custom({"response_chunk": data['token']})
                    else:
                        # Fallback for other nodes
                        self.stream_custom({"custom_llm_chunk": data['token']})

        try:
            stream_start = time.time()
            with open('/tmp/node_timing.log', 'a') as f:
                f.write(f"[TIMING] base_node_call_start | node={self.node_name} | stream_tokens={stream_tokens} | tools_count={len(tools) if tools else 0}\n")
            print(f"[TIMING] base_node_call_start | node={self.node_name} | stream_tokens={stream_tokens} | tools_count={len(tools) if tools else 0}", flush=True)
            self.logger.info(
                f"base_node_call_start | "
                f"node={self.node_name} | "
                f"stream_tokens={stream_tokens} | "
                f"tools_count={len(tools) if tools else 0}"
            )

            # Choose between streaming and non-streaming based on stream_tokens
            if stream_tokens:
                # Streaming mode - use stream_tokens with token callback
                response, _ = await model_service.stream_tokens(
                    messages=messages,
                    token_callback=token_callback,
                    tools=tools,
                    model=model,
                    provider=provider,
                    timeout=120.0
                )
            else:
                # Non-streaming mode - use call_model (fixes gpt-5 org verification issue)
                response, _ = await model_service.call_model(
                    messages=messages,
                    tools=tools,
                    model=model,
                    provider=provider,
                    timeout=120.0
                )

            stream_duration = int((time.time() - stream_start) * 1000)
            total_duration = int((time.time() - call_start) * 1000)

            print(f"[TIMING] base_node_stream_complete | node={self.node_name} | stream_duration_ms={stream_duration} | total_duration_ms={total_duration}", flush=True)
            self.logger.info(
                f"base_node_stream_complete | "
                f"node={self.node_name} | "
                f"stream_duration_ms={stream_duration} | "
                f"total_duration_ms={total_duration}"
            )

            return response
        except Exception as e:
            self.logger.error(f"Model call failed: {e}")
            from langchain_core.messages import AIMessage
            return AIMessage(content=f"Model error: {str(e)}")
    
    def _messages_to_prompt(self, messages) -> str:
        """
        Convert LangChain messages to a prompt string for ISA client
        
        Args:
            messages: List of LangChain messages
            
        Returns:
            Combined prompt string
        """
        prompt_parts = []
        
        for msg in messages:
            content = getattr(msg, 'content', str(msg))
            msg_type = type(msg).__name__
            
            if msg_type == 'SystemMessage':
                prompt_parts.append(f"System: {content}")
            elif msg_type == 'HumanMessage':
                prompt_parts.append(f"Human: {content}")
            elif msg_type == 'AIMessage':
                prompt_parts.append(f"Assistant: {content}")
            elif msg_type == 'ToolMessage':
                prompt_parts.append(f"Tool Result: {content}")
            else:
                prompt_parts.append(f"{msg_type}: {content}")
        
        return "\n\n".join(prompt_parts)
    
    def stream_tool(self, tool_name: str, progress_info: str):
        """
        Stream tool progress
        
        Args:
            tool_name: Name of tool being executed
            progress_info: Progress information
        """
        self.stream_custom({
            "data": f"[{tool_name}] {progress_info}",
            "type": "progress"
        })
    
    
    @abstractmethod
    async def _execute_logic(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """
        Core execution logic to be implemented by subclasses
        
        Args:
            state: Current state
            config: LangGraph RunnableConfig with context in configurable
            
        Returns:
            Updated state
        """
        pass
    
    async def execute(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """
        Unified execution entry point with config context support
        
        Args:
            state: Current state
            config: LangGraph RunnableConfig with context in configurable
            
        Returns:
            Updated state
        """
        try:
            # Simple logging - no streaming overhead
            self.logger.info(f"{self.node_name} starting")
            
            # Call subclass core logic with config context
            updated_state = await self._execute_logic(state, config)
            
            self.logger.info(f"{self.node_name} completed")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"{self.node_name} error: {e}")
            raise