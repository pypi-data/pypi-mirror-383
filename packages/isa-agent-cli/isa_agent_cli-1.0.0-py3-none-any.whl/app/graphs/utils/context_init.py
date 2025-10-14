#!/usr/bin/env python3
"""
LangGraph Runtime Context Preparation

This module only handles 4 things:
1. Initialize memory (user_id + thread_id)  
2. Load default tools from MCP
3. Load default prompts from MCP
4. Load default resources from MCP

Nothing else. Keep it simple.
"""

import asyncio
import logging
import time
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from langchain_core.messages import HumanMessage
from ...components.mcp_service import MCPService
from ...components.storage_service import get_storage_service
from ...types.agent_state import AgentState
from .memory_utils import get_user_memory_context
from ...utils.logger import agent_logger

logger = agent_logger  # Use centralized logger for Loki integration


class RuntimeContextHelper:
    """
    Simple helper for LangGraph runtime context preparation
    
    Only does 4 things:
    1. Memory initialization
    2. Default tools loading
    3. Default prompts loading  
    4. Default resources loading
    """
    
    def __init__(self, mcp_url: str = None):
        if mcp_url is None:
            from app.config import settings
            mcp_url = settings.resolved_mcp_server_url + "/mcp"
        self.mcp_url = mcp_url
        self.mcp_service = MCPService(mcp_url)
        self.logger = agent_logger  # Use centralized logger for Loki integration
        
        # Default data cache
        self._default_prompts = {}
        self._default_tools = []
        self._default_resources = []
        self._initialized = False
        
        # Advanced caching system
        self._cache_ttl = 300  # 5 minutes default TTL
        self._tool_search_cache = {}  # Cache for tool searches
        self._memory_context_cache = {}  # Cache for memory contexts
        self._prompt_cache = {}  # Cache for assembled prompts
        
        # Cache statistics
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    async def initialize(self):
        """Initialize MCP service and load defaults"""
        try:
            init_start = time.time()
            await self.mcp_service.initialize()
            mcp_init_duration = int((time.time() - init_start) * 1000)
            self.logger.info(f"context_mcp_init | duration_ms={mcp_init_duration}")

            # Load all defaults in parallel
            import asyncio
            load_start = time.time()
            await asyncio.gather(
                self._load_default_prompts(),
                self._load_default_tools(),
                self._load_default_resources()
            )
            load_duration = int((time.time() - load_start) * 1000)
            self.logger.info(f"context_load_defaults | duration_ms={load_duration}")

            self._initialized = True
            total_init_duration = int((time.time() - init_start) * 1000)
            self.logger.info(f"Runtime context helper initialized | total_duration_ms={total_init_duration}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            raise
    
    async def _load_default_prompts(self):
        """Load default prompts from MCP with required arguments"""
        try:
            prompts = await self.mcp_service.get_default_prompts(max_results=50)
            
            # Define required arguments for prompts that need them
            prompt_args = {
                'default_reason_prompt': {'user_message': 'placeholder'},
                'default_response_prompt': {},
                'default_review_prompt': {'user_message': 'placeholder'}
            }
            
            # Convert to name -> assembled_text dict
            for prompt_info in prompts:
                name = prompt_info.get('name', '')
                if name:
                    # Use appropriate arguments for each prompt
                    args = prompt_args.get(name, {})
                    text = await self.mcp_service.get_prompt(name, args)
                    if text:
                        self._default_prompts[name] = text
            
            self.logger.info(f"Loaded {len(self._default_prompts)} default prompts")
            
        except Exception as e:
            self.logger.error(f"Failed to load default prompts: {e}")
            self._default_prompts = {}
    
    async def _load_default_tools(self):
        """Load default tools from MCP"""
        try:
            self._default_tools = await self.mcp_service.get_default_tools(max_results=50)
            self.logger.info(f"Loaded {len(self._default_tools)} default tools")
            
        except Exception as e:
            self.logger.error(f"Failed to load default tools: {e}")
            self._default_tools = []
    
    async def search_relevant_tools(self, user_query: str, max_results: int = 10) -> list:
        """
        Search for tools relevant to user query using semantic search with caching

        Args:
            user_query: User's query to search tools for
            max_results: Maximum number of relevant tools to return

        Returns:
            List of relevant tools based on semantic matching
        """
        try:
            search_start = time.time()

            if not user_query or not user_query.strip():
                self.logger.debug("[PHASE:CONTEXT] tool_search_skip | reason=empty_query")
                return self._default_tools[:max_results]

            # Normalize query for better cache hits (lowercase, strip whitespace)
            normalized_query = user_query.lower().strip()

            # Pattern detection: Skip tool search for simple queries that don't need tools
            simple_patterns = [
                # Math/calculation queries
                r'\b\d+\s*[\+\-\*\/]\s*\d+\b',  # "2+2", "10 * 5"
                r'\bwhat is \d+[\+\-\*\/]\d+\b',  # "what is 2+2"
                # Greetings
                r'^(hi|hello|hey|greetings?)!?\s*$',
                # Simple questions that don't need external tools
                r'^(how are you|what\'?s up|test)\??!?\s*$',
            ]

            import re
            for pattern in simple_patterns:
                if re.search(pattern, normalized_query, re.IGNORECASE):
                    self.logger.info(
                        f"[PHASE:CONTEXT] tool_search_simple_pattern | "
                        f"query='{user_query[:50]}' | "
                        f"pattern_matched=True | "
                        f"returning_defaults={min(5, max_results)}"
                    )
                    return self._default_tools[:min(5, max_results)]  # Return fewer defaults for simple queries

            # Check cache first with normalized query
            cache_key = self._get_cache_key("search_tools", normalized_query, max_results=max_results)
            cached_tools = self._get_cached_data(self._tool_search_cache, cache_key)

            if cached_tools is not None:
                cache_hit_duration = int((time.time() - search_start) * 1000)
                self.logger.info(
                    f"[PHASE:CONTEXT] tool_search_cache_hit | "
                    f"query='{user_query[:50]}' | "
                    f"tools_count={len(cached_tools)} | "
                    f"duration_ms={cache_hit_duration}"
                )
                self._cache_stats['hits'] += 1
                return cached_tools

            # Cache miss - perform search
            self._cache_stats['misses'] += 1
            self.logger.info(
                f"[PHASE:CONTEXT] tool_search_cache_miss | "
                f"query='{user_query[:50]}' | "
                f"initiating_mcp_search=True"
            )

            relevant_tools = await self.mcp_service.search_tools(
                query=user_query,
                max_results=max_results
            )

            # Cache the results with normalized query key
            self._set_cache_data(self._tool_search_cache, cache_key, relevant_tools)

            search_duration = int((time.time() - search_start) * 1000)
            tool_names = [t.get('name', 'unknown') for t in relevant_tools[:5]]
            self.logger.info(
                f"[PHASE:CONTEXT] tool_search_complete | "
                f"query='{user_query[:50]}' | "
                f"found={len(relevant_tools)} | "
                f"top_tools={tool_names} | "
                f"cache_status=miss | "
                f"duration_ms={search_duration}"
            )
            return relevant_tools

        except Exception as e:
            self.logger.error(
                f"[PHASE:CONTEXT] tool_search_error | "
                f"query='{user_query[:50] if user_query else 'N/A'}' | "
                f"error={type(e).__name__} | "
                f"message={str(e)[:200]} | "
                f"fallback=default_tools",
                exc_info=True
            )
            # Fallback to default tools
            return self._default_tools[:max_results]
    
    async def _load_default_resources(self):
        """Load default resources from MCP"""
        try:
            self._default_resources = await self.mcp_service.get_default_resources(max_results=50)
            self.logger.info(f"Loaded {len(self._default_resources)} default resources")
            
        except Exception as e:
            self.logger.error(f"Failed to load default resources: {e}")
            self._default_resources = []
    
    def _get_cache_key(self, operation: str, *args, **kwargs) -> str:
        """Generate cache key from operation and parameters"""
        key_data = f"{operation}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_data(self, cache_dict: Dict, cache_key: str) -> Optional[Any]:
        """Get data from cache if not expired"""
        if cache_key in cache_dict:
            data, timestamp = cache_dict[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                self._cache_stats['hits'] += 1
                return data
            else:
                # Cache expired
                del cache_dict[cache_key]
                self._cache_stats['evictions'] += 1
        
        self._cache_stats['misses'] += 1
        return None
    
    def _set_cache_data(self, cache_dict: Dict, cache_key: str, data: Any):
        """Store data in cache with timestamp"""
        cache_dict[cache_key] = (data, time.time())
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = (self._cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._cache_stats,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2),
            'cache_sizes': {
                'tool_searches': len(self._tool_search_cache),
                'memory_contexts': len(self._memory_context_cache),
                'prompts': len(self._prompt_cache)
            }
        }
    
    def clear_cache(self, cache_type: Optional[str] = None):
        """Clear cache data"""
        if cache_type == 'tools':
            self._tool_search_cache.clear()
        elif cache_type == 'memory':
            self._memory_context_cache.clear()
        elif cache_type == 'prompts':
            self._prompt_cache.clear()
        else:
            # Clear all caches
            self._tool_search_cache.clear()
            self._memory_context_cache.clear()
            self._prompt_cache.clear()
        
        self.logger.info(f"Cache cleared: {cache_type or 'all'}")
    
    async def _get_cached_memory_context(self, user_id: str, thread_id: str) -> str:
        """Get memory context with caching"""
        # Check cache first
        cache_key = self._get_cache_key("memory_context", user_id, thread_id, max_length=2000)
        cached_context = self._get_cached_data(self._memory_context_cache, cache_key)
        
        if cached_context is not None:
            self.logger.debug(f"Using cached memory context for user {user_id}, session {thread_id}")
            return cached_context
        
        # Cache miss - fetch from MCP
        try:
            memory_context = await get_user_memory_context(
                mcp_service=self.mcp_service,
                user_id=user_id,
                session_id=thread_id,
                max_length=2000
            )
            
            # Cache the result
            self._set_cache_data(self._memory_context_cache, cache_key, memory_context)
            
            self.logger.debug(f"Fetched and cached memory context for user {user_id}, session {thread_id}")
            return memory_context
            
        except Exception as e:
            self.logger.warning(f"Failed to get memory context: {e}")
            fallback_context = f"# Memory Context\n\nUser: {user_id}\nSession: {thread_id}\nNote: Memory unavailable"
            
            # Cache the fallback too (with shorter TTL)
            self._set_cache_data(self._memory_context_cache, cache_key, fallback_context)
            
            return fallback_context
    
    async def _check_user_has_files(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user has any files (both in storage and potentially from current request)
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with file availability information
        """
        try:
            # Check storage service for existing files
            files_result = await self.mcp_service.call_tool("list_user_files", {
                "user_id": user_id,
                "limit": 5  # Get a few files to understand what user has
            })
            
            import json
            files_data = json.loads(files_result) if isinstance(files_result, str) else files_result
            
            has_storage_files = False
            storage_file_count = 0
            recent_files = []
            
            if files_data.get("status") == "success" and files_data.get("data", {}).get("success"):
                files_list = files_data["data"].get("files", [])
                storage_file_count = len(files_list)
                has_storage_files = storage_file_count > 0
                recent_files = files_list[:3]  # Keep top 3 for context
            
            self.logger.info(
                f"[PHASE:CONTEXT] user_file_check | "
                f"user_id={user_id} | "
                f"storage_files={storage_file_count} | "
                f"has_files={has_storage_files}"
            )
            
            return {
                "has_files": has_storage_files,
                "storage_file_count": storage_file_count,
                "recent_files": recent_files,
                "file_types": list(set(f.get("content_type", "unknown") for f in recent_files)),
                "total_files": storage_file_count
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to check user files for {user_id}: {e}")
            return {
                "has_files": False,
                "storage_file_count": 0,
                "recent_files": [],
                "file_types": [],
                "total_files": 0,
                "error": str(e)
            }
    
    async def _get_user_file_context(self, user_id: str, user_query: str = None, max_results: int = 3) -> Dict[str, Any]:
        """
        Get relevant file context from user's Storage Service knowledge base
        
        Args:
            user_id: User identifier for knowledge isolation
            user_query: User query for semantic search (optional)
            max_results: Maximum number of relevant files to retrieve
            
        Returns:
            Dict with file context information and RAG results
        """
        try:
            if not user_query:
                return {"file_context": "", "relevant_files": [], "message": "No query provided for file context"}
            
            file_context_start = time.time()
            
            # TIMING: Step 1 - Search user's knowledge base for relevant content
            search_step_start = time.time()
            self.logger.info(f"[TIMING] search_knowledge_start | user_id={user_id} | query='{user_query[:50]}'")
            
            search_result = await self.mcp_service.call_tool("search_knowledge", {
                "user_id": user_id,
                "query": user_query,
                "top_k": max_results,
                "enable_rerank": True  # Enable reranking for better relevance
            })
            
            search_duration = int((time.time() - search_step_start) * 1000)
            self.logger.info(f"[TIMING] search_knowledge_complete | search_ms={search_duration} | user_id={user_id}")
            
            # Parse search results
            import json
            try:
                search_data = json.loads(search_result) if isinstance(search_result, str) else search_result
                
                if search_data.get("status") == "success" and search_data.get("data", {}).get("success"):
                    search_results = search_data["data"].get("search_results", [])
                    
                    if search_results:
                        # TIMING: Step 2 - Generate RAG response for context enhancement
                        rag_step_start = time.time()
                        self.logger.info(f"[TIMING] rag_generation_start | search_results={len(search_results)} | user_id={user_id}")
                        
                        rag_result = await self.mcp_service.call_tool("generate_rag_response", {
                            "user_id": user_id,
                            "query": f"Based on user's uploaded files, provide relevant context for: {user_query}",
                            "context_limit": max_results
                        })
                        rag_duration = int((time.time() - rag_step_start) * 1000)
                        self.logger.info(f"[TIMING] rag_generation_complete | rag_ms={rag_duration} | user_id={user_id}")
                        
                        # Parse RAG results
                        rag_data = json.loads(rag_result) if isinstance(rag_result, str) else rag_result
                        rag_context = ""
                        
                        if rag_data.get("status") == "success" and rag_data.get("data", {}).get("success"):
                            # The RAG response is in data.response field, not rag_answer.answer
                            rag_context = rag_data["data"].get("response", "")
                        
                        total_duration = int((time.time() - file_context_start) * 1000)
                        
                        self.logger.info(
                            f"[PHASE:CONTEXT] file_context_success | "
                            f"user_id={user_id} | "
                            f"query='{user_query[:50]}' | "
                            f"files_found={len(search_results)} | "
                            f"search_ms={search_duration} | "
                            f"rag_ms={rag_duration} | "
                            f"total_ms={total_duration}"
                        )
                        
                        return {
                            "file_context": rag_context,
                            "relevant_files": search_results,
                            "file_count": len(search_results),
                            "search_duration_ms": search_duration,
                            "rag_duration_ms": rag_duration,
                            "total_duration_ms": total_duration,
                            "message": f"Found {len(search_results)} relevant files"
                        }
                    else:
                        self.logger.info(
                            f"[PHASE:CONTEXT] file_context_empty | "
                            f"user_id={user_id} | "
                            f"query='{user_query[:50]}' | "
                            f"duration_ms={search_duration}"
                        )
                        return {
                            "file_context": "",
                            "relevant_files": [],
                            "file_count": 0,
                            "message": "No relevant files found in user's knowledge base"
                        }
                else:
                    error_msg = search_data.get("message", "Unknown search error")
                    self.logger.warning(
                        f"[PHASE:CONTEXT] file_context_search_failed | "
                        f"user_id={user_id} | "
                        f"error={error_msg[:100]}"
                    )
                    return {
                        "file_context": "",
                        "relevant_files": [],
                        "file_count": 0,
                        "message": f"Search failed: {error_msg}"
                    }
                    
            except json.JSONDecodeError as e:
                self.logger.error(
                    f"[PHASE:CONTEXT] file_context_parse_error | "
                    f"user_id={user_id} | "
                    f"error={str(e)[:100]}"
                )
                return {
                    "file_context": "",
                    "relevant_files": [],
                    "file_count": 0,
                    "message": f"Failed to parse search results: {str(e)}"
                }
                
        except Exception as e:
            self.logger.error(
                f"[PHASE:CONTEXT] file_context_error | "
                f"user_id={user_id} | "
                f"error={type(e).__name__} | "
                f"message={str(e)[:200]}",
                exc_info=True
            )
            return {
                "file_context": "",
                "relevant_files": [],
                "file_count": 0,
                "message": f"File context error: {str(e)}"
            }
    
    async def get_runtime_context(
        self,
        user_id: str,
        thread_id: str,
        session_service=None,
        user_query: str = None,
        enable_file_context: bool = True
    ) -> Dict[str, Any]:
        """
        Prepare runtime context with intelligent tool selection:
        1. Memory (user_id + thread_id aggregated context)
        2. Relevant tools (searched based on user query + defaults)
        3. Default prompts
        4. Default resources
        5. File context (RAG-enhanced context from user's uploaded files)

        Args:
            user_id: User identifier
            thread_id: Thread/session identifier
            session_service: Session service instance
            user_query: User's query for intelligent tool search
            enable_file_context: Whether to fetch file context from Storage Service (default: True)
        """
        context_start = time.time()
        self.logger.info(
            f"[PHASE:CONTEXT] get_runtime_context_start | "
            f"user_id={user_id} | "
            f"thread_id={thread_id} | "
            f"query='{user_query[:100] if user_query else 'None'}'"
        )

        if not self._initialized:
            await self.initialize()

        # 1. Get aggregated memory context with caching
        memory_start = time.time()
        memory_context = await self._get_cached_memory_context(user_id, thread_id)
        memory_duration = int((time.time() - memory_start) * 1000)
        memory_length = len(memory_context) if memory_context else 0
        self.logger.info(
            f"[PHASE:CONTEXT] memory_loaded | "
            f"user_id={user_id} | "
            f"thread_id={thread_id} | "
            f"memory_length={memory_length} | "
            f"duration_ms={memory_duration}"
        )
        
        # 1.5. Check if user has files and get file context (if enabled and query provided)
        user_file_info = await self._check_user_has_files(user_id)
        file_context_data = {"file_context": "", "relevant_files": [], "file_count": 0}
        
        if enable_file_context and user_query and user_file_info.get("has_files", False):
            file_context_data = await self._get_user_file_context(user_id, user_query, max_results=3)
        elif not enable_file_context:
            self.logger.debug(
                f"[PHASE:CONTEXT] file_context_disabled | "
                f"user_id={user_id} | "
                f"thread_id={thread_id}"
            )
        elif not user_query:
            self.logger.debug(
                f"[PHASE:CONTEXT] file_context_skipped | "
                f"user_id={user_id} | "
                f"thread_id={thread_id} | "
                f"reason=no_query"
            )
        elif not user_file_info.get("has_files", False):
            self.logger.debug(
                f"[PHASE:CONTEXT] file_context_skipped | "
                f"user_id={user_id} | "
                f"thread_id={thread_id} | "
                f"reason=no_files"
            )
        
        # 2. Get relevant tools based on user query
        tools_start = time.time()
        if user_query:
            # Search for relevant tools + include defaults
            search_start = time.time()
            relevant_tools = await self.search_relevant_tools(user_query, max_results=6)  # Reduced from 15 to 6
            search_duration = int((time.time() - search_start) * 1000)
            relevant_tool_names = [t.get('name', 'unknown') for t in relevant_tools[:5]]  # Top 5 for logging
            self.logger.info(
                f"[PHASE:CONTEXT] tool_search | "
                f"query='{user_query[:50]}...' | "
                f"found={len(relevant_tools)} | "
                f"top_tools={relevant_tool_names} | "
                f"duration_ms={search_duration}"
            )

            # ALWAYS ensure critical tools are at the front
            critical_tool_names = [
                'create_execution_plan', 
                'web_search', 
                'web_crawl', 
                'web_automation', 
                'replan_execution',
                # Composio tools for OAuth testing
                'composio_gmail_send_message',
                'composio_github_send_message',
                'composio_list_available_apps'
            ]
            
            # Add file-related tools if user has files
            if user_file_info.get("has_files", False):
                # Storage service RAG tools
                rag_tool_names = [
                    'search_knowledge',
                    'generate_rag_response', 
                    'list_user_files'
                ]
                
                # MCP data analysis tools from digital_analytics_service
                mcp_data_tools = [
                    'data_ingest',       # data_tools.py - Ingest CSV/Excel files  
                    'data_search',       # data_tools.py - Search data semantically
                    'data_query',        # data_tools.py - Natural language queries
                    'store_knowledge',   # digital_tools.py - Universal storage
                    'search_knowledge',  # digital_tools.py - Universal search
                    'knowledge_response' # digital_tools.py - RAG responses
                ]
                
                # Add both sets of tools
                critical_tool_names.extend(rag_tool_names)
                critical_tool_names.extend(mcp_data_tools)
                
                self.logger.info(
                    f"[PHASE:CONTEXT] file_tools_added | "
                    f"user_id={user_id} | "
                    f"file_count={user_file_info.get('total_files', 0)} | "
                    f"storage_rag_tools={rag_tool_names} | "
                    f"mcp_data_tools={mcp_data_tools}"
                )
            combined_tools = []

            # Step 1: Add critical tools from defaults first
            for tool_name in critical_tool_names:
                tool = next((t for t in self._default_tools if t.get('name') == tool_name), None)
                if tool and tool not in combined_tools:
                    combined_tools.append(tool)

            # Step 2: Add relevant search results (excluding critical tools already added)
            for tool in relevant_tools:
                if tool.get('name') not in critical_tool_names and tool not in combined_tools:
                    combined_tools.append(tool)
                    if len(combined_tools) >= 10:  # Stop at 10 tools
                        break

            tools_to_use = combined_tools[:10]  # Hard limit to 10 total tools

            tools_duration = int((time.time() - tools_start) * 1000)
            final_tool_names = [t.get('name', 'unknown') for t in tools_to_use]

            self.logger.info(
                f"[PHASE:CONTEXT] tools_finalized | "
                f"session_id={thread_id} | "
                f"user_id={user_id} | "
                f"relevant={len(relevant_tools)} | "
                f"total={len(tools_to_use)} | "
                f"tools={final_tool_names} | "
                f"duration_ms={tools_duration}"
            )
        else:
            # No query provided - use default tools
            tools_to_use = self._default_tools
            tools_duration = int((time.time() - tools_start) * 1000)

            self.logger.info(
                f"context_tools_loaded | "
                f"session_id={thread_id} | "
                f"user_id={user_id} | "
                f"mode=default | "
                f"total_tools={len(tools_to_use)} | "
                f"duration_ms={tools_duration}"
            )

        # Log complete context preparation
        context_duration = int((time.time() - context_start) * 1000)
        memory_length = len(memory_context) if memory_context else 0
        file_context_length = len(file_context_data.get("file_context", ""))

        self.logger.info(
            f"[PHASE:CONTEXT] context_complete | "
            f"session_id={thread_id} | "
            f"user_id={user_id} | "
            f"memory_length={memory_length} | "
            f"file_context_length={file_context_length} | "
            f"file_count={file_context_data.get('file_count', 0)} | "
            f"tools_count={len(tools_to_use)} | "
            f"prompts_count={len(self._default_prompts)} | "
            f"resources_count={len(self._default_resources)} | "
            f"total_duration_ms={context_duration} | "
            f"memory_ms={memory_duration} | "
            f"tools_ms={tools_duration}"
        )

        return {
            # 1. Memory (aggregated from MCP memory tools)
            'user_id': user_id,
            'thread_id': thread_id,
            'memory_context': memory_context,

            # 2. File context (RAG-enhanced context from user's uploaded files)
            'file_context': file_context_data.get("file_context", ""),
            'relevant_files': file_context_data.get("relevant_files", []),
            'file_count': file_context_data.get("file_count", 0),
            
            # 2.5. User file information for RAG capabilities
            'user_file_info': user_file_info,
            'has_user_files': user_file_info.get("has_files", False),

            # 3. Final tools (searched + defaults combined)
            'available_tools': tools_to_use,

            # 4. Default prompts
            'default_prompts': self._default_prompts,

            # 5. Default resources
            'default_resources': self._default_resources,

            # Essential services
            'mcp_service': self.mcp_service,
            'session_service': session_service,
            'runtime_initialized': True
        }
    
    async def close(self):
        """Clean shutdown"""
        if self.mcp_service:
            await self.mcp_service.close()
        self._initialized = False


# Global instance
_runtime_helper = None


async def get_runtime_helper(mcp_url: str = None) -> RuntimeContextHelper:
    if mcp_url is None:
        from app.config import settings
        mcp_url = settings.resolved_mcp_server_url + "/mcp"
    """Get global runtime helper instance"""
    global _runtime_helper
    
    if _runtime_helper is None:
        _runtime_helper = RuntimeContextHelper(mcp_url)
        await _runtime_helper.initialize()
    
    return _runtime_helper


async def enhance_user_query(
    user_query: str,
    prompt_name: str,
    prompt_args: Dict[str, Any],
    mcp_url: str = None
) -> str:
    """
    Enhance user query using MCP prompt template with caching
    
    Args:
        user_query: Original user input
        prompt_name: MCP prompt template name
        prompt_args: Arguments for prompt template
        mcp_url: MCP service URL
        
    Returns:
        Enhanced user query with prompt template applied
    """
    try:
        helper = await get_runtime_helper(mcp_url)
        
        # Ensure required arguments are provided for prompts that need them
        if prompt_name in ['default_reason_prompt', 'default_review_prompt'] and 'user_message' not in prompt_args:
            prompt_args['user_message'] = user_query
        
        # Check cache first
        cache_key = helper._get_cache_key("enhance_query", prompt_name, user_query, **prompt_args)
        cached_prompt = helper._get_cached_data(helper._prompt_cache, cache_key)
        
        if cached_prompt is not None:
            helper.logger.debug(f"Using cached enhanced query for prompt '{prompt_name}'")
            return cached_prompt
        
        # Cache miss - get prompt from MCP
        enhanced_prompt = await helper.mcp_service.get_prompt(prompt_name, prompt_args)
        
        if enhanced_prompt:
            # Cache the result
            helper._set_cache_data(helper._prompt_cache, cache_key, enhanced_prompt)
            helper.logger.debug(f"Enhanced and cached query using prompt '{prompt_name}'")
            return enhanced_prompt
        else:
            logger.warning(f"Prompt template '{prompt_name}' not found, using original query")
            # Cache the fallback
            helper._set_cache_data(helper._prompt_cache, cache_key, user_query)
            return user_query
            
    except Exception as e:
        logger.error(f"Query enhancement failed: {e}")
        return user_query


async def prepare_runtime_context(
    user_id: str,
    thread_id: str,
    session_service=None,
    mcp_url: str = None,
    user_query: str = None,
    prompt_name: str = None,
    prompt_args: Dict[str, Any] = None,
    enable_file_context: bool = True
) -> Dict[str, Any]:
    """
    Prepare runtime context with 5 core components:
    
    1. Memory (user_id + thread_id aggregated context)
    2. MCP Tools (default + query-relevant search)
    3. MCP Prompts (default prompt templates)
    4. MCP Resources (default resource definitions)
    5. Knowledge Context (file context from user's uploaded files)

    Args:
        user_id: User identifier
        thread_id: Thread/session identifier
        session_service: Session service instance
        mcp_url: MCP service URL
        user_query: User query for intelligent tool search and file context
        prompt_name: MCP prompt template name (optional)
        prompt_args: Prompt template arguments (optional)
        enable_file_context: Whether to fetch file context from Storage Service

    Returns:
        Complete runtime context for LangGraph execution
    """
    prepare_start = time.time()

    helper_start = time.time()
    helper = await get_runtime_helper(mcp_url)
    helper_duration = int((time.time() - helper_start) * 1000)
    logger.info(f"context_helper_init | user_id={user_id} | thread_id={thread_id} | duration_ms={helper_duration}")
    with open("/tmp/chat_timing_debug.log", "a") as f:
        f.write(f"{thread_id} | helper_init: {helper_duration}ms\n")

    context_start = time.time()
    context = await helper.get_runtime_context(user_id, thread_id, session_service, user_query, enable_file_context)
    context_duration = int((time.time() - context_start) * 1000)
    logger.info(f"context_get_runtime | user_id={user_id} | thread_id={thread_id} | duration_ms={context_duration}")
    with open("/tmp/chat_timing_debug.log", "a") as f:
        f.write(f"{thread_id} | get_runtime_context: {context_duration}ms\n")
    
    # Optional query enhancement with prompt templates
    if user_query and prompt_name:
        try:
            enhanced_query = await enhance_user_query(
                user_query=user_query,
                prompt_name=prompt_name,
                prompt_args=prompt_args or {},
                mcp_url=mcp_url
            )
            context['enhanced_query'] = enhanced_query
            context['original_query'] = user_query

            prepare_duration = int((time.time() - prepare_start) * 1000)
            logger.info(
                f"context_prepare_complete | "
                f"session_id={thread_id} | "
                f"user_id={user_id} | "
                f"enhanced=true | "
                f"prompt={prompt_name} | "
                f"duration_ms={prepare_duration}"
            )
        except Exception as e:
            logger.error(
                f"context_enhance_error | "
                f"session_id={thread_id} | "
                f"user_id={user_id} | "
                f"error={type(e).__name__} | "
                f"message={str(e)[:200]}",
                exc_info=True
            )
            context['enhanced_query'] = user_query
            context['original_query'] = user_query
    elif user_query:
        # Use original query without enhancement
        context['enhanced_query'] = user_query
        context['original_query'] = user_query

        prepare_duration = int((time.time() - prepare_start) * 1000)
        logger.info(
            f"context_prepare_complete | "
            f"session_id={thread_id} | "
            f"user_id={user_id} | "
            f"enhanced=false | "
            f"duration_ms={prepare_duration}"
        )

    return context


def create_initial_state(user_query: str) -> AgentState:
    """
    Create initial agent state - only provide message
    
    Args:
        user_query: User input message
        
    Returns:
        AgentState with HumanMessage
    """
    state = AgentState(
        messages=[HumanMessage(content=user_query)]
    )
    
    return state


async def get_runtime_cache_stats(mcp_url: str = None) -> Dict[str, Any]:
    if mcp_url is None:
        from app.config import settings
        mcp_url = settings.resolved_mcp_server_url + "/mcp"
    """Get runtime cache performance statistics"""
    try:
        helper = await get_runtime_helper(mcp_url)
        return helper.get_cache_stats()
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {"error": str(e)}


async def clear_runtime_cache(cache_type: Optional[str] = None, mcp_url: str = None):
    if mcp_url is None:
        from app.config import settings
        mcp_url = settings.resolved_mcp_server_url + "/mcp"
    """Clear runtime cache"""
    try:
        helper = await get_runtime_helper(mcp_url)
        helper.clear_cache(cache_type)
        return True
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return False


async def cleanup_runtime():
    """Cleanup global helper"""
    global _runtime_helper
    
    if _runtime_helper:
        await _runtime_helper.close()
        _runtime_helper = None


# Context preparation complete - no prediction functionality needed