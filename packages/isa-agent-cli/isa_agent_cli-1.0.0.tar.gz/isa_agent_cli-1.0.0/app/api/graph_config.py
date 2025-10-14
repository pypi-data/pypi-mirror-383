#!/usr/bin/env python3
"""
Graph Configuration Management API

REST API endpoints for managing SmartAgentGraphBuilder configurations.
Provides CRUD operations and graph building capabilities.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import base64

from ..graphs.graph_config_service import (
    get_graph_config_service, 
    GraphConfigService, 
    GraphBuilderConfig,
    GuardrailMode
)
from .auth.api_key_manager import require_admin_permission, require_read_permission
from ..utils.logger import api_logger

router = APIRouter(prefix="/api/v1/agents/graph", tags=["graph-configuration"])


# Request/Response Models
class CreateConfigRequest(BaseModel):
    """Request model for creating graph configuration"""
    config_name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    
    # Guardrail settings
    guardrail_enabled: bool = Field(default=False)
    guardrail_mode: GuardrailMode = Field(default=GuardrailMode.MODERATE)
    
    # Failsafe settings
    failsafe_enabled: bool = Field(default=True)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Performance limits
    max_graph_iterations: int = Field(default=50, ge=1, le=1000)
    max_agent_loops: int = Field(default=10, ge=1, le=100)
    max_tool_loops: int = Field(default=5, ge=1, le=50)
    
    # Cache policies
    llm_cache_ttl: int = Field(default=300, ge=60, le=3600)
    tool_cache_ttl: int = Field(default=120, ge=30, le=1800)
    
    # Retry policies  
    max_retry_attempts: int = Field(default=3, ge=1, le=10)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)


class UpdateConfigRequest(BaseModel):
    """Request model for updating graph configuration"""
    description: Optional[str] = None
    guardrail_enabled: Optional[bool] = None
    guardrail_mode: Optional[GuardrailMode] = None
    failsafe_enabled: Optional[bool] = None
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_graph_iterations: Optional[int] = Field(None, ge=1, le=1000)
    max_agent_loops: Optional[int] = Field(None, ge=1, le=100)
    max_tool_loops: Optional[int] = Field(None, ge=1, le=50)
    llm_cache_ttl: Optional[int] = Field(None, ge=60, le=3600)
    tool_cache_ttl: Optional[int] = Field(None, ge=30, le=1800)
    max_retry_attempts: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ConfigResponse(BaseModel):
    """Response model for configuration data"""
    config_name: str
    config_version: str
    is_active: bool
    description: Optional[str]
    guardrail_enabled: bool
    guardrail_mode: GuardrailMode
    failsafe_enabled: bool
    confidence_threshold: float
    max_graph_iterations: int
    max_agent_loops: int
    max_tool_loops: int
    llm_cache_ttl: int
    tool_cache_ttl: int
    max_retry_attempts: int
    tags: List[str]
    created_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ValidationResponse(BaseModel):
    """Response model for configuration validation"""
    valid: bool
    message: str
    graph_info: Optional[Dict[str, Any]]
    warnings: List[str]


class StatsResponse(BaseModel):
    """Response model for service statistics"""
    total_configurations: int
    active_configuration: Optional[str]
    configurations: List[Dict[str, Any]]
    builder_cached: bool


class VisualizationResponse(BaseModel):
    """Response model for graph visualization"""
    config_name: str
    format: str
    content: str
    metadata: Dict[str, Any]


class GraphStructureResponse(BaseModel):
    """Response model for detailed graph structure"""
    config_name: str
    architecture: str
    nodes: Dict[str, Any]
    edges: List[Dict[str, Any]]
    routing_logic: Dict[str, Any]
    limits: Dict[str, Any]
    features: List[str]


# API Endpoints

@router.get("/configurations", response_model=List[ConfigResponse])
async def list_configurations(
    include_inactive: bool = False,
    api_key_info: dict = Depends(require_read_permission)
):
    """List all graph configurations"""
    try:
        service = await get_graph_config_service()
        configs = await service.list_configurations(include_inactive=include_inactive)
        
        api_logger.info(f"📋 Listed {len(configs)} graph configurations")
        return [ConfigResponse(**config.dict()) for config in configs]
        
    except Exception as e:
        api_logger.error(f"❌ Failed to list configurations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configurations", response_model=ConfigResponse)
async def create_configuration(
    request: CreateConfigRequest,
    api_key_info: dict = Depends(require_admin_permission)
):
    """Create a new graph configuration"""
    try:
        service = await get_graph_config_service()
        
        # Create configuration object
        config = GraphBuilderConfig(
            config_name=request.config_name,
            description=request.description,
            guardrail_enabled=request.guardrail_enabled,
            guardrail_mode=request.guardrail_mode,
            failsafe_enabled=request.failsafe_enabled,
            confidence_threshold=request.confidence_threshold,
            max_graph_iterations=request.max_graph_iterations,
            max_agent_loops=request.max_agent_loops,
            max_tool_loops=request.max_tool_loops,
            llm_cache_ttl=request.llm_cache_ttl,
            tool_cache_ttl=request.tool_cache_ttl,
            max_retry_attempts=request.max_retry_attempts,
            tags=request.tags,
            created_by=api_key_info.get("name", "admin")
        )
        
        created_config = await service.create_configuration(config)
        
        api_logger.info(f"✅ Created graph configuration: {request.config_name}")
        return ConfigResponse(**created_config.dict())
        
    except ValueError as e:
        api_logger.error(f"❌ Configuration creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        api_logger.error(f"❌ Configuration creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configurations/{config_name}", response_model=ConfigResponse)
async def get_configuration(
    config_name: str,
    api_key_info: dict = Depends(require_read_permission)
):
    """Get specific graph configuration"""
    try:
        service = await get_graph_config_service()
        config = await service.get_configuration(config_name)
        
        if not config:
            raise HTTPException(status_code=404, detail=f"Configuration '{config_name}' not found")
        
        api_logger.info(f"📖 Retrieved configuration: {config_name}")
        return ConfigResponse(**config.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"❌ Failed to get configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/configurations/{config_name}", response_model=ConfigResponse)
async def update_configuration(
    config_name: str,
    request: UpdateConfigRequest,
    api_key_info: dict = Depends(require_admin_permission)
):
    """Update existing graph configuration"""
    try:
        service = await get_graph_config_service()
        
        # Convert request to dict, excluding None values
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        updated_config = await service.update_configuration(config_name, updates)
        
        api_logger.info(f"📝 Updated configuration: {config_name}")
        return ConfigResponse(**updated_config.dict())
        
    except ValueError as e:
        api_logger.error(f"❌ Configuration update failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        api_logger.error(f"❌ Configuration update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/configurations/{config_name}")
async def delete_configuration(
    config_name: str,
    api_key_info: dict = Depends(require_admin_permission)
):
    """Delete graph configuration"""
    try:
        service = await get_graph_config_service()
        success = await service.delete_configuration(config_name)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Configuration '{config_name}' not found")
        
        api_logger.info(f"🗑️ Deleted configuration: {config_name}")
        return {"message": f"Configuration '{config_name}' deleted successfully"}
        
    except ValueError as e:
        api_logger.error(f"❌ Configuration deletion failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"❌ Configuration deletion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active", response_model=ConfigResponse)
async def get_active_configuration(
    api_key_info: dict = Depends(require_read_permission)
):
    """Get currently active graph configuration"""
    try:
        service = await get_graph_config_service()
        config = await service.get_active_configuration()
        
        api_logger.info(f"📍 Retrieved active configuration: {config.config_name}")
        return ConfigResponse(**config.dict())
        
    except Exception as e:
        api_logger.error(f"❌ Failed to get active configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/active/{config_name}", response_model=ConfigResponse)
async def set_active_configuration(
    config_name: str,
    api_key_info: dict = Depends(require_admin_permission)
):
    """Set active graph configuration"""
    try:
        service = await get_graph_config_service()
        config = await service.set_active_configuration(config_name)
        
        api_logger.info(f"🎯 Set active configuration: {config_name}")
        return ConfigResponse(**config.dict())
        
    except ValueError as e:
        api_logger.error(f"❌ Failed to set active configuration: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        api_logger.error(f"❌ Active configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configurations/{config_name}/validate", response_model=ValidationResponse)
async def validate_configuration(
    config_name: str,
    api_key_info: dict = Depends(require_read_permission)
):
    """Validate graph configuration by building a test graph"""
    try:
        service = await get_graph_config_service()
        config = await service.get_configuration(config_name)
        
        if not config:
            raise HTTPException(status_code=404, detail=f"Configuration '{config_name}' not found")
        
        validation_result = await service.validate_configuration(config)
        
        api_logger.info(f"🔍 Validated configuration: {config_name} - {'✅ Valid' if validation_result['valid'] else '❌ Invalid'}")
        return ValidationResponse(**validation_result)
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"❌ Configuration validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/build/{config_name}")
async def build_graph_with_config(
    config_name: str,
    api_key_info: dict = Depends(require_admin_permission)
):
    """Build graph using specific configuration"""
    try:
        service = await get_graph_config_service()
        graph = await service.build_graph_with_config(config_name)
        
        # Get graph info for response
        graph_builder = await service.get_graph_builder(config_name)
        graph_info = graph_builder.get_graph_info()
        
        api_logger.info(f"🏗️ Built graph with configuration: {config_name}")
        return {
            "message": f"Graph built successfully with configuration '{config_name}'",
            "config_name": config_name,
            "graph_info": graph_info
        }
        
    except ValueError as e:
        api_logger.error(f"❌ Graph building failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        api_logger.error(f"❌ Graph building error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebuild")
async def rebuild_active_graph(
    api_key_info: dict = Depends(require_admin_permission)
):
    """Rebuild graph with active configuration"""
    try:
        service = await get_graph_config_service()
        active_config = await service.get_active_configuration()
        
        # Force rebuild
        graph_builder = await service.get_graph_builder(force_rebuild=True)
        graph = graph_builder.build_graph()
        
        graph_info = graph_builder.get_graph_info()
        
        api_logger.info(f"🔄 Rebuilt graph with active configuration: {active_config.config_name}")
        return {
            "message": f"Graph rebuilt successfully with active configuration '{active_config.config_name}'",
            "config_name": active_config.config_name,
            "graph_info": graph_info
        }
        
    except Exception as e:
        api_logger.error(f"❌ Graph rebuilding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_configuration_stats(
    api_key_info: dict = Depends(require_read_permission)
):
    """Get graph configuration service statistics"""
    try:
        service = await get_graph_config_service()
        stats = service.get_service_stats()
        
        api_logger.info("📊 Retrieved configuration statistics")
        return StatsResponse(**stats)
        
    except Exception as e:
        api_logger.error(f"❌ Failed to get configuration stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modes", response_model=Dict[str, List[str]])
async def get_available_modes(
    api_key_info: dict = Depends(require_read_permission)
):
    """Get available guardrail modes and other configuration options"""
    try:
        api_logger.info("📋 Retrieved available configuration modes")
        return {
            "guardrail_modes": [mode.value for mode in GuardrailMode],
            "supported_features": [
                "guardrails",
                "failsafe", 
                "retry_policies",
                "cache_policies",
                "performance_limits"
            ]
        }
        
    except Exception as e:
        api_logger.error(f"❌ Failed to get available modes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualize/active", response_model=VisualizationResponse)
async def visualize_active_graph(
    format: str = "mermaid",
    api_key_info: dict = Depends(require_read_permission)
):
    """Visualize active graph configuration"""
    try:
        service = await get_graph_config_service()
        active_config = await service.get_active_configuration()
        
        # Get visualization for active config
        visualization_result = await service.visualize_graph(active_config.config_name, format)
        
        api_logger.info(f"🎨 Generated {format} visualization for active configuration")
        return VisualizationResponse(**visualization_result)
        
    except Exception as e:
        api_logger.error(f"❌ Active visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualize/{config_name}", response_model=VisualizationResponse)
async def visualize_graph(
    config_name: str,
    format: str = "mermaid",  # mermaid, png, ascii
    api_key_info: dict = Depends(require_read_permission)
):
    """Visualize graph structure"""
    try:
        service = await get_graph_config_service()
        
        # Validate format
        valid_formats = ["mermaid", "png", "ascii"]
        if format not in valid_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid format. Must be one of: {valid_formats}"
            )
        
        # Get visualization
        visualization_result = await service.visualize_graph(config_name, format)
        
        api_logger.info(f"🎨 Generated {format} visualization for configuration: {config_name}")
        return VisualizationResponse(**visualization_result)
        
    except ValueError as e:
        api_logger.error(f"❌ Visualization failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        api_logger.error(f"❌ Visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structure/active", response_model=GraphStructureResponse)
async def get_active_graph_structure(
    api_key_info: dict = Depends(require_read_permission)
):
    """Get detailed structure information for active graph"""
    try:
        service = await get_graph_config_service()
        active_config = await service.get_active_configuration()
        
        structure_data = await service.get_graph_structure(active_config.config_name)
        
        api_logger.info(f"📊 Retrieved active graph structure")
        return GraphStructureResponse(**structure_data)
        
    except Exception as e:
        api_logger.error(f"❌ Active structure retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structure/{config_name}", response_model=GraphStructureResponse)
async def get_graph_structure(
    config_name: str,
    api_key_info: dict = Depends(require_read_permission)
):
    """Get detailed graph structure information"""
    try:
        service = await get_graph_config_service()
        structure_data = await service.get_graph_structure(config_name)
        
        api_logger.info(f"📊 Retrieved graph structure for configuration: {config_name}")
        return GraphStructureResponse(**structure_data)
        
    except ValueError as e:
        api_logger.error(f"❌ Structure retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        api_logger.error(f"❌ Structure retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_graph_info():
    """Get general graph configuration information (public endpoint)"""
    return {
        "service": "Graph Configuration Management",
        "version": "1.0",
        "description": "Manages SmartAgentGraphBuilder configurations with CRUD operations",
        "features": [
            "Dynamic configuration management",
            "Graph validation",
            "Active configuration switching", 
            "Performance and security controls",
            "Configuration versioning",
            "Graph visualization (mermaid, png, ascii)",
            "Detailed graph structure analysis"
        ],
        "authentication_required": True,
        "admin_required_for": [
            "create", "update", "delete",
            "set_active", "build", "rebuild"
        ],
        "visualization_formats": ["mermaid", "png", "ascii"]
    }