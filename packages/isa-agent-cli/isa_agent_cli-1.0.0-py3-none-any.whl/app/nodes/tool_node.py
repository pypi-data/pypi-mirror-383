#!/usr/bin/env python3
"""
Tool Node - Clean tool execution with MCP integration

Professional tool execution node that:
1. Executes tool calls from reason_node
2. Uses base_node MCP integration  
3. Handles plan_tool detection for autonomous execution
4. Provides clean streaming feedback
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt, Command

from ..types.agent_state import AgentState
from .base_node import BaseNode
from ..services.hil_service import hil_service
from ..utils.logger import agent_logger

logger = agent_logger  # Use centralized logger for Loki integration


class ToolNode(BaseNode):
    """Professional tool execution node with MCP integration"""
    
    def __init__(self):
        super().__init__("ToolNode")
        print("🔧🔧🔧 ToolNode CONSTRUCTOR called! 🔧🔧🔧")
        
        # Cache for tool security levels to avoid repeated MCP queries
        self._security_level_cache = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        
        # Batch authorization tracking
        self._authorization_batch = {}
    
    async def _execute_logic(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """
        Execute tools from reason_node
        
        Args:
            state: Current agent state with messages containing tool_calls
            config: Runtime config with MCP service context
            
        Returns:
            Updated state with tool execution results
        """
        print("🔧🔧🔧 ToolNode._execute_logic started! 🔧🔧🔧")
        
        self.logger.info("🔧 ToolNode executing tools")
        
        messages = state.get("messages", [])
        
        if not messages:
            self.logger.warning("No messages for tool execution")
            return {"next_action": "end"}
        
        last_message = messages[-1]
        tool_calls = getattr(last_message, 'tool_calls', [])
        
        if not tool_calls:
            self.logger.warning("No tool calls found in last message")
            return {"next_action": "end"}
        
        # Extract all tool names for batch authorization check
        tool_info_list = []
        for i, tool_call in enumerate(tool_calls):
            tool_name, tool_args, tool_call_id = self._extract_tool_info(tool_call, i)
            tool_info_list.append((tool_name, tool_args, tool_call_id))
        
        tool_names = [info[0] for info in tool_info_list]
        
        # Batch authorization check
        self.logger.info(f"🔒 Starting batch authorization check for {len(tool_names)} tools: {tool_names}")
        authorization_results = await self._batch_check_tool_authorization(tool_names, config)
        self.logger.info(f"📋 Authorization results: {authorization_results}")
        
        # Check if any tools need authorization and batch request if needed
        high_security_tools = [
            (tool_name, auth_info[0]) 
            for tool_name, auth_info in authorization_results.items() 
            if auth_info[1]  # needs_authorization
        ]
        
        if high_security_tools:
            await self._request_batch_authorization(high_security_tools, config)
            self.logger.info(f"✅ Batch authorization completed for {len(high_security_tools)} high-security tools")

        # PHASE 1: Detect long-running tasks and offer HIL choice
        long_running_detected = self._detect_long_running_task(tool_info_list)
        if long_running_detected:
            execution_choice = await self._offer_execution_choice(long_running_detected, config)

            if execution_choice == "background":
                # PHASE 2: Queue background job and return job_id
                job_result = await self._queue_background_job(tool_info_list, state, config)
                tool_messages = [ToolMessage(
                    content=json.dumps(job_result),
                    tool_call_id=tool_info_list[0][2]  # Use first tool's call_id
                )]
                return {
                    "messages": tool_messages,
                    "next_action": "call_model",
                    "background_job": job_result
                }
            elif execution_choice == "quick":
                # Limit to fast execution (3 sources max, 30s timeout)
                tool_info_list = self._optimize_for_quick_execution(tool_info_list)

        # Collect all tool messages
        tool_messages = []

        # Execute each tool call (authorization already handled)
        for i, (tool_name, tool_args, tool_call_id) in enumerate(tool_info_list):
            self.stream_tool(tool_name, f"Starting execution ({i+1}/{len(tool_calls)})")

            # Structured logging: tool start
            tool_start = time.time()
            session_id = state.get("session_id", "unknown")
            self.logger.info(
                f"tool_call_start | "
                f"session_id={session_id} | "
                f"tool={tool_name} | "
                f"args_length={len(str(tool_args))}"
            )

            # Execute tool via base_node MCP integration (authorization already done)
            try:
                # Log tool execution start
                args_preview = str(tool_args)[:200]
                self.logger.info(
                    f"[PHASE:NODE_TOOL] tool_execution_start | "
                    f"session_id={session_id} | "
                    f"tool={tool_name} | "
                    f"args={args_preview}"
                )

                result = await self.mcp_call_tool(tool_name, tool_args, config)

                # Structured logging: tool success
                duration_ms = int((time.time() - tool_start) * 1000)
                result_preview = str(result)[:300] if result else "None"

                # Enhanced logging for web_crawl to track timeout issues
                if tool_name == "web_crawl":
                    url = tool_args.get("url", "unknown")
                    self.logger.info(
                        f"[PHASE:NODE_TOOL] web_crawl_complete | "
                        f"session_id={session_id} | "
                        f"url={url} | "
                        f"duration_ms={duration_ms} | "
                        f"result_length={len(str(result))}"
                    )

                self.logger.info(
                    f"[PHASE:NODE_TOOL] tool_execution_complete | "
                    f"session_id={session_id} | "
                    f"tool={tool_name} | "
                    f"status=success | "
                    f"duration_ms={duration_ms} | "
                    f"result_length={len(str(result))} | "
                    f"result_preview='{result_preview}'"
                )

            except Exception as e:
                # Structured logging: tool error
                duration_ms = int((time.time() - tool_start) * 1000)
                error_msg = f"Tool execution failed: {str(e)}"
                self.logger.error(
                    f"tool_call_error | "
                    f"session_id={session_id} | "
                    f"tool={tool_name} | "
                    f"duration_ms={duration_ms} | "
                    f"error={type(e).__name__} | "
                    f"message={str(e)[:200]}",
                    exc_info=True
                )
                
                # Create error tool message
                error_message = ToolMessage(
                    content=error_msg,
                    tool_call_id=tool_call_id
                )
                tool_messages.append(error_message)
                self.stream_tool(tool_name, f"Failed - {str(e)}")
                continue  # Skip to next tool
            
            # Check if this is a HIL response from MCP that needs interrupt handling
            if self._is_hil_response(result):
                self.logger.info(f"🤖 Detected HIL response from {tool_name} - triggering scenario-based HIL")

                # Parse HIL data and determine scenario
                parsed_result = json.loads(result) if isinstance(result, str) and result.startswith('{') else {}
                hil_action = parsed_result.get("action", "ask_human")

                try:
                    # Route to appropriate scenario-based HIL method
                    human_response = await self._handle_hil_scenario(
                        hil_action=hil_action,
                        parsed_result=parsed_result,
                        tool_name=tool_name,
                        tool_args=tool_args
                    )

                    self.logger.info(f"✅ HIL scenario completed: {hil_action}")

                    # Use human response as the tool result
                    result = str(human_response) if human_response is not None else "No human response received"

                except Exception as e:
                    self.logger.error(f"HIL scenario handling failed: {e}")
                    # Fallback to direct interrupt for backward compatibility
                    hil_data = self._parse_hil_response(result, tool_name, tool_args)
                    self.logger.info(f"🚨 Fallback to direct interrupt for HIL: {hil_data['question'][:50]}...")
                    human_response = interrupt(hil_data)
                    result = str(human_response) if human_response is not None else "No human response received"
            
            # Process normal tool results (only reached if no HIL interrupt)
            try:
                
                # Check for plan_tool and request human validation via HIL service
                if self._is_plan_tool(tool_name, result):
                    # Parse and store execution plan data in state first
                    plan_data = None
                    try:
                        plan_data = json.loads(result)
                        if isinstance(plan_data, dict):
                            if 'data' in plan_data:
                                # Standard MCP execution plan format
                                execution_plan = plan_data['data']
                                state["execution_plan"] = execution_plan
                                state["task_list"] = execution_plan.get('tasks', [])
                                state["execution_mode"] = execution_plan.get('execution_mode', 'sequential')
                                
                                task_count = len(execution_plan.get('tasks', []))
                                exec_mode = execution_plan.get('execution_mode', 'sequential')
                                self.stream_tool(tool_name, f"Execution plan parsed: {task_count} tasks in {exec_mode} mode")
                                
                                # 发射task计划事件
                                self.stream_custom({
                                    "task_planning": {
                                        "plan": execution_plan,
                                        "task_count": task_count,
                                        "execution_mode": exec_mode,
                                        "status": "parsed"
                                    }
                                })
                                
                            elif 'tasks' in plan_data:
                                # Direct tasks format
                                state["task_list"] = plan_data['tasks']
                                state["execution_mode"] = plan_data.get('execution_mode', 'sequential')
                                
                                task_count = len(plan_data['tasks'])
                                exec_mode = plan_data.get('execution_mode', 'sequential')
                                self.stream_tool(tool_name, f"Task list parsed: {task_count} tasks in {exec_mode} mode")
                                
                                # 发射task计划事件
                                self.stream_custom({
                                    "task_planning": {
                                        "tasks": plan_data['tasks'],
                                        "task_count": task_count,
                                        "execution_mode": exec_mode,
                                        "status": "parsed"
                                    }
                                })
                                
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Could not parse execution plan JSON: {e}")
                    
                    # CO-PLAN: Use existing HIL service for human validation
                    self.stream_tool(tool_name, "Plan detected - requesting human validation...")
                    
                    # Create human-friendly plan summary for validation
                    plan_summary = self._create_plan_summary(state.get('task_list', []), state.get('execution_mode', 'sequential'))
                    
                    # Use existing HIL service ask_human_with_interrupt for custom plan validation
                    # This gives us more control than approve_or_reject for the modify option
                    plan_validation_question = f"""Review this execution plan before starting autonomous execution:

{plan_summary}

Options:
• Type 'approve' to start execution immediately
• Type 'reject' to cancel and try a different approach  
• Type 'modify' to edit the plan before execution

Your choice:"""
                    
                    # IMPORTANT: Don't wrap interrupt() in try-except - let it propagate to pause graph
                    human_response = hil_service.ask_human_with_interrupt(
                        question=plan_validation_question,
                        context=json.dumps({
                            "task_count": len(state.get('task_list', [])),
                            "execution_mode": state.get('execution_mode', 'sequential'),
                            "tool_name": tool_name,
                            "raw_plan": plan_data
                        }, indent=2),
                        node_source="tool_node"
                    )
                    
                    # Parse human response for plan validation
                    response_str = str(human_response).lower().strip() if human_response else "reject"
                    
                    # Handle human response
                    if response_str == "approve":
                        state["next_action"] = "agent_executor"
                        self.stream_tool(tool_name, "✅ Plan approved by human - routing to autonomous execution")
                        
                        # 发射task状态更新事件
                        self.stream_custom({
                            "task_status_update": {
                                "status": "approved",
                                "next_action": "agent_executor",
                                "task_count": len(state.get('task_list', [])),
                                "message": "Plan approved by human"
                            }
                        })
                    elif response_str == "modify":
                        # Plan modification requested - use HIL review_and_edit
                        self.stream_tool(tool_name, "📝 Plan modification requested - opening editor...")
                        
                        try:
                            # Use HIL service review_and_edit for plan modification
                            modified_plan = hil_service.review_and_edit(
                                content_to_review=json.dumps(state.get('task_list', []), indent=2),
                                task_description=f"Modify the execution plan tasks. Original plan had {len(state.get('task_list', []))} tasks in {state.get('execution_mode', 'sequential')} mode.",
                                node_source="tool_node",
                                required_fields=["tasks"]
                            )
                            
                            if modified_plan.get("valid", False):
                                edited_content = modified_plan["edited_content"]
                                
                                # Parse modified plan
                                if isinstance(edited_content, str):
                                    modified_tasks = json.loads(edited_content)
                                else:
                                    modified_tasks = edited_content.get("tasks", [])
                                
                                # Update state with modified plan
                                state["task_list"] = modified_tasks
                                state["execution_plan"]["tasks"] = modified_tasks
                                state["execution_plan"]["total_tasks"] = len(modified_tasks)
                                state["plan_modified"] = True
                                
                                # Route to execution with modified plan
                                state["next_action"] = "agent_executor"
                                self.stream_tool(tool_name, f"✅ Plan modified and approved - {len(modified_tasks)} tasks ready for execution")
                                
                                # 发射task修改事件
                                self.stream_custom({
                                    "task_status_update": {
                                        "status": "modified",
                                        "next_action": "agent_executor",
                                        "task_count": len(modified_tasks),
                                        "message": "Plan modified and approved"
                                    }
                                })
                            else:
                                # Modification failed - back to reasoning
                                state["next_action"] = "call_model"
                                state["modification_error"] = modified_plan.get("error", "Plan modification failed")
                                self.stream_tool(tool_name, f"❌ Plan modification failed - returning to reasoning")
                        except Exception as e:
                            self.logger.error(f"Plan modification error: {e}")
                            state["next_action"] = "call_model"
                            state["modification_error"] = f"Modification error: {str(e)}"
                            self.stream_tool(tool_name, f"⚠️ Plan modification error - returning to reasoning: {e}")
                    else:
                        # Plan rejected - back to reasoning for alternative approach
                        state["next_action"] = "call_model"
                        state["plan_rejected"] = True
                        state["rejection_context"] = "Human rejected the execution plan"
                        self.stream_tool(tool_name, "❌ Plan rejected by human - returning to reasoning")
                        
                        # 发射task拒绝事件
                        self.stream_custom({
                            "task_status_update": {
                                "status": "rejected",
                                "next_action": "call_model",
                                "message": "Plan rejected by human"
                            }
                        })
                        
                        # Clean up plan data since it was rejected
                        state.pop("execution_plan", None)
                        state.pop("task_list", None)
                        state.pop("execution_mode", None)
                
                # Create tool message
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call_id
                )
                tool_messages.append(tool_message)
                
                self.stream_tool(tool_name, f"Completed - {len(str(result))} chars result")
                
            except Exception as e:
                # Check if this is a LangGraph interrupt (not a real error)
                # Interrupts contain 'Interrupt(' in their string representation
                error_str = str(e)
                if 'Interrupt(' in error_str and 'resumable=True' in error_str:
                    # This is a LangGraph interrupt - re-raise it to pause graph execution
                    self.logger.info(f"HIL interrupt detected for {tool_name} - re-raising to pause graph")
                    raise
                
                # Real error - handle normally
                error_msg = f"Tool execution failed: {str(e)}"
                self.logger.error(f"Tool {tool_name} failed: {e}")
                
                # Create error tool message
                error_message = ToolMessage(
                    content=error_msg,
                    tool_call_id=tool_call_id
                )
                tool_messages.append(error_message)
                
                self.stream_tool(tool_name, f"Failed - {str(e)}")
        
        # Return the state update including tool messages
        # The add_messages reducer will automatically append tool responses to existing conversation
        result = {
            "messages": tool_messages,
            "next_action": "call_model"
        }
        
        # Override next action if already set by plan_tool
        if "next_action" in state and state["next_action"] == "agent_executor":
            result["next_action"] = "agent_executor"
            
        return result
    
    def _extract_tool_info(self, tool_call, index: int) -> tuple:
        """Extract tool information from tool_call object or dict"""
        if hasattr(tool_call, 'name'):
            # LangChain ToolCall object
            return (
                tool_call.name,
                tool_call.args,
                getattr(tool_call, 'id', f'call_{index}')
            )
        elif isinstance(tool_call, dict):
            # Dictionary format
            return (
                tool_call.get('name', 'unknown'),
                tool_call.get('args', {}),
                tool_call.get('id', f'call_{index}')
            )
        else:
            # Fallback for unknown formats
            return ('unknown', {}, f'call_{index}')
    
    def _is_plan_tool(self, tool_name: str, result: str) -> bool:
        """
        Check if this is a plan or replan tool that should trigger autonomous execution
        
        Args:
            tool_name: Name of the executed tool
            result: Tool execution result
            
        Returns:
            True if this tool should trigger agent_executor
        """
        # Check for actual MCP tool names
        plan_tools = ['create_execution_plan', 'replan_execution']
        
        if tool_name in plan_tools:
            # Additional check: verify result contains task/plan structure
            try:
                parsed_result = json.loads(result)
                if isinstance(parsed_result, dict):
                    # Look for task/plan indicators
                    plan_indicators = ['tasks', 'plan', 'steps', 'execution_plan', 'data']
                    return any(key in parsed_result for key in plan_indicators)
            except json.JSONDecodeError:
                pass
            
            # If tool name matches, assume it's a plan/replan tool
            return True
        
        return False
    
    def _get_cached_security_level(self, tool_name: str) -> Optional[str]:
        """Get cached security level for tool"""
        cache_key = tool_name
        if cache_key in self._security_level_cache:
            cached_data, timestamp = self._security_level_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_data
            else:
                # Cache expired, remove it
                del self._security_level_cache[cache_key]
        return None
    
    def _cache_security_level(self, tool_name: str, security_level: str):
        """Cache security level for tool"""
        self._security_level_cache[tool_name] = (security_level, time.time())
    
    async def _batch_check_tool_authorization(
        self, 
        tool_names: List[str], 
        config: RunnableConfig
    ) -> Dict[str, Tuple[str, bool]]:
        """
        Batch check authorization for multiple tools
        
        Args:
            tool_names: List of tool names to check
            config: Runtime config with user context
            
        Returns:
            Dict mapping tool_name to (security_level, needs_authorization)
        """
        results = {}
        tools_to_query = []
        
        # Check cache first
        for tool_name in tool_names:
            cached_level = self._get_cached_security_level(tool_name)
            if cached_level:
                needs_auth = cached_level in ['HIGH', 'CRITICAL']
                results[tool_name] = (cached_level, needs_auth)
                self.logger.debug(f"📋 Cached security level for {tool_name}: {cached_level}")
            else:
                tools_to_query.append(tool_name)
        
        # Batch query remaining tools
        if tools_to_query:
            try:
                # Get security levels for all uncached tools
                batch_levels = await self._batch_get_security_levels(tools_to_query, config)
                
                for tool_name in tools_to_query:
                    security_level = batch_levels.get(tool_name, "LOW")  # Default to LOW
                    self._cache_security_level(tool_name, security_level)
                    needs_auth = security_level in ['HIGH', 'CRITICAL']
                    results[tool_name] = (security_level, needs_auth)
                    self.logger.debug(f"🔍 Queried security level for {tool_name}: {security_level}")
            
            except Exception as e:
                self.logger.error(f"Batch authorization check failed: {e}")
                # IMPORTANT: Fail-safe to HIGH security when checks fail
                self.logger.warning(f"⚠️ Authorization check failed - requiring authorization for all tools for safety")
                for tool_name in tools_to_query:
                    results[tool_name] = ("HIGH", True)  # Require authorization when uncertain
        
        return results
    
    async def _batch_get_security_levels(
        self, 
        tool_names: List[str], 
        config: RunnableConfig
    ) -> Dict[str, str]:
        """Get security levels for multiple tools in one MCP call"""
        try:
            # Use base_node method to get all security levels at once
            self.logger.info(f"🔍 Fetching security levels for tools: {tool_names}")
            security_data = await self.mcp_get_tool_security_levels(config)
            self.logger.info(f"📊 Security data received: {list(security_data.keys())}")
            
            tools_info = security_data.get("tools", {})
            self.logger.info(f"📋 Found {len(tools_info)} tools in security data")
            
            result = {}
            for tool_name in tool_names:
                tool_data = tools_info.get(tool_name, {})
                if tool_data:
                    security_level = tool_data.get('security_level', 'LOW')
                    self.logger.info(f"  🔑 {tool_name}: {security_level} (auth required: {tool_data.get('requires_authorization', False)})")
                    result[tool_name] = security_level
                else:
                    self.logger.warning(f"  ⚠️ {tool_name}: Not found in security data, defaulting to LOW")
                    result[tool_name] = "LOW"
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to get batch security levels: {e}")
            # IMPORTANT: For security, we should fail-safe to HIGH rather than LOW
            # This ensures authorization is required when security checks fail
            self.logger.warning(f"⚠️ Security check failed - defaulting to HIGH security for safety")
            result = {}
            for tool_name in tool_names:
                try:
                    # Try individual query as fallback
                    level = await self.mcp_get_tool_security_level(tool_name, config)
                    if level:
                        self.logger.info(f"  🔐 {tool_name}: Individual query returned {level}")
                        result[tool_name] = level
                    else:
                        # If we can't determine security, assume HIGH for safety
                        self.logger.warning(f"  🔐 {tool_name}: No security level found, defaulting to HIGH for safety")
                        result[tool_name] = "HIGH"
                except Exception as e2:
                    # On any error, default to HIGH security
                    self.logger.error(f"  🔐 {tool_name}: Security query failed ({e2}), defaulting to HIGH")
                    result[tool_name] = "HIGH"
            return result
    
    async def _request_batch_authorization(
        self, 
        high_security_tools: List[Tuple[str, str]], 
        config: RunnableConfig
    ):
        """
        Request authorization for multiple high-security tools at once
        
        Args:
            high_security_tools: List of (tool_name, security_level) tuples
            config: Runtime config with user context
        """
        if not high_security_tools:
            return
        
        user_id = self.get_user_id(config)
        
        # Create batch authorization request
        tool_list = "\n".join([
            f"- {tool_name} (Security: {level})"
            for tool_name, level in high_security_tools
        ])
        
        authorization_request = {
            "type": "batch_tool_authorization",
            "tools": high_security_tools,
            "user_id": user_id,
            "message": f"Multiple tools require authorization:\n\n{tool_list}\n\nDo you approve execution of all these tools?"
        }
        
        self.logger.info(f"🚨 Batch authorization request for {len(high_security_tools)} tools")
        # Use LangGraph interrupt() for human-in-the-loop authorization
        interrupt(authorization_request)
    
    def clear_security_cache(self):
        """Clear the security level cache (useful for testing or cache invalidation)"""
        self._security_level_cache.clear()
        self.logger.info("🧹 Security level cache cleared")
    
    def _is_hil_response(self, result: str) -> bool:
        """
        Check if MCP tool result indicates a Human-in-the-Loop request

        Args:
            result: String result from MCP tool

        Returns:
            True if this is a HIL response that needs interrupt handling
        """
        try:
            if isinstance(result, str) and result.startswith('{'):
                parsed = json.loads(result)
                if isinstance(parsed, dict):
                    # Check for HIL indicators (including Web Automation and Composio HIL)
                    return (
                        # Legacy HIL indicators
                        parsed.get("status") == "human_input_requested" or
                        parsed.get("action") == "ask_human" or
                        parsed.get("status") == "authorization_requested" or
                        # Composio OAuth HIL
                        parsed.get("status") == "oauth_required" or
                        # Web Automation HIL indicators
                        parsed.get("action") == "request_authorization" or
                        parsed.get("status") == "authorization_required" or
                        parsed.get("status") == "credential_required" or
                        parsed.get("status") == "human_required" or
                        parsed.get("hil_required") == True
                    )
        except (json.JSONDecodeError, TypeError):
            pass
        return False

    async def _handle_hil_scenario(
        self,
        hil_action: str,
        parsed_result: dict,
        tool_name: str,
        tool_args: dict
    ) -> Any:
        """
        Route HIL request to appropriate scenario-based method

        Args:
            hil_action: HIL action type from MCP response
            parsed_result: Parsed MCP response
            tool_name: Name of tool that triggered HIL
            tool_args: Tool arguments

        Returns:
            Human response after HIL interaction
        """
        hil_data = parsed_result.get("data", {})
        message = parsed_result.get("message", "Human input required")
        status = parsed_result.get("status", "")
        user_id = hil_data.get("user_id", "default")

        # Scenario 4a: Web Automation - Request Credential Usage
        if hil_action == "request_authorization" and status == "authorization_required":
            self.logger.info(f"📋 HIL Scenario 4a: Request credential usage for {tool_name}")

            provider = hil_data.get("provider", "unknown")
            credential_preview = hil_data.get("credential_preview", {})
            auth_type = hil_data.get("auth_type", "unknown")
            context = hil_data.get("details", "")

            # Call scenario-based HIL method
            approved = await hil_service.request_credential_usage(
                provider=provider,
                credential_preview=credential_preview,
                auth_type=auth_type,
                context=context,
                user_id=user_id,
                node_source="tool_node"
            )

            return {
                "approved": approved,
                "action": "credential_usage_decision",
                "message": f"Credential usage {'approved' if approved else 'denied'}"
            }

        # Scenario 4b: Web Automation - Request Manual Intervention
        elif hil_action == "ask_human" and status in ["credential_required", "human_required"]:
            self.logger.info(f"🙋 HIL Scenario 4b: Request manual intervention for {tool_name}")

            intervention_type = hil_data.get("intervention_type", "unknown")
            provider = hil_data.get("provider", "unknown")
            instructions = hil_data.get("instructions", message)
            screenshot_path = hil_data.get("screenshot", None)
            oauth_url = hil_data.get("oauth_url", None)
            context = hil_data.get("details", "")

            # Call scenario-based HIL method
            human_response = await hil_service.request_manual_intervention(
                intervention_type=intervention_type,
                provider=provider,
                instructions=instructions,
                context=context,
                screenshot_path=screenshot_path,
                oauth_url=oauth_url,
                user_id=user_id,
                node_source="tool_node"
            )

            return human_response

        # Scenario 1: Collect User Input (Legacy ask_human)
        elif hil_action == "ask_human" and status == "human_input_requested":
            self.logger.info(f"📝 HIL Scenario 1: Collect user input for {tool_name}")

            question = hil_data.get("question", message)
            context = hil_data.get("context", "")

            # Call scenario-based HIL method
            user_input = await hil_service.collect_user_input(
                question=question,
                context=context,
                user_id=user_id,
                node_source="tool_node"
            )

            return user_input

        # SCENARIO 3: OAuth Required (Composio - direct oauth_required status)
        elif status == "oauth_required":
            self.logger.info(f"🔐 HIL Scenario 3: OAuth required for {tool_name}")
            
            # Extract OAuth info from parsed result
            app_name = parsed_result.get("app_name", hil_data.get("app", "unknown"))
            oauth_url = parsed_result.get("oauth_url", "")
            instructions = parsed_result.get("instructions", message)
            
            # Call OAuth HIL method
            oauth_result = await hil_service.request_oauth_authorization(
                provider=app_name,
                oauth_url=oauth_url,
                scopes=None,
                context=f"{instructions}\n\n{parsed_result.get('context', '')}",
                user_id=user_id,
                node_source="tool_node"
            )
            
            return {
                "authorized": oauth_result.get("authorized", True),
                "oauth_result": oauth_result,
                "oauth_url": oauth_url,
                "message": f"OAuth {app_name} authorization completed"
            }
        
        # Scenario 2/3: Authorization requested - check if OAuth or Tool permission  
        elif status == "authorization_requested":
            request_type = hil_data.get("request_type")
            
            # SCENARIO 3: OAuth Authorization (Composio - request_type indicator)
            if request_type == "oauth_authorization":
                self.logger.info(f"🔐 HIL Scenario 3: OAuth authorization for {tool_name}")
                
                app_name = hil_data.get("app", "unknown")
                scope = hil_data.get("scope", "default")
                oauth_url = hil_data.get("oauth_url", f"https://backend.composio.dev/oauth/{app_name}")
                
                # Call OAuth HIL method
                oauth_result = await hil_service.request_oauth_authorization(
                    provider=app_name,
                    oauth_url=oauth_url,
                    scopes=[scope] if scope else None,
                    context=message,
                    user_id=user_id,
                    node_source="tool_node"
                )
                
                return {
                    "authorized": oauth_result.get("authorized", True),
                    "oauth_result": oauth_result,
                    "message": f"OAuth {app_name} {'authorized' if oauth_result.get('authorized') else 'denied'}"
                }
            
            # SCENARIO 2: Tool Permission (Regular authorization)
            else:
                self.logger.info(f"🔐 HIL Scenario 2: Request tool permission for {tool_name}")
                
                reason = hil_data.get("reason", message)
                security_level = hil_data.get("security_level", "HIGH")
                
                # Call scenario-based HIL method
                authorized = await hil_service.request_tool_permission(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    security_level=security_level,
                    reason=reason,
                    user_id=user_id,
                    node_source="tool_node"
                )
                
                return {
                    "authorized": authorized,
                    "message": f"Tool {tool_name} {'authorized' if authorized else 'denied'}"
                }

        # Fallback: Use generic interrupt for unrecognized scenarios
        else:
            self.logger.warning(f"⚠️ Unrecognized HIL scenario: action={hil_action}, status={status}")
            # Fallback to direct interrupt
            interrupt_data = self._parse_hil_response(json.dumps(parsed_result), tool_name, tool_args)
            return interrupt(interrupt_data)
    
    def _parse_hil_response(self, result: str, tool_name: str, tool_args: dict) -> dict:
        """
        Parse HIL response from MCP tool and create interrupt data
        
        Args:
            result: MCP tool result containing HIL request
            tool_name: Name of the tool that triggered HIL
            tool_args: Original tool arguments
            
        Returns:
            Interrupt data for LangGraph
        """
        try:
            parsed = json.loads(result)
            hil_data = parsed.get("data", {})
            
            # Create standardized interrupt data
            interrupt_data = {
                "type": "ask_human",
                "tool_name": tool_name,
                "tool_args": tool_args,
                "question": hil_data.get("question", "Human input required"),
                "context": hil_data.get("context", ""),
                "user_id": hil_data.get("user_id", "default"),
                "instruction": hil_data.get("instruction", "Please provide input to continue"),
                "timestamp": parsed.get("timestamp"),
                "original_response": parsed
            }
            
            # Handle authorization requests
            if parsed.get("status") == "authorization_requested":
                interrupt_data["type"] = "authorization"
                interrupt_data["question"] = f"Authorize {tool_name}?"
                interrupt_data["context"] = hil_data.get("reason", "Authorization required")
            
            # Handle OAuth required (Composio)
            elif parsed.get("status") == "oauth_required":
                interrupt_data["type"] = "oauth_authorization"
                interrupt_data["provider"] = parsed.get("app_name", "unknown")
                interrupt_data["oauth_url"] = parsed.get("oauth_url", "")
                interrupt_data["question"] = parsed.get("message", f"Authorize {parsed.get('app_name')}?")
                interrupt_data["instructions"] = parsed.get("instructions", "")
            
            return interrupt_data
            
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.error(f"Failed to parse HIL response: {e}")
            # Fallback interrupt data
            return {
                "type": "ask_human",
                "tool_name": tool_name,
                "question": "Human input required (parse error)",
                "context": f"Failed to parse response: {str(result)[:200]}...",
                "timestamp": None
            }
    
    def _process_human_response(self, human_response: any, hil_data: dict) -> str:
        """
        Process human response from interrupt and return appropriate tool result
        
        Args:
            human_response: Response from human via interrupt/resume cycle
            hil_data: Original HIL interrupt data
            
        Returns:
            Processed result string
        """
        try:
            # Handle different types of human responses
            if isinstance(human_response, dict):
                if "user_input" in human_response:
                    # Direct user input
                    return human_response["user_input"]
                elif "approved" in human_response:
                    # Authorization response
                    if human_response["approved"]:
                        return f"Authorization approved for {hil_data['tool_name']}"
                    else:
                        return f"Authorization denied for {hil_data['tool_name']}"
                else:
                    # Generic dict response
                    return json.dumps(human_response)
            elif isinstance(human_response, str):
                # Direct string response
                return human_response
            else:
                # Convert other types to string
                return str(human_response)
                
        except Exception as e:
            self.logger.error(f"Failed to process human response: {e}")
            return f"Human response received but processing failed: {str(e)}"
    
    def _create_plan_summary(self, task_list: List[Dict], execution_mode: str) -> str:
        """
        Create human-friendly summary of execution plan for validation
        
        Args:
            task_list: List of tasks from the execution plan
            execution_mode: Mode of execution (sequential, parallel, etc.)
            
        Returns:
            Human-readable plan summary
        """
        if not task_list:
            return "Empty execution plan"
        
        summary_parts = []
        summary_parts.append(f"**Execution Plan Summary**")
        summary_parts.append(f"• Mode: {execution_mode.title()}")
        summary_parts.append(f"• Total Tasks: {len(task_list)}")
        summary_parts.append("")
        
        for i, task in enumerate(task_list, 1):
            task_title = task.get('title', f'Task {i}')
            task_desc = task.get('description', 'No description')
            task_tools = task.get('tools', [])
            
            summary_parts.append(f"**{i}. {task_title}**")
            summary_parts.append(f"   Description: {task_desc}")
            
            if task_tools:
                tools_str = ", ".join(task_tools)
                summary_parts.append(f"   Tools: {tools_str}")
            
            # Add priority if available
            if task.get('priority'):
                summary_parts.append(f"   Priority: {task['priority']}")
            
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    # Removed all mode-related methods - keeping tool execution simple

    # =============================================================================
    # PHASE 1 & 2: LONG-RUNNING TASK DETECTION + BACKGROUND JOB QUEUE
    # =============================================================================

    def _detect_long_running_task(self, tool_info_list: List[Tuple[str, dict, str]]) -> Optional[dict]:
        """
        Detect if the tool execution will be long-running

        Returns:
            dict with task info if long-running, None otherwise
        """
        # Count web_crawl calls (each takes 10-15s)
        web_crawls = [t for t in tool_info_list if t[0] == "web_crawl"]

        # Lower threshold: 3+ crawls (~36s) warrants user choice
        if len(web_crawls) >= 3:
            estimated_time = len(web_crawls) * 12  # 12s average per crawl
            return {
                "task_type": "web_crawling",
                "tool_count": len(web_crawls),
                "estimated_time_seconds": estimated_time,
                "sources": [t[1].get("url", "unknown") for t in web_crawls]
            }

        # Also detect many web_search calls (less intensive but adds up)
        web_searches = [t for t in tool_info_list if t[0] == "web_search"]
        if len(web_searches) >= 5:  # Lowered from 8 to 5 (15s+ total)
            estimated_time = len(web_searches) * 3  # 3s average per search
            return {
                "task_type": "web_searching",
                "tool_count": len(web_searches),
                "estimated_time_seconds": estimated_time,
                "queries": [t[1].get("query", "unknown") for t in web_searches]
            }

        return None

    async def _offer_execution_choice(self, task_info: dict, config: RunnableConfig) -> str:
        """
        Offer user choice: quick (limited), comprehensive (wait), or background (async)

        Returns:
            "quick" | "comprehensive" | "background"
        """
        from ..services.hil_service import hil_service

        estimated_time = task_info["estimated_time_seconds"]
        tool_count = task_info["tool_count"]

        question = f"""🕐 Long-running task detected: {tool_count} web crawls (~{estimated_time}s total)

Choose execution mode:
• Type 'quick' - Fast response (3 sources, ~30s)
• Type 'comprehensive' - Wait for all {tool_count} sources (~{estimated_time}s)
• Type 'background' - Run in background, get job_id immediately

Your choice:"""

        try:
            response = hil_service.ask_human_with_interrupt(
                question=question,
                context=json.dumps(task_info, indent=2),
                node_source="tool_node"
            )

            choice = str(response).lower().strip()

            if choice in ["quick", "q"]:
                self.logger.info(f"✅ User chose QUICK execution mode")
                return "quick"
            elif choice in ["background", "bg", "b"]:
                self.logger.info(f"✅ User chose BACKGROUND execution mode")
                return "background"
            else:
                self.logger.info(f"✅ User chose COMPREHENSIVE execution mode (default)")
                return "comprehensive"

        except Exception as e:
            self.logger.error(f"HIL choice failed: {e}, defaulting to comprehensive")
            return "comprehensive"

    def _optimize_for_quick_execution(self, tool_info_list: List[Tuple[str, dict, str]]) -> List[Tuple[str, dict, str]]:
        """
        Optimize tool list for quick execution (limit web_crawls to 3)
        """
        web_crawls = [t for t in tool_info_list if t[0] == "web_crawl"]
        other_tools = [t for t in tool_info_list if t[0] != "web_crawl"]

        # Keep only first 3 web_crawls (usually the most reliable sources)
        limited_crawls = web_crawls[:3]

        self.logger.info(f"🚀 Quick mode: Limited from {len(web_crawls)} to {len(limited_crawls)} web_crawls")

        return other_tools + limited_crawls

    async def _queue_background_job(self, tool_info_list: List[Tuple[str, dict, str]], state: dict, config: RunnableConfig) -> dict:
        """
        Queue tools as background job and return job_id

        Returns:
            dict with job_id and status URL
        """
        import uuid
        from datetime import datetime

        job_id = f"job_{uuid.uuid4().hex[:12]}"
        session_id = state.get("session_id", "unknown")

        # Prepare job data
        job_data = {
            "job_id": job_id,
            "session_id": session_id,
            "tools": [
                {
                    "tool_name": t[0],
                    "tool_args": t[1],
                    "tool_call_id": t[2]
                }
                for t in tool_info_list
            ],
            "created_at": datetime.now().isoformat(),
            "status": "queued"
        }

        try:
            # Try to use Celery if available
            from ..services.background_job_service import queue_tool_execution_job

            celery_task = queue_tool_execution_job.delay(job_data, dict(config))

            self.logger.info(
                f"background_job_queued | "
                f"job_id={job_id} | "
                f"session_id={session_id} | "
                f"celery_task_id={celery_task.id} | "
                f"tool_count={len(tool_info_list)}"
            )

            return {
                "status": "queued",
                "job_id": job_id,
                "celery_task_id": celery_task.id,
                "message": f"Background job queued with {len(tool_info_list)} tools",
                "poll_url": f"/api/v1/jobs/{job_id}",
                "sse_url": f"/api/v1/jobs/{job_id}/stream",
                "estimated_completion": f"{len(tool_info_list) * 12}s"
            }

        except ImportError:
            # Fallback: Store in Redis directly without Celery
            self.logger.warning("Celery not available, using Redis fallback")

            try:
                import redis
                r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

                # Store job data in Redis
                r.setex(f"job:{job_id}", 3600, json.dumps(job_data))  # 1 hour TTL

                self.logger.info(
                    f"background_job_stored | "
                    f"job_id={job_id} | "
                    f"session_id={session_id} | "
                    f"backend=redis | "
                    f"tool_count={len(tool_info_list)}"
                )

                return {
                    "status": "queued",
                    "job_id": job_id,
                    "message": f"Background job queued (Redis) with {len(tool_info_list)} tools",
                    "poll_url": f"/api/v1/jobs/{job_id}",
                    "estimated_completion": f"{len(tool_info_list) * 12}s",
                    "note": "Celery not available, using Redis storage only"
                }

            except Exception as redis_error:
                self.logger.error(f"Redis storage failed: {redis_error}")

                # Final fallback: return synchronous execution
                return {
                    "status": "fallback_to_sync",
                    "job_id": job_id,
                    "message": "Background queue unavailable, executing synchronously",
                    "note": "Neither Celery nor Redis available"
                }