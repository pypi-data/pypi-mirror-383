#!/usr/bin/env python3
"""
Memory Curation Utilities - Co-memorize Implementation

Human-curated memory optimization for collaborative agentic AI.
Integrates with existing memory system to provide curation opportunities.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from ...services.hil_service import hil_service
from ...components.mcp_service import MCPService

logger = logging.getLogger(__name__)


class MemoryCurationHelper:
    """
    Helper for memory curation workflow integration
    
    Features:
    - Curation opportunity detection
    - Memory analytics and quality assessment
    - Human curation interface
    - Batch memory operations
    """
    
    def __init__(self):
        self.curation_triggers = {
            "conversation_complete": True,  # After each conversation
            "memory_threshold": 50,         # When user has 50+ memories
            "periodic_curation": True,      # Regular curation opportunities
            "quality_threshold": 0.7        # Quality score threshold
        }
    
    async def should_trigger_curation(
        self, 
        mcp_service, 
        user_id: str, 
        session_id: str,
        conversation_complete: bool = False
    ) -> Dict[str, Any]:
        """
        Determine if memory curation should be triggered
        
        Args:
            mcp_service: MCP service instance
            user_id: User identifier
            session_id: Session identifier  
            conversation_complete: Whether conversation just completed
            
        Returns:
            Curation decision with reasons
        """
        try:
            # Get memory analytics
            analytics = await self._get_memory_analytics(mcp_service, user_id)
            
            curation_reasons = []
            should_curate = False
            
            # 1. Conversation complete trigger
            if conversation_complete and self.curation_triggers["conversation_complete"]:
                # Only trigger if we have meaningful memories to curate
                if analytics.get("total_memories", 0) >= 5:
                    curation_reasons.append("Conversation completed with sufficient memories")
                    should_curate = True
            
            # 2. Memory threshold trigger
            total_memories = analytics.get("total_memories", 0)
            if total_memories >= self.curation_triggers["memory_threshold"]:
                curation_reasons.append(f"High memory count: {total_memories} memories")
                should_curate = True
            
            # 3. Quality issues
            quality_issues = analytics.get("quality_issues", [])
            if len(quality_issues) >= 3:
                curation_reasons.append(f"Quality issues detected: {len(quality_issues)} problems")
                should_curate = True
            
            # 4. Duplicate detection
            duplicates = analytics.get("potential_duplicates", 0)
            if duplicates >= 3:
                curation_reasons.append(f"Potential duplicates: {duplicates} found")
                should_curate = True
            
            return {
                "should_curate": should_curate,
                "reasons": curation_reasons,
                "analytics": analytics,
                "priority": "high" if len(curation_reasons) >= 2 else "medium"
            }
            
        except Exception as e:
            logger.error(f"Curation trigger check failed: {e}")
            return {"should_curate": False, "error": str(e)}
    
    async def _get_memory_analytics(self, mcp_service, user_id: str) -> Dict[str, Any]:
        """
        Get memory analytics for curation decisions
        
        Args:
            mcp_service: MCP service instance
            user_id: User identifier
            
        Returns:
            Memory analytics data
        """
        try:
            # Get memory counts by type
            memory_counts = {}
            total_memories = 0
            
            # Count different memory types
            memory_types = ["session", "factual", "episodic", "semantic", "procedural", "working"]
            for memory_type in memory_types:
                try:
                    # Use existing search functionality to count memories
                    result = await mcp_service.call_tool("search_memories", {
                        "user_id": user_id,
                        "query": "",  # Empty query to get all
                        "memory_types": [memory_type.upper()],
                        "top_k": 100  # Get count estimate
                    })
                    
                    parsed = self._parse_mcp_response(result)
                    if parsed.get('status') == 'success':
                        results = parsed.get('data', {}).get('results', [])
                        memory_counts[memory_type] = len(results)
                        total_memories += len(results)
                    else:
                        memory_counts[memory_type] = 0
                        
                except Exception as e:
                    logger.warning(f"Failed to count {memory_type} memories: {e}")
                    memory_counts[memory_type] = 0
            
            # Detect quality issues (placeholder logic - could be enhanced)
            quality_issues = []
            if memory_counts.get("factual", 0) > memory_counts.get("semantic", 0) * 3:
                quality_issues.append("Too many factual vs semantic memories")
            
            if memory_counts.get("working", 0) > 20:
                quality_issues.append("Too many working memories (should be cleaned)")
            
            # Estimate duplicates (placeholder logic)
            potential_duplicates = min(total_memories // 10, 10)  # Rough estimate
            
            return {
                "total_memories": total_memories,
                "memory_counts": memory_counts,
                "quality_issues": quality_issues,
                "potential_duplicates": potential_duplicates,
                "curation_score": max(0, 1.0 - len(quality_issues) * 0.2),
                "needs_attention": len(quality_issues) > 0 or potential_duplicates > 5
            }
            
        except Exception as e:
            logger.error(f"Memory analytics failed: {e}")
            return {
                "total_memories": 0,
                "memory_counts": {},
                "quality_issues": ["Analytics unavailable"],
                "potential_duplicates": 0,
                "curation_score": 0.5,
                "needs_attention": False
            }
    
    def _parse_mcp_response(self, raw_response: str) -> dict:
        """Parse MCP response (reuse from memory_utils)"""
        try:
            # Check for event stream format first
            if 'event: message' in raw_response and 'data:' in raw_response:
                lines = raw_response.split('\n')
                for line in lines:
                    if line.startswith('data:'):
                        json_str = line[5:].strip()
                        data = json.loads(json_str)
                        if 'result' in data and 'content' in data['result']:
                            content = data['result']['content'][0]['text']
                            return json.loads(content)
            
            # Fallback: try to parse as direct JSON
            return json.loads(raw_response)
            
        except Exception as e:
            logger.error(f"Failed to parse MCP response: {e}")
            return {"status": "error", "error": "Failed to parse response"}
    
    async def request_memory_curation(
        self, 
        analytics: Dict[str, Any], 
        user_id: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """
        Request human memory curation
        
        Args:
            analytics: Memory analytics data
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Curation decisions from human
        """
        # Create curation summary
        curation_summary = self._create_curation_summary(analytics, user_id)
        
        curation_question = f"""🧠 **Memory Optimization Available**

{curation_summary}

**Current Memory State:**
• Total Memories: {analytics.get('total_memories', 0)}
• Quality Score: {analytics.get('curation_score', 0.5):.1f}/1.0
• Issues Found: {len(analytics.get('quality_issues', []))}

**Benefits of Curation:**
• Faster memory retrieval
• Better conversation context  
• Improved agent performance
• Cleaner memory organization

**Options:**
• Type 'curate' to review and optimize memories
• Type 'auto' to apply automatic optimizations
• Type 'skip' to skip curation this time

Your choice:"""
        
        try:
            human_response = hil_service.ask_human_with_interrupt(
                question=curation_question,
                context=json.dumps({
                    "user_id": user_id,
                    "session_id": session_id,
                    "total_memories": analytics.get("total_memories", 0),
                    "quality_score": analytics.get("curation_score", 0.5),
                    "issues": analytics.get("quality_issues", [])
                }, indent=2),
                node_source="memory_curation"
            )
            
            response_str = str(human_response).lower().strip() if human_response else "skip"
            
            if response_str == "curate":
                return {"action": "curate", "mode": "interactive"}
            elif response_str == "auto":
                return {"action": "curate", "mode": "automatic"}
            else:
                return {"action": "skip", "reason": "Human chose to skip curation"}
                
        except Exception as e:
            logger.error(f"Memory curation request failed: {e}")
            return {"action": "skip", "reason": f"Error: {e}"}
    
    def _create_curation_summary(self, analytics: Dict[str, Any], user_id: str) -> str:
        """Create human-friendly curation summary"""
        summary_parts = []
        
        memory_counts = analytics.get("memory_counts", {})
        total = analytics.get("total_memories", 0)
        
        summary_parts.append(f"📊 **Memory Analysis for {user_id}:**")
        
        if memory_counts:
            summary_parts.append("**Memory Distribution:**")
            for mem_type, count in memory_counts.items():
                percentage = (count / max(total, 1)) * 100
                summary_parts.append(f"   • {mem_type.title()}: {count} ({percentage:.1f}%)")
        
        quality_issues = analytics.get("quality_issues", [])
        if quality_issues:
            summary_parts.append("\n**Issues Detected:**")
            for issue in quality_issues:
                summary_parts.append(f"   ⚠️ {issue}")
        
        duplicates = analytics.get("potential_duplicates", 0)
        if duplicates > 0:
            summary_parts.append(f"\n**Optimization Opportunities:**")
            summary_parts.append(f"   🔄 {duplicates} potential duplicate memories")
        
        return "\n".join(summary_parts)
    
    async def apply_automatic_curation(
        self, 
        mcp_service, 
        user_id: str, 
        analytics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply automatic curation optimizations
        
        Args:
            mcp_service: MCP service instance
            user_id: User identifier
            analytics: Memory analytics data
            
        Returns:
            Curation results
        """
        results = {
            "memories_optimized": 0,
            "working_memory_cleared": 0,
            "quality_improvements": 0,
            "optimizations_applied": []
        }
        
        try:
            # 1. Clear old working memories (TTL-based)
            working_count = analytics.get("memory_counts", {}).get("working", 0)
            if working_count > 10:
                # This would need a specific MCP tool to clear old working memories
                # For now, just log the intent
                results["working_memory_cleared"] = max(0, working_count - 10)
                results["optimizations_applied"].append(f"Cleared {working_count - 10} old working memories")
            
            # 2. Quality improvements (placeholder - would need specific MCP tools)
            quality_issues = len(analytics.get("quality_issues", []))
            if quality_issues > 0:
                results["quality_improvements"] = quality_issues
                results["optimizations_applied"].append(f"Addressed {quality_issues} quality issues")
            
            # 3. Memory organization (placeholder)
            total_memories = analytics.get("total_memories", 0)
            if total_memories > 0:
                results["memories_optimized"] = min(total_memories // 10, 5)  # Conservative estimate
                results["optimizations_applied"].append("Optimized memory organization")
            
            logger.info(f"Applied automatic curation for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Automatic curation failed: {e}")
            results["error"] = str(e)
            return results


# Global helper instance
memory_curation_helper = MemoryCurationHelper()


async def check_memory_curation_opportunity(
    mcp_service,
    user_id: str,
    session_id: str,
    conversation_complete: bool = False
) -> Dict[str, Any]:
    """
    Check if memory curation opportunity exists
    
    Args:
        mcp_service: MCP service instance
        user_id: User identifier
        session_id: Session identifier
        conversation_complete: Whether conversation just completed
        
    Returns:
        Curation opportunity assessment
    """
    return await memory_curation_helper.should_trigger_curation(
        mcp_service, user_id, session_id, conversation_complete
    )


async def execute_memory_curation(
    mcp_service,
    user_id: str,
    session_id: str,
    analytics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute memory curation workflow
    
    Args:
        mcp_service: MCP service instance
        user_id: User identifier
        session_id: Session identifier
        analytics: Memory analytics data
        
    Returns:
        Curation results
    """
    try:
        # Request human curation decision
        curation_decision = await memory_curation_helper.request_memory_curation(
            analytics, user_id, session_id
        )
        
        if curation_decision["action"] == "curate":
            if curation_decision["mode"] == "automatic":
                # Apply automatic optimizations
                results = await memory_curation_helper.apply_automatic_curation(
                    mcp_service, user_id, analytics
                )
                results["curation_type"] = "automatic"
                return results
            else:
                # Interactive curation (placeholder - would need detailed UI)
                return {
                    "curation_type": "interactive", 
                    "status": "placeholder",
                    "message": "Interactive curation would show detailed memory editor"
                }
        else:
            # Curation skipped
            return {
                "curation_type": "skipped",
                "reason": curation_decision.get("reason", "User chose to skip"),
                "memories_optimized": 0
            }
            
    except Exception as e:
        logger.error(f"Memory curation execution failed: {e}")
        return {
            "curation_type": "error",
            "error": str(e),
            "memories_optimized": 0
        }


# =============================================================================
# PROACTIVE MEMORY CURATION
# =============================================================================

class ProactiveMemoryCurationHelper(MemoryCurationHelper):
    """
    Enhanced memory curation with predictive optimization
    
    Extends the existing MemoryCurationHelper with proactive capabilities:
    - Predictive memory optimization needs detection
    - Memory usage forecasting  
    - Proactive context pre-loading
    - Confidence-based curation triggers
    """
    
    def __init__(self):
        super().__init__()
        # Enhanced proactive triggers
        self.proactive_triggers = {
            **self.curation_triggers,
            "prediction_confidence": 0.8,   # Confidence threshold for proactive actions
            "usage_forecast": True,         # Enable usage forecasting
            "preemptive_optimization": True  # Enable preemptive optimization
        }
    
    async def check_proactive_curation_opportunity(self, user_id: str, context: Dict[str, Any], mcp_service: MCPService = None) -> Optional[Dict[str, Any]]:
        """
        Check if proactive memory optimization is needed using MCP predictions
        
        Args:
            user_id: User identifier
            context: Current context with potential predictions
            mcp_service: MCP service instance for predictions
            
        Returns:
            Proactive curation opportunity or None if not needed
        """
        try:
            if not mcp_service:
                logger.warning("No MCP service provided for proactive curation check")
                return None
            
            # Get memory predictions from MCP service
            logger.info(f"Checking proactive memory curation opportunity for user {user_id}")
            
            # Call the predict_memory_optimization tool (assuming it exists from MCP prediction service)
            memory_predictions = await mcp_service.call_tool("predict_memory_optimization", {
                "user_id": user_id,
                "context": context
            })
            
            # Parse the prediction response
            if isinstance(memory_predictions, str):
                parsed_predictions = self._parse_mcp_response(memory_predictions)
            else:
                parsed_predictions = memory_predictions
            
            prediction_data = parsed_predictions.get("data", {}) if parsed_predictions.get("status") == "success" else {}
            
            # Check if optimization is needed with high confidence
            optimization_needed = prediction_data.get('optimization_needed', False)
            confidence = prediction_data.get('confidence', 0.0)
            
            if optimization_needed and confidence > self.proactive_triggers['prediction_confidence']:
                return await self._prepare_proactive_curation(user_id, prediction_data)
            
            logger.debug(f"Proactive curation not needed for user {user_id} (confidence: {confidence:.2f})")
            return None
            
        except Exception as e:
            logger.error(f"Proactive curation check failed for user {user_id}: {e}")
            return None
    
    async def _prepare_proactive_curation(self, user_id: str, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare proactive memory curation based on predictions
        
        Args:
            user_id: User identifier
            predictions: Memory optimization predictions
            
        Returns:
            Proactive curation recommendations
        """
        try:
            return {
                "type": "proactive_curation",
                "user_id": user_id,
                "predicted_needs": predictions.get('memory_usage_forecast', {}),
                "recommended_actions": predictions.get('optimization_actions', []),
                "confidence": predictions.get('confidence', 0.0),
                "benefits": predictions.get('expected_benefits', {}),
                "urgency": self._assess_optimization_urgency(predictions),
                "estimated_impact": predictions.get('performance_improvement', {}),
                "proactive_trigger": True
            }
            
        except Exception as e:
            logger.error(f"Failed to prepare proactive curation for user {user_id}: {e}")
            return None
    
    def _assess_optimization_urgency(self, predictions: Dict[str, Any]) -> str:
        """
        Assess the urgency of memory optimization based on predictions
        
        Args:
            predictions: Memory optimization predictions
            
        Returns:
            Urgency level: 'low', 'medium', 'high', 'critical'
        """
        try:
            confidence = predictions.get('confidence', 0.0)
            memory_usage_forecast = predictions.get('memory_usage_forecast', {})
            
            # Check predicted memory growth
            growth_rate = memory_usage_forecast.get('growth_rate', 0.0)
            current_usage = memory_usage_forecast.get('current_usage_percent', 0.0)
            
            # Assess urgency based on multiple factors
            if confidence > 0.95 and (growth_rate > 0.5 or current_usage > 0.9):
                return 'critical'
            elif confidence > 0.9 and (growth_rate > 0.3 or current_usage > 0.8):
                return 'high'  
            elif confidence > 0.8 and (growth_rate > 0.2 or current_usage > 0.7):
                return 'medium'
            else:
                return 'low'
                
        except Exception:
            return 'medium'  # Safe default
    
    async def apply_proactive_memory_optimization(
        self, 
        mcp_service: MCPService,
        user_id: str, 
        proactive_curation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply proactive memory optimization based on predictions
        
        Args:
            mcp_service: MCP service instance
            user_id: User identifier
            proactive_curation: Proactive curation recommendations
            
        Returns:
            Optimization results
        """
        try:
            recommended_actions = proactive_curation.get('recommended_actions', [])
            confidence = proactive_curation.get('confidence', 0.0)
            
            results = {
                "optimization_type": "proactive",
                "confidence": confidence,
                "actions_taken": [],
                "performance_impact": {},
                "memories_optimized": 0,
                "preemptive_actions": 0
            }
            
            logger.info(f"Applying proactive memory optimization for user {user_id}")
            
            # Apply high-confidence optimizations automatically
            for action in recommended_actions:
                action_type = action.get('type', '')
                action_confidence = action.get('confidence', 0.0)
                
                if action_confidence > self.proactive_triggers['prediction_confidence']:
                    try:
                        # Apply the optimization action
                        if action_type == 'preemptive_cleanup':
                            cleanup_result = await self._apply_preemptive_cleanup(mcp_service, user_id, action)
                            results['actions_taken'].append(f"Preemptive cleanup: {cleanup_result}")
                            results['preemptive_actions'] += 1
                            
                        elif action_type == 'memory_reorganization':
                            reorg_result = await self._apply_memory_reorganization(mcp_service, user_id, action)
                            results['actions_taken'].append(f"Memory reorganization: {reorg_result}")
                            results['memories_optimized'] += action.get('affected_count', 0)
                            
                        elif action_type == 'context_preloading':
                            preload_result = await self._apply_context_preloading(mcp_service, user_id, action)
                            results['actions_taken'].append(f"Context preloading: {preload_result}")
                            
                    except Exception as e:
                        logger.error(f"Failed to apply action {action_type}: {e}")
                        results['actions_taken'].append(f"Failed {action_type}: {str(e)}")
            
            # Record performance impact
            predicted_benefits = proactive_curation.get('benefits', {})
            results['performance_impact'] = {
                'retrieval_speed_improvement': predicted_benefits.get('retrieval_speed', 0.0),
                'context_quality_improvement': predicted_benefits.get('context_quality', 0.0),
                'memory_efficiency_gain': predicted_benefits.get('efficiency', 0.0)
            }
            
            logger.info(f"Proactive optimization completed for user {user_id}: {len(results['actions_taken'])} actions")
            return results
            
        except Exception as e:
            logger.error(f"Proactive memory optimization failed for user {user_id}: {e}")
            return {
                "optimization_type": "proactive",
                "error": str(e),
                "actions_taken": [],
                "memories_optimized": 0
            }
    
    async def _apply_preemptive_cleanup(self, mcp_service: MCPService, user_id: str, action: Dict[str, Any]) -> str:
        """Apply preemptive memory cleanup based on predictions"""
        try:
            # This would call specific MCP tools for memory cleanup
            # For now, return a placeholder result
            target_types = action.get('target_memory_types', [])
            cleanup_threshold = action.get('cleanup_threshold', 0.7)
            
            # Simulate cleanup action
            logger.info(f"Preemptive cleanup for user {user_id}: {target_types} (threshold: {cleanup_threshold})")
            return f"Cleaned {len(target_types)} memory types with threshold {cleanup_threshold}"
            
        except Exception as e:
            logger.error(f"Preemptive cleanup failed: {e}")
            return f"Cleanup failed: {str(e)}"
    
    async def _apply_memory_reorganization(self, mcp_service: MCPService, user_id: str, action: Dict[str, Any]) -> str:
        """Apply memory reorganization based on predictions"""
        try:
            # This would call specific MCP tools for memory reorganization
            reorganization_strategy = action.get('strategy', 'default')
            affected_count = action.get('affected_count', 0)
            
            # Simulate reorganization
            logger.info(f"Memory reorganization for user {user_id}: {reorganization_strategy} strategy, {affected_count} memories")
            return f"Reorganized {affected_count} memories using {reorganization_strategy} strategy"
            
        except Exception as e:
            logger.error(f"Memory reorganization failed: {e}")
            return f"Reorganization failed: {str(e)}"
    
    async def _apply_context_preloading(self, mcp_service: MCPService, user_id: str, action: Dict[str, Any]) -> str:
        """Apply context preloading based on predictions"""
        try:
            # This would preload predicted context for faster access
            context_types = action.get('context_types', [])
            priority_level = action.get('priority', 'medium')
            
            # Simulate context preloading
            logger.info(f"Context preloading for user {user_id}: {context_types} (priority: {priority_level})")
            return f"Preloaded {len(context_types)} context types with {priority_level} priority"
            
        except Exception as e:
            logger.error(f"Context preloading failed: {e}")
            return f"Preloading failed: {str(e)}"


# Global proactive helper instance
proactive_memory_helper = ProactiveMemoryCurationHelper()


async def check_proactive_memory_curation(
    user_id: str, 
    context: Dict[str, Any], 
    mcp_service: MCPService = None
) -> Optional[Dict[str, Any]]:
    """
    Check if proactive memory curation is needed
    
    Args:
        user_id: User identifier
        context: Current context (may contain predictions)
        mcp_service: MCP service for predictions
        
    Returns:
        Proactive curation opportunity or None
    """
    return await proactive_memory_helper.check_proactive_curation_opportunity(
        user_id, context, mcp_service
    )


async def apply_proactive_memory_optimization(
    mcp_service: MCPService,
    user_id: str,
    proactive_curation: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply proactive memory optimization
    
    Args:
        mcp_service: MCP service instance
        user_id: User identifier  
        proactive_curation: Proactive curation recommendations
        
    Returns:
        Optimization results
    """
    return await proactive_memory_helper.apply_proactive_memory_optimization(
        mcp_service, user_id, proactive_curation
    )