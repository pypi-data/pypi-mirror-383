"""
MCP Service - Production-grade interface for MCP Search API

Provides high-performance, cached access to MCP capabilities including:
- Search across tools, prompts, and resources with semantic matching
- Tool execution with comprehensive error handling and billing tracking
- Resource and prompt management with intelligent caching
- Connection pooling and HTTP/2 support for optimal performance

Uses the latest MCP Search API (v2024) with user access control and
implements enterprise-grade caching, logging, and error handling.
"""

import json
import requests
import asyncio
import logging
from time import time
from typing import Dict, List, Any, Optional

from ..config import settings


class MCPService:
    """
    Production-grade MCP service with enterprise features
    
    Features:
    - High-performance caching with configurable TTL
    - Connection pooling and HTTP/2 support
    - Comprehensive error handling and logging
    - Metrics and monitoring capabilities
    - Thread-safe operations with async locks
    """
    
    def __init__(self, mcp_url: str, cache_ttl: int = 300, logger: Optional[logging.Logger] = None):
        """
        Initialize MCP service with production settings
        
        Args:
            mcp_url: Base MCP server URL (e.g., 'http://localhost:8081' or 'http://localhost:8081/mcp')
            cache_ttl: Cache time-to-live in seconds (default 5 minutes)
            logger: Optional logger instance (creates default if None)
        """
        # Normalize the URL: remove /mcp suffix if present, use 127.0.0.1 instead of localhost
        base_url = mcp_url.rstrip('/')
        if base_url.endswith('/mcp'):
            base_url = base_url[:-4]  # Remove '/mcp' suffix only (not from hostname!)
        base_url = base_url.replace('localhost', '127.0.0.1')  # Fix httpx IPv6 issue
        
        self.base_url = base_url  # Base URL without /mcp (for health, capabilities, search, security)
        self.mcp_url = f"{base_url}/mcp"  # JSON-RPC endpoints need /mcp prefix
        self.session: Optional[requests.Session] = None
        self.session_id = 1
        
        # Setup logging
        self.logger = logger or logging.getLogger(__name__)
        
        # For backward compatibility
        self.search_base_url = self.base_url
        
        # Performance optimizations
        self.cache_ttl = cache_ttl
        self._capabilities_cache = None
        self._capabilities_cache_time = 0
        self._search_cache = {}  # query -> (result, timestamp)
        self._cache_lock = asyncio.Lock()
        
        # Metrics
        self._metrics = {
            'requests_total': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'tool_executions': 0
        }
    
    # ==================== LIFECYCLE ====================
    
    async def initialize(self):
        """Initialize HTTP session with production-grade connection settings"""
        try:
            self.session = requests.Session()
            self.session.headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "User-Agent": "MCPService/1.0"
            })
            
            # Configure connection pooling
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=20,
                pool_maxsize=20,
                max_retries=3,
                pool_block=False
            )
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
            
            self.logger.info(
                "MCP service initialized",
                extra={
                    "base_url": self.base_url,
                    "mcp_url": self.mcp_url,
                    "cache_ttl": self.cache_ttl,
                    "connection_pooling": True
                }
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP service: {e}")
            raise
    
    async def close(self):
        """Close HTTP session and cleanup resources"""
        try:
            if self.session:
                self.session.close()
                self.session = None
            
            # Clear caches
            async with self._cache_lock:
                self._capabilities_cache = None
                self._search_cache.clear()
            
            self.logger.info(
                "MCP service closed",
                extra={"metrics": self._metrics}
            )
        except Exception as e:
            self.logger.error(f"Error closing MCP service: {e}")
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached data is still valid"""
        return time() - timestamp < self.cache_ttl
    
    async def _cleanup_search_cache(self):
        """Remove expired entries from search cache"""
        current_time = time()
        expired_keys = [
            key for key, (_, timestamp) in self._search_cache.items()
            if current_time - timestamp >= self.cache_ttl
        ]
        for key in expired_keys:
            del self._search_cache[key]
    
    # ==================== CORE JSON-RPC ====================
    
    async def _request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """Make JSON-RPC request to MCP server"""
        if not self.session:
            raise Exception("Session not initialized - call initialize() first")
        
        data = {"jsonrpc": "2.0", "id": self.session_id, "method": method}
        if params:
            data["params"] = params
        self.session_id += 1
        
        # JSON-RPC requests go to specific endpoints under /mcp/
        endpoint_map = {
            "tools/call": f"{self.mcp_url}/tools/call",
            "prompts/get": f"{self.mcp_url}/prompts/get", 
            "resources/read": f"{self.mcp_url}/resources/read"
        }
        url = endpoint_map.get(method, self.mcp_url)
        response = self.session.post(url, json=data, timeout=30.0)
        
        try:
            return response.json()
        except:
            # Handle SSE responses
            text = response.text
            if "data: " in text:
                for line in text.split('\n'):
                    if line.startswith("data: "):
                        return json.loads(line[6:])
            raise Exception(f"Invalid response: {response.status_code}")
    
    async def _search_request(self, endpoint: str, payload: Optional[Dict] = None, 
                             params: Optional[Dict] = None) -> Dict:
        """Make request to Search API endpoints with comprehensive error handling"""
        if not self.session:
            raise ConnectionError("Session not initialized - call initialize() first")
        
        # Search API endpoints don't use /mcp prefix
        url = f"{self.base_url}{endpoint}"
        self._metrics['requests_total'] += 1
        
        try:
            if payload:
                # POST request
                response = self.session.post(url, json=payload, timeout=10.0)
            else:
                # GET request
                response = self.session.get(url, params=params or {}, timeout=10.0)
            
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            self._metrics['errors'] += 1
            error_msg = f"HTTP {e.response.status_code} error for {endpoint}"
            self.logger.error(
                error_msg,
                extra={
                    "endpoint": endpoint,
                    "status_code": e.response.status_code,
                    "response_text": e.response.text[:500]
                }
            )
            raise ConnectionError(error_msg) from e
            
        except requests.exceptions.RequestException as e:
            self._metrics['errors'] += 1
            error_msg = f"Network error for {endpoint}: {str(e)}"
            self.logger.error(
                error_msg,
                extra={"endpoint": endpoint, "error_type": type(e).__name__}
            )
            raise ConnectionError(error_msg) from e
            
        except json.JSONDecodeError as e:
            self._metrics['errors'] += 1
            error_msg = f"Invalid JSON response from {endpoint}"
            self.logger.error(error_msg, extra={"endpoint": endpoint})
            raise ValueError(error_msg) from e
    
    # ==================== FORMAT CONVERSION ====================
    
    def convert_search_results_to_tools(self, search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert MCP search results to standard tools format
        
        Args:
            search_results: MCP search results with metadata structure
            
        Returns:
            List of tools in standard format with inputSchema
        """
        tools = []
        
        for result in search_results.get('results', []):
            if result.get('type') == 'tool':
                tool = {
                    "name": result.get('name', ''),
                    "description": result.get('description', '').strip(),
                    "inputSchema": result.get('metadata', {}).get('input_schema', {})
                }
                tools.append(tool)
        
        return tools
    
    # ==================== SEARCH OPERATIONS ====================
    
    async def search_all(self, query: str, user_id: Optional[str] = None, 
                        filters: Optional[Dict] = None, max_results: int = 10) -> Dict[str, Any]:
        """
        Universal search across all capability types with intelligent caching
        
        Args:
            query: Natural language search query
            user_id: Optional user ID for access control
            filters: Optional search filters (types, keywords, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            Search results with metadata and result count
        """
        # Create cache key
        cache_key = f"{query}:{user_id}:{filters}:{max_results}"
        
        # Check cache first
        async with self._cache_lock:
            if cache_key in self._search_cache:
                result, timestamp = self._search_cache[cache_key]
                if self._is_cache_valid(timestamp):
                    self._metrics['cache_hits'] += 1
                    self.logger.debug(
                        "Search cache hit",
                        extra={"query": query, "user_id": user_id}
                    )
                    return result
            
            # Cleanup expired cache entries periodically
            await self._cleanup_search_cache()
        
        self._metrics['cache_misses'] += 1
        
        payload = {
            "query": query,
            "max_results": max_results
        }
        
        if user_id:
            payload["user_id"] = user_id
        if filters:
            payload["filters"] = filters
        
        try:
            result = await self._search_request("/search", payload)
            count = result.get('result_count', 0)
            
            self.logger.info(
                "Search completed",
                extra={
                    "query": query,
                    "user_id": user_id,
                    "result_count": count,
                    "max_results": max_results
                }
            )
            
            # Cache the result
            async with self._cache_lock:
                self._search_cache[cache_key] = (result, time())
            
            return result
            
        except Exception as e:
            self._metrics['errors'] += 1
            self.logger.error(
                "Search failed",
                extra={
                    "query": query,
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            return {
                "status": "error", 
                "message": str(e), 
                "results": [], 
                "result_count": 0
            }
    
    async def search_tools(self, query: str, user_id: Optional[str] = None, 
                          max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for tools matching query and convert to standard format"""
        filters = {"types": ["tool"]}
        result = await self.search_all(query, user_id, filters, max_results)
        return self.convert_search_results_to_tools(result)
    
    async def search_prompts(self, query: str, user_id: Optional[str] = None, 
                            max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for prompts matching query"""
        filters = {"types": ["prompt"]}
        result = await self.search_all(query, user_id, filters, max_results)
        return result.get("results", [])
    
    async def search_resources(self, user_id: str, query: Optional[str] = None, 
                              max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for user resources, optionally filtered by query"""
        filters = {"types": ["resource"]}
        
        if query:
            result = await self.search_all(query, user_id, filters, max_results)
            return result.get("results", [])
        else:
            # Get all user resources via list_all
            all_capabilities = await self.list_all(user_id)
            return all_capabilities.get("resources", [])
    
    # ==================== DEFAULT OPERATIONS ====================
    
    async def get_all_defaults(self, max_results: int = 20) -> Dict[str, Any]:
        """
        Get all default capabilities (tools, prompts, resources)
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            All default capabilities organized by type
        """
        try:
            result = await self.search_all("default", filters=None, max_results=max_results)
            
            # Organize results by type
            organized_results = {
                "tools": [],
                "prompts": [], 
                "resources": [],
                "total_count": result.get("result_count", 0)
            }
            
            for item in result.get("results", []):
                item_type = item.get("type", "unknown")
                if item_type in organized_results:
                    organized_results[item_type].append(item)
            
            self.logger.info(
                "Default capabilities retrieved",
                extra={
                    "tools_count": len(organized_results["tools"]),
                    "prompts_count": len(organized_results["prompts"]),
                    "resources_count": len(organized_results["resources"]),
                    "total_count": organized_results["total_count"]
                }
            )
            
            return organized_results
            
        except Exception as e:
            self.logger.error(f"Failed to get default capabilities: {e}")
            return {
                "tools": [],
                "prompts": [],
                "resources": [],
                "total_count": 0,
                "error": str(e)
            }
    
    async def get_default_tools(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Get all default tools in standard format
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of default tools with inputSchema format
        """
        try:
            filters = {"types": ["tool"]}
            result = await self.search_all("default", filters=filters, max_results=max_results)
            tools = self.convert_search_results_to_tools(result)
            
            self.logger.info(
                "Default tools retrieved",
                extra={"tools_count": len(tools)}
            )
            
            return tools
            
        except Exception as e:
            self.logger.error(f"Failed to get default tools: {e}")
            return []
    
    async def get_default_prompts(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Get all default prompts
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of default prompts
        """
        try:
            filters = {"types": ["prompt"]}
            result = await self.search_all("default", filters=filters, max_results=max_results)
            prompts = result.get("results", [])
            
            self.logger.info(
                "Default prompts retrieved", 
                extra={"prompts_count": len(prompts)}
            )
            
            return prompts
            
        except Exception as e:
            self.logger.error(f"Failed to get default prompts: {e}")
            return []
    
    async def get_default_resources(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Get all default resources
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of default resources
        """
        try:
            filters = {"types": ["resource"]}
            result = await self.search_all("default", filters=filters, max_results=max_results)
            resources = result.get("results", [])
            
            self.logger.info(
                "Default resources retrieved",
                extra={"resources_count": len(resources)}
            )
            
            return resources
            
        except Exception as e:
            self.logger.error(f"Failed to get default resources: {e}")
            return []
    

    # ==================== LIST OPERATIONS ====================
    
    async def list_all(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all available capabilities organized by type with intelligent caching
        
        Args:
            user_id: Optional user ID for resource filtering
            
        Returns:
            Complete capabilities structure with tools, prompts, and resources
        """
        # Check capabilities cache
        async with self._cache_lock:
            if (self._capabilities_cache is not None and 
                self._is_cache_valid(self._capabilities_cache_time)):
                self._metrics['cache_hits'] += 1
                self.logger.debug(
                    "Capabilities cache hit",
                    extra={"user_id": user_id}
                )
                return self._capabilities_cache
        
        self._metrics['cache_misses'] += 1
        
        params = {}
        if user_id:
            params["user_id"] = user_id
        
        try:
            result = await self._search_request("/capabilities", params=params)
            
            # Calculate total capabilities for logging
            capabilities = result.get('capabilities', {})
            total = (
                capabilities.get('tools', {}).get('count', 0) +
                capabilities.get('prompts', {}).get('count', 0) +
                capabilities.get('resources', {}).get('count', 0)
            )
            
            self.logger.info(
                "Capabilities retrieved",
                extra={
                    "user_id": user_id,
                    "total_capabilities": total,
                    "tools_count": capabilities.get('tools', {}).get('count', 0),
                    "prompts_count": capabilities.get('prompts', {}).get('count', 0),
                    "resources_count": capabilities.get('resources', {}).get('count', 0)
                }
            )
            
            # Cache the result
            async with self._cache_lock:
                self._capabilities_cache = result
                self._capabilities_cache_time = time()
            
            return result
            
        except Exception as e:
            self._metrics['errors'] += 1
            self.logger.error(
                "Failed to retrieve capabilities",
                extra={"user_id": user_id, "error": str(e)}
            )
            return {
                "capabilities": {
                    "tools": {"available": [], "count": 0},
                    "prompts": {"available": [], "count": 0},
                    "resources": {"available": [], "count": 0}
                },
                "metadata": {}
            }
    
    async def list_tools(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available tools"""
        all_capabilities = await self.list_all(user_id)
        return all_capabilities.get("capabilities", {}).get("tools", {}).get("available", [])
    
    async def list_prompts(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available prompts"""
        all_capabilities = await self.list_all(user_id)
        return all_capabilities.get("capabilities", {}).get("prompts", {}).get("available", [])
    
    async def list_resources(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available resources"""
        all_capabilities = await self.list_all(user_id)
        return all_capabilities.get("capabilities", {}).get("resources", {}).get("available", [])
    
    async def get_all_lists(self, user_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Optimized method to get all lists in one API call"""
        all_capabilities = await self.list_all(user_id)
        capabilities = all_capabilities.get("capabilities", {})
        
        return {
            "tools": capabilities.get("tools", {}).get("available", []),
            "prompts": capabilities.get("prompts", {}).get("available", []),
            "resources": capabilities.get("resources", {}).get("available", [])
        }
    
    # ==================== EXECUTION OPERATIONS ====================
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute MCP tool with comprehensive logging and error handling
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments dictionary
            
        Returns:
            Tool execution result as string
            
        Raises:
            ConnectionError: If session not initialized or network issues
            ValueError: If invalid response received
        """
        self._metrics['tool_executions'] += 1
        
        self.logger.info(
            "Tool execution started",
            extra={
                "tool_name": tool_name,
                "arguments": arguments
            }
        )
        
        try:
            result = await self._request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            if "result" in result:
                content = result["result"].get("content", [])
                if content and len(content) > 0:
                    tool_result = content[0].get("text", "No result")
                    
                    # Check for JSON response with billing info
                    try:
                        parsed_result = json.loads(tool_result)
                        if isinstance(parsed_result, dict):
                            # Log billing information if present
                            billing_info = {}
                            if "billing" in parsed_result:
                                billing_info = parsed_result["billing"]
                                cost = billing_info.get('total_cost_usd', 0)
                            elif "cost_usd" in parsed_result:
                                cost = parsed_result.get('cost_usd', 0)
                                billing_info = {"total_cost_usd": cost}
                            
                            if billing_info:
                                self.logger.info(
                                    "Tool execution completed with billing",
                                    extra={
                                        "tool_name": tool_name,
                                        "billing": billing_info,
                                        "result_length": len(tool_result)
                                    }
                                )
                            else:
                                self.logger.info(
                                    "Tool execution completed",
                                    extra={
                                        "tool_name": tool_name,
                                        "result_length": len(tool_result)
                                    }
                                )
                            
                            return tool_result
                        else:
                            self.logger.info(
                                "Tool execution completed",
                                extra={
                                    "tool_name": tool_name,
                                    "result_type": "non-dict-json",
                                    "result_length": len(tool_result)
                                }
                            )
                            return tool_result
                            
                    except json.JSONDecodeError:
                        # Plain text result
                        self.logger.info(
                            "Tool execution completed",
                            extra={
                                "tool_name": tool_name,
                                "result_type": "text",
                                "result_length": len(tool_result)
                            }
                        )
                        return tool_result
                        
            elif "error" in result:
                error_msg = result['error']['message']
                self.logger.error(
                    "Tool execution failed",
                    extra={
                        "tool_name": tool_name,
                        "error_message": error_msg
                    }
                )
                return f"Error: {error_msg}"
            
            self.logger.warning(
                "Tool execution returned unexpected response",
                extra={
                    "tool_name": tool_name,
                    "response": str(result)[:200]
                }
            )
            return f"Unexpected response: {result}"
            
        except Exception as e:
            self._metrics['errors'] += 1
            error_msg = f"Tool execution failed: {str(e)}"
            self.logger.error(
                "Tool execution exception",
                extra={
                    "tool_name": tool_name,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return error_msg
    
    async def get_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """
        Get assembled prompt from MCP server using correct endpoint
        
        Args:
            prompt_name: Name of prompt template
            arguments: Prompt arguments for template substitution
            
        Returns:
            Assembled prompt text or None if failed
        """
        self.logger.info(
            "Prompt retrieval started",
            extra={"prompt_name": prompt_name, "arguments": arguments}
        )
        
        try:
            # Use dedicated prompts/get endpoint instead of JSON-RPC
            payload = {
                "jsonrpc": "2.0",
                "id": self.session_id,
                "method": "prompts/get",
                "params": {
                    "name": prompt_name,
                    "arguments": arguments
                }
            }
            self.session_id += 1
            
            # Make request to /mcp/prompts/get endpoint
            response = self.session.post(
                f"{self.mcp_url}/prompts/get",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            
            # Handle SSE response format (MCP returns event stream)
            response_text = response.text.strip()
            if "event: message" in response_text and "data: " in response_text:
                # Parse SSE format
                lines = response_text.split('\n')
                for line in lines:
                    if line.startswith("data: "):
                        result = json.loads(line[6:])
                        break
                else:
                    # Fallback to JSON if SSE parsing fails
                    result = response.json()
            else:
                # Direct JSON response
                result = response.json()
            
            if "result" in result and "messages" in result["result"]:
                messages = result["result"]["messages"]
                if messages and len(messages) > 0:
                    message = messages[0]
                    content = message.get("content", {})
                    
                    if isinstance(content, dict) and "text" in content:
                        prompt_text = content["text"]
                        self.logger.info(
                            "Prompt assembled successfully",
                            extra={
                                "prompt_name": prompt_name,
                                "content_length": len(prompt_text)
                            }
                        )
                        return prompt_text
                    elif isinstance(content, str):
                        self.logger.info(
                            "Prompt assembled successfully",
                            extra={
                                "prompt_name": prompt_name,
                                "content_length": len(content)
                            }
                        )
                        return content
                    
            elif "error" in result:
                error_msg = result['error']['message']
                self.logger.error(
                    "Prompt retrieval failed",
                    extra={
                        "prompt_name": prompt_name,
                        "error_message": error_msg
                    }
                )
                
            return None
                
        except Exception as e:
            self._metrics['errors'] += 1
            self.logger.error(
                "Prompt retrieval exception",
                extra={
                    "prompt_name": prompt_name,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return None
    
    async def get_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """
        Read MCP resource content with comprehensive error handling
        
        Args:
            uri: Resource URI to read
            
        Returns:
            Resource data dictionary with contents and metadata, or None if failed
        """
        self.logger.info(
            "Resource retrieval started",
            extra={"uri": uri}
        )
        
        try:
            result = await self._request("resources/read", {"uri": uri})
            
            if "result" in result and "contents" in result["result"]:
                contents = result["result"]["contents"]
                if contents and len(contents) > 0:
                    resource_data = {
                        "uri": uri,
                        "contents": contents[0].get("text", ""),
                        "mimeType": contents[0].get("mimeType", "text/plain")
                    }
                    
                    self.logger.info(
                        "Resource loaded successfully",
                        extra={
                            "uri": uri,
                            "content_length": len(resource_data['contents']),
                            "mime_type": resource_data['mimeType']
                        }
                    )
                    return resource_data
                    
            elif "error" in result:
                error_msg = result['error']['message']
                self.logger.error(
                    "Resource retrieval failed",
                    extra={
                        "uri": uri,
                        "error_message": error_msg
                    }
                )
                
            return None
                
        except Exception as e:
            self._metrics['errors'] += 1
            self.logger.error(
                "Resource retrieval exception",
                extra={
                    "uri": uri,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return None
    
    # ==================== SECURITY LEVEL OPERATIONS ====================
    
    async def get_tool_security_levels(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get security levels for all available tools
        
        Args:
            user_id: Optional user ID for access control
            
        Returns:
            Dict with tools and their security levels
        """
        try:
            params = {}
            if user_id:
                params["user_id"] = user_id
            
            result = await self._search_request("/security/levels", params=params)
            
            # Extract tools from security_levels if present
            if 'security_levels' in result and 'tools' in result['security_levels']:
                tools = result['security_levels']['tools']
                formatted_result = {'tools': tools, 'metadata': result.get('metadata', {})}
            else:
                formatted_result = result
            
            self.logger.info(
                "Tool security levels retrieved",
                extra={
                    "user_id": user_id,
                    "tools_count": len(formatted_result.get('tools', {}))
                }
            )
            
            return formatted_result
            
        except Exception as e:
            self._metrics['errors'] += 1
            self.logger.error(
                "Failed to get tool security levels",
                extra={"user_id": user_id, "error": str(e)}
            )
            return {"tools": {}, "metadata": {}}
    
    async def search_tools_by_security_level(self, security_level: str, query: Optional[str] = None, 
                                           user_id: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tools by security level
        
        Args:
            security_level: Security level (LOW, MEDIUM, HIGH, CRITICAL)
            query: Optional search query to filter tools
            user_id: Optional user ID for access control
            max_results: Maximum number of results
            
        Returns:
            List of tools matching the security level and query
        """
        try:
            payload = {
                "security_level": security_level.upper(),
                "max_results": max_results
            }
            
            if query:
                payload["query"] = query
            if user_id:
                payload["user_id"] = user_id
            
            result = await self._search_request("/security/search", payload)
            tools = self.convert_search_results_to_tools(result)
            
            self.logger.info(
                "Security level search completed",
                extra={
                    "security_level": security_level,
                    "query": query,
                    "user_id": user_id,
                    "tools_found": len(tools)
                }
            )
            
            return tools
            
        except Exception as e:
            self._metrics['errors'] += 1
            self.logger.error(
                "Security level search failed",
                extra={
                    "security_level": security_level,
                    "query": query,
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            return []
    
    async def get_tool_security_level(self, tool_name: str, user_id: Optional[str] = None) -> Optional[str]:
        """
        Get security level for a specific tool
        
        Args:
            tool_name: Name of the tool
            user_id: Optional user ID for access control
            
        Returns:
            Security level string (LOW, MEDIUM, HIGH, CRITICAL) or None if not found
        """
        try:
            security_levels = await self.get_tool_security_levels(user_id)
            tools = security_levels.get('tools', {})
            
            tool_info = tools.get(tool_name)
            if tool_info:
                return tool_info.get('security_level')
            
            return None
            
        except Exception as e:
            self.logger.error(
                "Failed to get tool security level",
                extra={"tool_name": tool_name, "user_id": user_id, "error": str(e)}
            )
            return None
    
    async def check_tool_security_authorized(self, tool_name: str, required_level: str, 
                                           user_id: Optional[str] = None) -> bool:
        """
        Check if a tool meets the required security level
        
        Args:
            tool_name: Name of the tool
            required_level: Required security level (LOW, MEDIUM, HIGH, CRITICAL)
            user_id: Optional user ID for access control
            
        Returns:
            True if tool meets or exceeds required security level
        """
        try:
            tool_level = await self.get_tool_security_level(tool_name, user_id)
            if not tool_level:
                return False
            
            # Security level hierarchy: LOW < MEDIUM < HIGH < CRITICAL
            level_hierarchy = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
            
            tool_level_value = level_hierarchy.get(tool_level.upper(), 0)
            required_level_value = level_hierarchy.get(required_level.upper(), 0)
            
            authorized = tool_level_value >= required_level_value
            
            self.logger.info(
                "Security authorization check",
                extra={
                    "tool_name": tool_name,
                    "tool_security_level": tool_level,
                    "required_level": required_level,
                    "authorized": authorized,
                    "user_id": user_id
                }
            )
            
            return authorized
            
        except Exception as e:
            self.logger.error(
                "Security authorization check failed",
                extra={
                    "tool_name": tool_name,
                    "required_level": required_level,
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            return False
    
    # ==================== CACHE MANAGEMENT ====================
    
    async def clear_cache(self):
        """Clear all cached data and log the operation"""
        async with self._cache_lock:
            cache_stats_before = {
                "capabilities_cached": self._capabilities_cache is not None,
                "search_cache_size": len(self._search_cache)
            }
            
            self._capabilities_cache = None
            self._capabilities_cache_time = 0
            self._search_cache.clear()
            
        self.logger.info(
            "Cache cleared",
            extra={"cache_stats_before": cache_stats_before}
        )
    
    async def refresh_capabilities(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Force refresh capabilities cache and return new data"""
        self.logger.info(
            "Forcing capabilities cache refresh",
            extra={"user_id": user_id}
        )
        
        async with self._cache_lock:
            self._capabilities_cache = None
            self._capabilities_cache_time = 0
        
        return await self.list_all(user_id)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache and performance statistics"""
        return {
            "capabilities_cached": self._capabilities_cache is not None,
            "capabilities_cache_age": time() - self._capabilities_cache_time if self._capabilities_cache else 0,
            "search_cache_size": len(self._search_cache),
            "cache_ttl": self.cache_ttl,
            "metrics": self._metrics.copy()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        total_requests = self._metrics['requests_total']
        cache_hit_rate = (
            self._metrics['cache_hits'] / (self._metrics['cache_hits'] + self._metrics['cache_misses'])
            if (self._metrics['cache_hits'] + self._metrics['cache_misses']) > 0 else 0
        )
        
        return {
            **self._metrics.copy(),
            "cache_hit_rate": cache_hit_rate,
            "error_rate": self._metrics['errors'] / total_requests if total_requests > 0 else 0
        }
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        self.logger.info("Resetting performance metrics", extra={"metrics_before": self._metrics.copy()})
        self._metrics = {
            'requests_total': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'tool_executions': 0
        }
    
