"""
Simplified FastAPI application using smart_agent.py directly
"""
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import json

from .config import settings
from .smart_agent_v2 import SmartAgent
from .components.multimodal_processor import MultimodalProcessor
from .utils.logger import api_logger

# Pydantic models for API
from pydantic import BaseModel

class ConversationRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    user_id: Optional[str] = "anonymous"

class ConversationResponse(BaseModel):
    response: str
    thread_id: str
    trace_id: Optional[str] = None
    credits_used: int = 0

class HealthCheckResponse(BaseModel):
    status: str
    version: str
    timestamp: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# Global smart agent instance
smart_agent = None

# Lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global smart_agent
    
    api_logger.info("🚀 Starting Smart Agent API...")
    
    # Initialize smart agent with config-based MCP URL
    smart_agent = SmartAgent()  # Will use settings.mcp_server_url from config
    await smart_agent.__aenter__()
    
    api_logger.info("✅ Smart Agent API ready")
    yield
    
    # Cleanup on shutdown
    api_logger.info("🛑 Shutting down Smart Agent API...")
    if smart_agent:
        await smart_agent.__aexit__(None, None, None)
    api_logger.info("✅ Cleanup completed")

# Create FastAPI app
app = FastAPI(
    title="Smart Agent API",
    description="HTTP API for Smart Agent with MCP integration - 🎆 Unified /api/chat endpoint!",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include billing router
# try:
#     from .api.billing import billing_router
#     app.include_router(billing_router)
#     api_logger.info("✅ Billing endpoints registered")
# except ImportError as e:
#     api_logger.warning(f"⚠️ Failed to import billing endpoints: {e}")

# Include tracing router
try:
    from .api.tracing import tracing_router
    app.include_router(tracing_router)
    api_logger.info("✅ Tracing endpoints registered")
except ImportError as e:
    api_logger.warning(f"⚠️ Failed to import tracing endpoints: {e}")

# Mount static files for tracing dashboard
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Agent API v1.2",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "documentation": "/docs"
    }

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        version="1.2.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/chat", response_model=ConversationResponse)
async def chat(request: ConversationRequest):
    """Main chat endpoint using Smart Agent"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        # Use smart agent
        result = await smart_agent.chat(
            user_input=request.message,
            session_id=request.thread_id,
            user_id=request.user_id
        )
        
        if result["error"]:
            raise HTTPException(status_code=500, detail=result["response"])
        
        return ConversationResponse(
            response=result["response"],
            thread_id=result["session_id"],
            trace_id=result.get("trace_id"),
            credits_used=result.get("credits_used", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/api/chat/streaming")
async def unified_chat_streaming(
    request: Request,
    message: Optional[str] = Form(None),
    thread_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form("anonymous"),
    audio: Optional[UploadFile] = File(None)
):
    """统一的聊天流式端点，支持多模态输入 - 匹配前端SDK路径"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        # 动态获取所有文件（支持 file_0, file_1, file_2... 格式）
        form_data = await request.form()
        files = []
        for key, value in form_data.items():
            if key.startswith('file_') and isinstance(value, UploadFile) and value.filename:
                files.append(value)
        
        # 解析消息数据
        text_input = ""
        metadata = {}
        
        if message:
            try:
                # 尝试解析JSON格式的消息
                message_data = json.loads(message)
                text_input = message_data.get('text', '') or message_data.get('message', '')
                metadata = message_data
            except (json.JSONDecodeError, TypeError):
                # 如果不是JSON，直接使用字符串
                text_input = message
                metadata = {}
        
        # 检查是否有多模态输入
        has_multimodal = bool(audio and audio.filename) or bool(files)
        
        # 验证输入
        if not text_input and not has_multimodal:
            raise HTTPException(status_code=400, detail="需要提供文字消息、语音或文件")
        
        final_thread_id = thread_id
        final_user_id = user_id or "anonymous"
        
        async def event_generator():
            try:
                progress = 0
                
                if not has_multimodal:
                    # 纯文字聊天流程
                    yield f"data: {json.dumps({'type': 'progress', 'progress': 10, 'step': '开始处理文字消息...', 'content': '开始处理文字消息...'})}\n\n"
                    
                    async for chunk in smart_agent.streaming_chat(
                        user_input=text_input,
                        session_id=final_thread_id,
                        user_id=final_user_id
                    ):
                        # 转换为前端期望的格式
                        if chunk.get('type') == 'token':
                            yield f"data: {json.dumps({'type': 'content', 'content': chunk.get('content', '')})}\n\n"
                        elif chunk.get('type') == 'end':
                            yield f"data: {json.dumps({'type': 'complete', 'progress': 100})}\n\n"
                            yield "data: [DONE]\n\n"
                        elif chunk.get('type') == 'error':
                            yield f"data: {json.dumps({'type': 'error', 'message': chunk.get('content', '')})}\n\n"
                        else:
                            yield f"data: {json.dumps(chunk)}\n\n"
                else:
                    # 多模态处理流程
                    processor = MultimodalProcessor()
                    
                    try:
                        audio_text = None
                        file_contents = []
                        progress = 10
                        
                        # 处理语音文件
                        if audio and audio.filename:
                            yield f"data: {json.dumps({'type': 'progress', 'progress': 20, 'step': '正在处理语音文件...', 'content': '正在处理语音文件...'})}\n\n"
                            try:
                                audio_result = await processor.process_audio_file(audio)
                                audio_text = audio_result.get("text", "")
                                transcription_text = f"语音转录: {audio_text}\n\n"
                                yield f"data: {json.dumps({'type': 'content', 'content': transcription_text})}\n\n"
                                progress = 40
                            except Exception as e:
                                yield f"data: {json.dumps({'type': 'error', 'message': f'语音处理失败: {str(e)}'})}\n\n"
                        
                        # 处理上传的文件
                        if files:
                            yield f"data: {json.dumps({'type': 'progress', 'progress': progress + 20, 'step': f'正在处理 {len(files)} 个文件...', 'content': f'正在处理 {len(files)} 个文件...'})}\n\n"
                            try:
                                file_contents = await processor.process_files(files)
                                
                                # 输出文件处理结果
                                files_count = len(file_contents)
                                content_text = f"已处理 {files_count} 个文件\n\n"
                                yield f"data: {json.dumps({'type': 'content', 'content': content_text})}\n\n"
                                progress = 60
                            except Exception as e:
                                yield f"data: {json.dumps({'type': 'error', 'message': f'文件处理失败: {str(e)}'})}\n\n"
                        
                        # AI生成回复
                        yield f"data: {json.dumps({'type': 'progress', 'progress': 80, 'step': 'AI正在生成回复...', 'content': 'AI正在生成回复...'})}\n\n"
                        
                        # 多模态流式聊天
                        async for chunk in smart_agent.multimodal_streaming_chat(
                            text_input=text_input,
                            audio_text=audio_text,
                            file_contents=file_contents,
                            session_id=final_thread_id,
                            user_id=final_user_id
                        ):
                            # 转换为前端期望的格式
                            if chunk.get('type') == 'token':
                                yield f"data: {json.dumps({'type': 'content', 'content': chunk.get('content', '')})}\n\n"
                            elif chunk.get('type') == 'end':
                                yield f"data: {json.dumps({'type': 'complete', 'progress': 100})}\n\n"
                                yield "data: [DONE]\n\n"
                            elif chunk.get('type') == 'error':
                                yield f"data: {json.dumps({'type': 'error', 'message': chunk.get('content', '')})}\n\n"
                            else:
                                yield f"data: {json.dumps(chunk)}\n\n"
                            
                    finally:
                        # 清理处理器
                        await processor.close()
                        
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
        
    except Exception as e:
        api_logger.error(f"❌ Streaming chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming chat failed: {str(e)}")

# =============================================================================
# UNIFIED CHAT ENDPOINT - Single endpoint for all chat types
# =============================================================================

@app.post("/api/chat")
async def unified_chat_endpoint(
    request: Request,
    message: Optional[str] = Form(None),
    thread_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form("anonymous"),
    audio: Optional[UploadFile] = File(None),
    force_streaming: Optional[bool] = Form(None),
    force_non_streaming: Optional[bool] = Form(None)
):
    """
    🎆 统一的聊天端点 - ONE ENDPOINT FOR EVERYTHING!
    
    支持:
    - 纯文本聊天
    - 语音输入
    - 文件上传（多个）
    - 自动流式检测
    - 手动流式控制
    """
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        # 动态获取所有文件（支持 file_0, file_1, file_2... 格式）
        form_data = await request.form()
        files = []
        for key, value in form_data.items():
            if key.startswith('file_') and isinstance(value, UploadFile) and value.filename:
                files.append(value)
        
        # 解析消息数据
        text_input = ""
        if message:
            try:
                # 尝试解析JSON格式的消息
                message_data = json.loads(message)
                text_input = message_data.get('text', '') or message_data.get('message', '')
            except (json.JSONDecodeError, TypeError):
                # 如果不是JSON，直接使用字符串
                text_input = message
        
        # 处理音频文件
        audio_text = None
        file_contents = []
        
        # 检查是否有多模态输入
        has_multimodal = bool(audio and audio.filename) or bool(files)
        
        # 验证输入
        if not text_input and not has_multimodal:
            raise HTTPException(status_code=400, detail="需要提供文字消息、语音或文件")
        
        # 处理多模态数据
        if has_multimodal:
            processor = MultimodalProcessor()
            try:
                if audio and audio.filename:
                    audio_result = await processor.process_audio_file(audio)
                    audio_text = audio_result.get("text", "")
                
                if files:
                    file_contents = await processor.process_files(files)
            finally:
                await processor.close()
        
        # 使用统一端点处理
        async def event_generator():
            async for chunk in smart_agent.unified_chat(
                text_input=text_input,
                audio_text=audio_text,
                file_contents=file_contents,
                session_id=thread_id,
                user_id=user_id,
                force_streaming=force_streaming,
                force_non_streaming=force_non_streaming
            ):
                # 转换为前端期望的格式
                if chunk.get('type') == 'token':
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk.get('content', '')})}\n\n"
                elif chunk.get('type') == 'end':
                    yield f"data: {json.dumps({'type': 'complete', 'progress': 100})}\n\n"
                    yield "data: [DONE]\n\n"
                elif chunk.get('type') == 'error':
                    yield f"data: {json.dumps({'type': 'error', 'message': chunk.get('content', '')})}\n\n"
                elif chunk.get('type') in ['start', 'progress', 'credits']:
                    yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"❌ Unified chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/capabilities")
async def get_capabilities():
    """Get Smart Agent capabilities"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        return smart_agent.get_capabilities()
        
    except Exception as e:
        print(f"❌ Capabilities error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")

@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        sessions = smart_agent.session_manager.sessions
        session_list = []
        
        for session_id, session_data in sessions.items():
            session_list.append({
                "session_id": session_id,
                "created_at": session_data["created_at"].isoformat(),
                "last_activity": session_data["last_activity"].isoformat(),
                "message_count": session_data["message_count"]
            })
        
        return {
            "sessions": session_list,
            "total": len(session_list)
        }
        
    except Exception as e:
        print(f"❌ List sessions error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get session history with enhanced database integration"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        # Get rich conversation history from database
        history = await smart_agent.get_session_history(session_id)
        
        return {
            "session_id": session_id,
            "history": history,
            "message_count": len(history)
        }
        
    except Exception as e:
        print(f"❌ Get session history error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session history: {str(e)}")

@app.get("/sessions/{session_id}/stats")
async def get_session_stats(session_id: str):
    """Get session statistics"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        stats = await smart_agent.get_session_stats(session_id)
        
        return {
            "session_id": session_id,
            "stats": stats
        }
        
    except Exception as e:
        print(f"❌ Get session stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session stats: {str(e)}")

@app.get("/sessions/{session_id}/details")
async def get_session_details(session_id: str):
    """Get complete session details with history and stats"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        # Get session with complete details
        session_details = await smart_agent.session_manager.get_session_with_history(session_id)
        
        if not session_details:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "session_id": session_id,
            "session_data": session_details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get session details error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session details: {str(e)}")

@app.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    """Get all sessions for a user"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        sessions = await smart_agent.get_user_sessions(user_id)
        
        return {
            "user_id": user_id,
            "sessions": sessions,
            "total_sessions": len(sessions)
        }
        
    except Exception as e:
        print(f"❌ Get user sessions error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user sessions: {str(e)}")

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a session"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        await smart_agent.clear_session(session_id)
        
        return {"message": f"Session {session_id} cleared successfully"}
        
    except Exception as e:
        print(f"❌ Clear session error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear session: {str(e)}")

@app.post("/sessions/{session_id}/set")
async def set_session(session_id: str):
    """Set current session"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        smart_agent.set_session_id(session_id)
        
        return {"message": f"Current session set to {session_id}"}
        
    except Exception as e:
        print(f"❌ Set session error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set session: {str(e)}")

@app.post("/guardrails/configure")
async def configure_guardrails(enabled: bool = False, mode: str = "moderate"):
    """Configure guardrails"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        smart_agent.configure_guardrails(enabled=enabled, mode=mode)
        
        return {
            "message": f"Guardrails {'enabled' if enabled else 'disabled'}",
            "mode": mode
        }
        
    except Exception as e:
        print(f"❌ Configure guardrails error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to configure guardrails: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        capabilities = smart_agent.get_capabilities()
        sessions = smart_agent.session_manager.sessions
        
        return {
            "system": {
                "status": "running",
                "version": "1.2.0",
                "timestamp": datetime.now().isoformat()
            },
            "agent": capabilities,
            "sessions": {
                "total_sessions": len(sessions),
                "current_session": smart_agent.current_session_id,
                "sessions": list(sessions.keys())
            }
        }
        
    except Exception as e:
        print(f"❌ Get stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/tracing/trace/{trace_id}")
async def get_trace_details(trace_id: str):
    """Get detailed trace information"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        # Access the tracer directly from the tracing module
        try:
            from app.tracing.tracer import tracer
            if not tracer:
                raise HTTPException(status_code=503, detail="Tracer not available")
            
            trace_summary = tracer.get_trace_summary(trace_id)
            
            if not trace_summary:
                raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
            
            return trace_summary
            
        except ImportError:
            raise HTTPException(status_code=503, detail="Tracing module not available")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get trace error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trace: {str(e)}")

@app.get("/tracing/traces")
async def list_traces():
    """List all available traces"""
    try:
        if not smart_agent:
            raise HTTPException(status_code=503, detail="Smart agent not initialized")
        
        try:
            from app.tracing.tracer import tracer
            if not tracer:
                return {"traces": [], "total": 0}
            
            # Try SQLite tracer first
            if hasattr(tracer, 'get_traces'):
                traces = tracer.get_traces(limit=100)
                return {
                    "traces": traces,
                    "total": len(traces)
                }
            
            # Fallback to old logic for in-memory tracer
            all_traces = {}
            
            # Group spans by trace_id
            for span in tracer.spans.values():
                trace_id = span.trace_id
                if trace_id not in all_traces:
                    all_traces[trace_id] = {
                        "trace_id": trace_id,
                        "span_count": 0,
                        "start_time": span.start_time,
                        "operations": [],
                        "duration": 0
                    }
                
                all_traces[trace_id]["span_count"] += 1
                all_traces[trace_id]["operations"].append(span.operation_name)
                if span.duration:
                    all_traces[trace_id]["duration"] = max(all_traces[trace_id]["duration"], span.duration)
            
            # Sort by start time (most recent first)
            traces_list = sorted(all_traces.values(), key=lambda x: x["start_time"], reverse=True)
            
            return {
                "traces": traces_list,
                "total": len(traces_list)
            }
            
        except ImportError:
            return {"traces": [], "total": 0, "message": "Tracing module not available"}
        
    except Exception as e:
        print(f"❌ List traces error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list traces: {str(e)}")

@app.get("/tracing/dashboard")
async def tracing_dashboard():
    """Serve tracing dashboard"""
    dashboard_path = Path(__file__).parent / "static" / "tracing" / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(str(dashboard_path))
    else:
        raise HTTPException(status_code=404, detail="Tracing dashboard not found")

@app.get("/trace/{trace_id}")
async def trace_detail_page(trace_id: str):
    """Serve trace detail page"""
    detail_path = Path(__file__).parent / "static" / "tracing" / "trace_detail.html"
    if detail_path.exists():
        return FileResponse(str(detail_path))
    else:
        # Fallback to dashboard with trace ID in URL fragment
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/tracing/dashboard#{trace_id}", status_code=302)

# =============================================================================
# TRACING WEB VIEWER ENDPOINTS (Production Ready)
# =============================================================================

@app.get("/tracing/traces")
async def list_traces_web(
    limit: int = 50,
    status: Optional[str] = None,
    session_id: Optional[str] = None
):
    """Get list of traces for web viewer"""
    try:
        from app.tracing.tracer import tracer
        if not tracer:
            raise HTTPException(status_code=503, detail="Tracer not available")
        
        # Check if tracer has the required methods
        if not hasattr(tracer, 'get_traces'):
            raise HTTPException(status_code=503, detail="Tracer does not support get_traces method")
        
        traces = tracer.get_traces(limit=limit, status=status, session_id=session_id)
        
        # Format for display and fix data issues
        from datetime import datetime
        for trace in traces:
            # Format start time
            if trace.get('start_time') is not None:
                try:
                    trace['start_time_formatted'] = datetime.fromtimestamp(trace['start_time']).strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, OSError):
                    trace['start_time_formatted'] = '-'
            else:
                trace['start_time_formatted'] = '-'
                
            # Format duration
            if trace.get('duration') is not None:
                trace['duration_formatted'] = f"{trace['duration']:.3f}s"
            else:
                trace['duration_formatted'] = '-'
            
            # Fix total_spans count - query actual spans for this trace
            try:
                if hasattr(tracer, 'supabase'):
                    # SupabaseTracer - use direct database query
                    spans_result = tracer.supabase.table('spans').select('span_id').eq('trace_id', trace['trace_id']).execute()
                    trace['total_spans'] = len(spans_result.data)
                elif hasattr(tracer, 'spans'):
                    # SimpleTracer - count from memory
                    trace_spans = [span for span in tracer.spans.values() if span.trace_id == trace['trace_id']]
                    trace['total_spans'] = len(trace_spans)
                else:
                    trace['total_spans'] = 0
            except Exception as e:
                print(f"⚠️ Failed to count spans for trace {trace['trace_id']}: {e}")
                trace['total_spans'] = 0
        
        return {
            'traces': traces,
            'total': len(traces)
        }
        
    except Exception as e:
        print(f"❌ List traces web error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list traces: {str(e)}")

@app.get("/tracing/traces/{trace_id}/details")
async def get_trace_details_web(trace_id: str):
    """Get detailed trace information for web viewer"""
    try:
        from app.tracing.tracer import tracer
        if not tracer:
            raise HTTPException(status_code=503, detail="Tracer not available")
        
        details = tracer.get_trace_details(trace_id)
        if not details:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        # Format timestamps
        from datetime import datetime
        trace = details['trace']
        if trace.get('start_time'):
            trace['start_time_formatted'] = datetime.fromtimestamp(trace['start_time']).strftime('%Y-%m-%d %H:%M:%S')
        if trace.get('end_time'):
            trace['end_time_formatted'] = datetime.fromtimestamp(trace['end_time']).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format span timestamps
        for span in details['spans']:
            if span.get('start_time'):
                span['start_time_formatted'] = datetime.fromtimestamp(span['start_time']).strftime('%H:%M:%S.%f')[:-3]
            if span.get('end_time'):
                span['end_time_formatted'] = datetime.fromtimestamp(span['end_time']).strftime('%H:%M:%S.%f')[:-3]
            if span.get('duration'):
                span['duration_formatted'] = f"{span['duration']:.3f}s"
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get trace details web error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trace details: {str(e)}")

@app.get("/tracing/traces/{trace_id}/flow")
async def get_langgraph_flow_web(trace_id: str):
    """Get LangGraph execution flow for web viewer"""
    try:
        from app.tracing.tracer import tracer
        if not tracer:
            raise HTTPException(status_code=503, detail="Tracer not available")
        
        flow = tracer.get_langgraph_flow(trace_id)
        
        # Format for visualization
        for step in flow:
            if step.get('execution_time'):
                step['execution_time_formatted'] = f"{step['execution_time']:.3f}s"
        
        return {
            'trace_id': trace_id,
            'flow': flow
        }
        
    except Exception as e:
        print(f"❌ Get LangGraph flow web error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get flow: {str(e)}")

@app.get("/tracing/traces/{trace_id}/model-interactions")
async def get_model_interactions_web(trace_id: str):
    """Get model interactions for web viewer"""
    try:
        from app.tracing.tracer import tracer
        import json
        
        if not tracer:
            raise HTTPException(status_code=503, detail="Tracer not available")
        
        interactions = []
        
        # Check if we're using Supabase tracer
        if hasattr(tracer, 'supabase'):
            # Get spans for this trace first
            spans_query = tracer.supabase.table('spans').select('span_id, operation_name').eq('trace_id', trace_id).execute()
            span_ids = [s['span_id'] for s in spans_query.data]
            
            if span_ids:
                # Get model interaction logs
                logs_query = tracer.supabase.table('span_logs').select(
                    'timestamp, message, data, span_id, level'
                ).in_('span_id', span_ids).or_(
                    'message.ilike.%Model input%,message.ilike.%Model output%'
                ).order('timestamp').execute()
                
                logs = logs_query.data
                spans_data = {s['span_id']: s for s in spans_query.data}
                
                # Group by interaction pairs
                current_interaction = {}
                for log in logs:
                    span_data = spans_data.get(log['span_id'], {})
                    
                    if 'Model input' in log['message']:
                        current_interaction = {
                            'span_id': log['span_id'],
                            'operation_name': span_data.get('operation_name', 'unknown'),
                            'timestamp': log['timestamp'],
                            'input': json.loads(log['data']) if log['data'] else None,
                            'output': None
                        }
                    elif 'Model output' in log['message'] and current_interaction:
                        current_interaction['output'] = json.loads(log['data']) if log['data'] else None
                        interactions.append(current_interaction)
                        current_interaction = {}
                
                # If no model logs found, create from LangGraph execution data
                if not interactions:
                    lg_query = tracer.supabase.table('langgraph_executions').select(
                        '*'
                    ).eq('trace_id', trace_id).eq('node_name', 'call_model').execute()
                    
                    for execution in lg_query.data:
                        input_state = json.loads(execution.get('input_state', '{}')) if execution.get('input_state') else {}
                        output_state = json.loads(execution.get('output_state', '{}')) if execution.get('output_state') else {}
                        
                        input_messages = input_state.get('messages', [])
                        output_messages = output_state.get('messages', [])
                        
                        if input_messages and output_messages and len(output_messages) > len(input_messages):
                            new_message = output_messages[len(input_messages):][0] if len(output_messages) > len(input_messages) else None
                            
                            interactions.append({
                                'span_id': execution.get('span_id'),
                                'operation_name': 'call_model',
                                'timestamp': execution.get('created_at'),
                                'input': {
                                    'messages': input_messages,
                                    'tools_count': input_state.get('tools_count', 0)
                                },
                                'output': {
                                    'message': new_message,
                                    'execution_time': execution.get('execution_time')
                                }
                            })
        
        return {
            'trace_id': trace_id,
            'interactions': interactions,
            'total_interactions': len(interactions)
        }
        
    except Exception as e:
        print(f"❌ Get model interactions web error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model interactions: {str(e)}")

@app.get("/tracing/traces/{trace_id}/node-details")
async def get_node_details_web(trace_id: str):
    """Get node details for web viewer"""
    try:
        from app.tracing.tracer import tracer
        import json
        
        if not tracer:
            raise HTTPException(status_code=503, detail="Tracer not available")
        
        node_details = []
        
        # Check if we're using Supabase tracer
        if hasattr(tracer, 'supabase'):
            # Get LangGraph execution data
            lg_query = tracer.supabase.table('langgraph_executions').select(
                '*'
            ).eq('trace_id', trace_id).order('execution_order').execute()
            
            # Get spans data for additional context
            spans_query = tracer.supabase.table('spans').select('*').eq('trace_id', trace_id).execute()
            spans_by_name = {}
            for span in spans_query.data:
                node_name = span['operation_name'].replace('node_', '') if span['operation_name'].startswith('node_') else span['operation_name']
                spans_by_name[node_name] = span
            
            # Process each LangGraph execution
            for execution in lg_query.data:
                node_name = execution.get('node_name', 'unknown')
                
                input_state = json.loads(execution.get('input_state', '{}')) if execution.get('input_state') else {}
                output_state = json.loads(execution.get('output_state', '{}')) if execution.get('output_state') else {}
                span_data = spans_by_name.get(node_name, {})
                
                node_detail = {
                    'operation_name': f'node_{node_name}',
                    'node_name': node_name,
                    'span_id': execution.get('span_id'),
                    'execution_order': execution.get('execution_order', 0),
                    'execution_time': execution.get('execution_time', 0),
                    'timestamp': execution.get('created_at'),
                    'inputs': [],
                    'outputs': []
                }
                
                # Node-specific processing (same logic as in web_viewer.py)
                if node_name == 'manage_memory':
                    node_detail['inputs'].append({
                        'type': 'session_context',
                        'session_id': input_state.get('session_id', 'unknown'),
                        'user_query': input_state.get('user_query', ''),
                        'messages_count': input_state.get('messages_count', 0),
                        'conversation_summary': input_state.get('conversation_summary', '')
                    })
                    node_detail['outputs'].append({
                        'type': 'memory_result',
                        'action': 'memory_processed',
                        'messages_after': output_state.get('messages_count', 0)
                    })
                
                elif node_name == 'call_model':
                    input_messages = input_state.get('messages', [])
                    output_messages = output_state.get('messages', [])
                    
                    node_detail['inputs'].append({
                        'type': 'model_input',
                        'messages': input_messages,
                        'tools_available': input_state.get('tools_count', 0),
                        'execution_strategy': input_state.get('execution_strategy', 'direct')
                    })
                    
                    if len(output_messages) > len(input_messages):
                        new_messages = output_messages[len(input_messages):]
                        node_detail['outputs'].append({
                            'type': 'model_output',
                            'new_messages': new_messages,
                            'total_messages': len(output_messages)
                        })
                
                elif node_name == 'should_continue':
                    node_detail['inputs'].append({
                        'type': 'routing_input',
                        'messages_count': input_state.get('messages_count', 0),
                        'last_message_type': input_state.get('messages', [{}])[-1].get('type', 'unknown') if input_state.get('messages') else 'none'
                    })
                    node_detail['outputs'].append({
                        'type': 'routing_decision',
                        'next_action': execution.get('next_action', 'end'),
                        'decision_logic': 'Route to next step based on message analysis'
                    })
                
                # Add span timing information
                if span_data:
                    node_detail['span_info'] = {
                        'start_time': span_data.get('start_time'),
                        'end_time': span_data.get('end_time'),
                        'duration': span_data.get('duration'),
                        'status': span_data.get('status', 'completed')
                    }
                
                node_details.append(node_detail)
        
        return {
            'trace_id': trace_id,
            'node_details': node_details,
            'total_nodes': len(node_details)
        }
        
    except Exception as e:
        print(f"❌ Get node details web error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get node details: {str(e)}")

@app.get("/tracing/stats")
async def get_tracing_stats():
    """Get tracing system statistics"""
    try:
        from app.tracing.tracer import tracer
        if not tracer:
            raise HTTPException(status_code=503, detail="Tracer not available")
        
        traces = tracer.get_traces(limit=1000)
        
        total_traces = len(traces)
        completed_traces = len([t for t in traces if t.get('status') == 'completed'])
        failed_traces = len([t for t in traces if t.get('status') == 'failed'])
        
        if traces:
            avg_duration = sum(t.get('duration', 0) for t in traces if t.get('duration')) / len([t for t in traces if t.get('duration')])
        else:
            avg_duration = 0
        
        return {
            'total_traces': total_traces,
            'completed_traces': completed_traces,
            'failed_traces': failed_traces,
            'success_rate': (completed_traces / total_traces * 100) if total_traces > 0 else 0,
            'avg_duration': avg_duration
        }
        
    except Exception as e:
        print(f"❌ Get tracing stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    print(f"❌ Unhandled error: {exc}")
    return ErrorResponse(
        error="Internal server error",
        details=str(exc)
    )

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting Smart Agent API on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "app.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )