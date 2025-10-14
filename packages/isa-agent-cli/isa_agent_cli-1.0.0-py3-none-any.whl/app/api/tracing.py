#!/usr/bin/env python3
"""
追踪API端点 - 基于现有数据库提供请求追踪查询和分析
"""

import logging
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

from ..services.tracing_service import get_tracing_service

logger = logging.getLogger(__name__)

# 创建追踪API路由
tracing_router = APIRouter(prefix="/api/v1/agents/tracing", tags=["tracing"])


class RequestTraceSummary(BaseModel):
    """请求追踪摘要"""
    thread_id: str
    start_time: str
    end_time: Optional[str]
    duration_ms: Optional[int]
    checkpoint_count: int
    total_messages: int
    user_request: str
    status: str


class MessageDetail(BaseModel):
    """消息详情"""
    index: int
    message_type: str
    content_preview: str
    content_length: int
    has_tool_calls: bool
    tool_call_ids: List[str]


class CheckpointDetail(BaseModel):
    """检查点详情"""
    checkpoint_id: str
    version: str
    timestamp: str
    message_count: int
    messages: List[MessageDetail]


class RequestTraceDetail(BaseModel):
    """请求追踪详细信息"""
    thread_id: str
    start_time: str
    end_time: Optional[str]
    duration_ms: Optional[int]
    total_messages: int
    checkpoints: List[CheckpointDetail]
    message_growth: List[int]
    estimated_nodes: List[str]
    timeline: List[Dict[str, Any]]


class NodeStatsItem(BaseModel):
    """节点统计项"""
    node_name: str
    total_executions: int
    avg_duration_ms: float
    min_duration_ms: int
    max_duration_ms: int
    success_rate: float


class NodePerformanceStats(BaseModel):
    """节点性能统计"""
    analysis_period_days: int
    total_requests_analyzed: int
    node_statistics: List[NodeStatsItem]


@tracing_router.get("/requests", response_model=List[RequestTraceSummary])
async def get_recent_requests(
    limit: int = Query(50, ge=1, le=200, description="返回的请求数量限制"),
    hours: int = Query(24, ge=1, le=168, description="时间范围（小时）")
):
    """获取最近的请求追踪列表"""
    try:
        tracing_service = await get_tracing_service()
        traces = await tracing_service.get_recent_traces(limit=limit, hours=hours)
        
        summaries = []
        for trace in traces:
            summaries.append(RequestTraceSummary(
                thread_id=trace['thread_id'],
                start_time=trace['start_time'].isoformat() if trace['start_time'] else "",
                end_time=trace['end_time'].isoformat() if trace['end_time'] else None,
                duration_ms=trace['duration_ms'],
                checkpoint_count=trace['checkpoint_count'],
                total_messages=trace['total_messages'],
                user_request=trace['user_request'],
                status=trace['status']
            ))
        
        return summaries
        
    except Exception as e:
        logger.error(f"Failed to get recent requests: {e}")
        raise HTTPException(status_code=500, detail=f"获取请求列表失败: {str(e)}")


@tracing_router.get("/requests/{thread_id}", response_model=RequestTraceDetail)
async def get_request_detail(
    thread_id: str = Path(..., description="线程ID")
):
    """获取特定请求的详细追踪信息"""
    try:
        tracing_service = await get_tracing_service()
        trace = await tracing_service.get_thread_trace(thread_id)
        
        if not trace:
            raise HTTPException(status_code=404, detail=f"请求追踪 {thread_id} 不存在")
        
        # 转换检查点信息
        checkpoints = []
        for cp in trace.checkpoints:
            messages = []
            for msg in cp.messages:
                messages.append(MessageDetail(
                    index=msg.index,
                    message_type=msg.message_type,
                    content_preview=msg.content_preview,
                    content_length=msg.content_length,
                    has_tool_calls=msg.has_tool_calls,
                    tool_call_ids=msg.tool_call_ids
                ))
            
            checkpoints.append(CheckpointDetail(
                checkpoint_id=cp.checkpoint_id,
                version=cp.version,
                timestamp=cp.timestamp.isoformat() if cp.timestamp else "",
                message_count=cp.message_count,
                messages=messages
            ))
        
        # 生成时间线
        timeline = _generate_request_timeline(trace)
        
        return RequestTraceDetail(
            thread_id=trace.thread_id,
            start_time=trace.start_time.isoformat() if trace.start_time else "",
            end_time=trace.end_time.isoformat() if trace.end_time else None,
            duration_ms=trace.duration_ms,
            total_messages=trace.total_messages,
            checkpoints=checkpoints,
            message_growth=trace.message_growth,
            estimated_nodes=trace.estimated_nodes,
            timeline=timeline
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get request detail: {e}")
        raise HTTPException(status_code=500, detail=f"获取请求详情失败: {str(e)}")


@tracing_router.get("/requests/{thread_id}/timeline")
async def get_request_timeline(
    thread_id: str = Path(..., description="线程ID")
):
    """获取请求的时间线视图"""
    try:
        tracing_service = await get_tracing_service()
        trace = await tracing_service.get_thread_trace(thread_id)
        
        if not trace:
            raise HTTPException(status_code=404, detail=f"请求追踪 {thread_id} 不存在")
        
        timeline = _generate_request_timeline(trace)
        return {"thread_id": thread_id, "timeline": timeline}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get request timeline: {e}")
        raise HTTPException(status_code=500, detail=f"获取请求时间线失败: {str(e)}")


@tracing_router.get("/nodes/performance", response_model=NodePerformanceStats)
async def get_node_performance(
    days: int = Query(7, ge=1, le=90, description="统计天数")
):
    """获取节点性能统计"""
    try:
        tracing_service = await get_tracing_service()
        stats = await tracing_service.get_node_performance_stats(days=days)
        
        node_stats = []
        for stat in stats['node_statistics']:
            node_stats.append(NodeStatsItem(
                node_name=stat['node_name'],
                total_executions=stat['total_executions'],
                avg_duration_ms=stat['avg_duration_ms'],
                min_duration_ms=stat['min_duration_ms'],
                max_duration_ms=stat['max_duration_ms'],
                success_rate=stat['success_rate']
            ))
        
        return NodePerformanceStats(
            analysis_period_days=stats['analysis_period_days'],
            total_requests_analyzed=stats['total_requests_analyzed'],
            node_statistics=node_stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get node performance: {e}")
        raise HTTPException(status_code=500, detail=f"获取节点性能失败: {str(e)}")


@tracing_router.get("/requests/{thread_id}/conversations")
async def get_request_conversations(
    thread_id: str = Path(..., description="线程ID")
):
    """按用户请求分组显示对话内容 - 使用修复后的tracing服务"""
    try:
        tracing_service = await get_tracing_service()
        trace = await tracing_service.get_thread_trace(thread_id)
        
        if not trace:
            raise HTTPException(status_code=404, detail=f"线程 {thread_id} 不存在")
        
        conversations = []
        current_conversation = None
        
        # 遍历所有检查点的消息
        for checkpoint in trace.checkpoints:
            for message in checkpoint.messages:
                if message.message_type == "HumanMessage":
                    # 检查是否是新对话
                    is_new = True
                    if current_conversation and current_conversation.get("user_request"):
                        if message.content_preview == current_conversation["user_request"]:
                            is_new = False
                    
                    if is_new:
                        if current_conversation:
                            conversations.append(current_conversation)
                        current_conversation = {
                            "user_request": message.content_preview,
                            "message_type": message.message_type,
                            "checkpoint": checkpoint.version,
                            "responses": []
                        }
                
                elif current_conversation and message.message_type in ["AIMessage", "SystemMessage", "ToolMessage"]:
                    # 添加响应到当前对话
                    if not any(message.content_preview == resp["content"] for resp in current_conversation["responses"]):
                        current_conversation["responses"].append({
                            "content": message.content_preview,
                            "message_type": message.message_type,
                            "checkpoint": checkpoint.version
                        })
        
        # 添加最后一个对话
        if current_conversation:
            conversations.append(current_conversation)
        
        # 去重和清理
        unique_conversations = []
        for conv in conversations:
            if conv["user_request"] and len(conv["user_request"]) > 3:
                # 去除重复的用户请求
                if not any(conv["user_request"] in existing["user_request"] or 
                          existing["user_request"] in conv["user_request"] 
                          for existing in unique_conversations):
                    unique_conversations.append(conv)
        
        return {
            "thread_id": thread_id,
            "total_conversations": len(unique_conversations),
            "conversations": unique_conversations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get request conversations: {e}")
        raise HTTPException(status_code=500, detail=f"获取对话内容失败: {str(e)}")


@tracing_router.get("/requests/{thread_id}/messages/detailed")
async def get_detailed_messages(
    thread_id: str = Path(..., description="线程ID")
):
    """获取线程中所有消息类型的详细信息 - 使用修复后的tracing服务"""
    try:
        tracing_service = await get_tracing_service()
        trace = await tracing_service.get_thread_trace(thread_id)
        
        if not trace:
            raise HTTPException(status_code=404, detail=f"线程 {thread_id} 不存在")
        
        all_messages = {
            'HumanMessage': [],
            'AIMessage': [],
            'SystemMessage': [], 
            'ToolMessage': []
        }
        
        # 遍历所有检查点的消息
        for checkpoint_index, checkpoint in enumerate(trace.checkpoints):
            for message in checkpoint.messages:
                if message.message_type in all_messages:
                    message_info = {
                        "content": message.content_preview,
                        "checkpoint": checkpoint.version,
                        "checkpoint_index": checkpoint_index,
                        "length": message.content_length,
                        "has_tool_calls": message.has_tool_calls,
                        "tool_call_ids": message.tool_call_ids
                    }
                    # 避免重复
                    if not any(msg["content"] == message.content_preview for msg in all_messages[message.message_type]):
                        all_messages[message.message_type].append(message_info)
        
        # 统计信息
        stats = {
            msg_type: {
                "count": len(messages),
                "avg_length": sum(msg["length"] for msg in messages) / len(messages) if messages else 0,
                "total_length": sum(msg["length"] for msg in messages)
            }
            for msg_type, messages in all_messages.items()
        }
        
        return {
            "thread_id": thread_id,
            "message_types": all_messages,
            "statistics": stats,
            "total_messages": sum(len(messages) for messages in all_messages.values()),
            "checkpoints_analyzed": len(trace.checkpoints)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get detailed messages: {e}")
        raise HTTPException(status_code=500, detail=f"获取详细消息失败: {str(e)}")


@tracing_router.get("/messages/analysis")
async def get_message_analysis(
    thread_id: str = Query(..., description="线程ID"),
    show_content: bool = Query(False, description="是否显示消息内容")
):
    """获取消息分析报告"""
    try:
        tracing_service = await get_tracing_service()
        trace = await tracing_service.get_thread_trace(thread_id)
        
        if not trace:
            raise HTTPException(status_code=404, detail=f"请求追踪 {thread_id} 不存在")
        
        # 分析消息类型分布
        message_types = {}
        total_content_length = 0
        tool_calls_count = 0
        
        for checkpoint in trace.checkpoints:
            for message in checkpoint.messages:
                msg_type = message.message_type
                if msg_type not in message_types:
                    message_types[msg_type] = 0
                message_types[msg_type] += 1
                
                total_content_length += message.content_length
                if message.has_tool_calls:
                    tool_calls_count += len(message.tool_call_ids)
        
        # 分析消息增长趋势
        growth_analysis = []
        for i in range(1, len(trace.message_growth)):
            growth = trace.message_growth[i] - trace.message_growth[i-1]
            growth_analysis.append({
                "checkpoint": i,
                "messages_added": growth,
                "estimated_node": trace.estimated_nodes[i] if i < len(trace.estimated_nodes) else "unknown"
            })
        
        analysis = {
            "thread_id": thread_id,
            "summary": {
                "total_checkpoints": len(trace.checkpoints),
                "total_messages": trace.total_messages,
                "total_content_length": total_content_length,
                "tool_calls_count": tool_calls_count,
                "duration_ms": trace.duration_ms
            },
            "message_type_distribution": message_types,
            "message_growth_pattern": trace.message_growth,
            "growth_analysis": growth_analysis,
            "estimated_node_sequence": trace.estimated_nodes
        }
        
        # 如果需要显示内容，添加消息详情
        if show_content:
            analysis["message_details"] = []
            for checkpoint in trace.checkpoints[-1:]:  # 只显示最后一个检查点的消息
                for message in checkpoint.messages:
                    analysis["message_details"].append({
                        "index": message.index,
                        "type": message.message_type,
                        "content": message.content_preview,
                        "length": message.content_length,
                        "has_tool_calls": message.has_tool_calls
                    })
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get message analysis: {e}")
        raise HTTPException(status_code=500, detail=f"获取消息分析失败: {str(e)}")


def _generate_request_timeline(trace) -> List[Dict[str, Any]]:
    """生成请求时间线"""
    timeline = []
    
    # 请求开始
    timeline.append({
        "timestamp": trace.start_time.isoformat() if trace.start_time else "",
        "event": "请求开始",
        "type": "request_start",
        "details": {
            "thread_id": trace.thread_id,
            "initial_messages": trace.checkpoints[0].message_count if trace.checkpoints else 0
        }
    })
    
    # 检查点事件
    for i, checkpoint in enumerate(trace.checkpoints):
        estimated_node = trace.estimated_nodes[i] if i < len(trace.estimated_nodes) else "unknown"
        
        timeline.append({
            "timestamp": checkpoint.timestamp.isoformat() if checkpoint.timestamp else "",
            "event": f"检查点 {i+1} - {estimated_node}节点",
            "type": "checkpoint",
            "node": estimated_node,
            "details": {
                "checkpoint_id": checkpoint.checkpoint_id,
                "message_count": checkpoint.message_count,
                "messages_added": (
                    checkpoint.message_count - trace.checkpoints[i-1].message_count 
                    if i > 0 else checkpoint.message_count
                )
            }
        })
    
    # 请求结束
    if trace.end_time:
        timeline.append({
            "timestamp": trace.end_time.isoformat(),
            "event": "请求完成",
            "type": "request_complete",
            "details": {
                "duration_ms": trace.duration_ms,
                "total_messages": trace.total_messages,
                "total_checkpoints": len(trace.checkpoints)
            }
        })
    
    return timeline