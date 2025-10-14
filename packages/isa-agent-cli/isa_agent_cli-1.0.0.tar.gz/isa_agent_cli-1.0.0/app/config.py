"""
Configuration management for the Enhanced MCP Client
"""
import os
from typing import Optional
from pydantic import BaseModel, SecretStr, computed_field
from dotenv import load_dotenv

def get_env_file_path():
    """Get the appropriate environment file path based on ENVIRONMENT variable"""
    env = os.getenv("ENVIRONMENT", "dev")
    
    env_files = {
        "dev": "deployment/dev/.env",
        "test": "deployment/test/.env.test",
        "staging": "deployment/staging/.env.staging",
        "production": "deployment/production/.env.production"
    }
    
    return env_files.get(env, "deployment/dev/.env")

# Load environment variables based on environment  
env_file = get_env_file_path()
load_dotenv(env_file, override=False)  # Load environment-specific file, but prioritize system environment variables

class Settings(BaseModel):
    """Application settings"""
    
    # AI Model Configuration - Mixed Strategy
    # Default: Cerebras gpt-oss-120b (fast & cheap for most nodes)
    # ReasonNode override: gpt-4.1-mini (reliable tool calling)

    # Note: Cerebras gpt-oss-120b doesn't support response_format, use prompt engineering for JSON
    # ai_provider: str = os.getenv("AI_PROVIDER", "cerebras")
    # ai_model: str = os.getenv("AI_MODEL", "gpt-oss-120b")

    ai_provider: str = os.getenv("AI_PROVIDER", "openai")
    ai_model: str = os.getenv("AI_MODEL", "gpt-4.1-nano")

    # ReasonNode uses gpt-4.1-mini for reliable tool calling (configured in reason_node.py)
    reason_model_provider: str = os.getenv("REASON_MODEL_PROVIDER", "openai")
    reason_model: str = os.getenv("REASON_MODEL", "gpt-4.1-mini")  # gpt-4.1-mini - stronger reasoning
    
    # ResponseNode uses gpt-4.1-nano for fast response formatting
    response_model_provider: str = os.getenv("RESPONSE_MODEL_PROVIDER", "openai")
    response_model: str = os.getenv("RESPONSE_MODEL", "gpt-4.1-nano")  # gpt-4.1-nano - fast formatting

    # Note: gpt-4.1 tool calling is unstable (sometimes works, sometimes doesn't)
    # Note: gpt-4.1-mini also could not call create_execution_plan
    # Note: gpt-5-mini timed out (may not exist or has issues)

    ai_temperature: float = float(os.getenv("AI_TEMPERATURE", "0"))
    
    # ISA Model Configuration
    isa_mode: str = os.getenv("ISA_MODE", "local")  # local 或 api
    
    # MCP Server Configuration - Now using properties with Consul discovery
    
    # Consul Configuration
    consul_host: str = os.getenv("CONSUL_HOST", "localhost")
    consul_port: int = int(os.getenv("CONSUL_PORT", "8500"))

    # Loki Configuration (Centralized Logging)
    loki_url: str = os.getenv("LOKI_URL", "http://localhost:3100")
    loki_enabled: bool = os.getenv("LOKI_ENABLED", "true").lower() == "true"

    # Redis Configuration (for Celery and job queue)
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))

    # Celery Configuration
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/1")
    
    def resolve_service_url(self, url: str) -> str:
        """
        Resolve service URL - supports consul:// URLs for service discovery
        """
        if url.startswith("consul://"):
            from app.components.consul_discovery import discover_service_url
            service_name = url.replace("consul://", "").split("/")[0]
            remaining_path = url.replace(f"consul://{service_name}", "")
            
            # Default URLs for fallback
            defaults = {
                "models": "http://localhost:8082",
                "mcp": "http://localhost:8081"
            }
            
            discovered_url = discover_service_url(service_name, defaults.get(service_name))
            if discovered_url:
                return discovered_url + remaining_path
            return url
        return url
    
    @property
    def isa_api_url(self) -> str:
        """Get ISA API URL via Consul discovery with ENV fallback"""
        from app.components.consul_discovery import discover_service_url
        # Try ENV first as override (for special cases like external URLs)
        env_url = os.getenv("ISA_API_URL")
        if env_url:
            return env_url
        # Use Consul discovery with fallback - Model service registers as "model_service"
        return discover_service_url("model_service", "http://localhost:8082")
    
    @property
    def mcp_server_url(self) -> str:
        """Get MCP server URL via Consul discovery with ENV fallback"""
        from app.components.consul_discovery import discover_service_url
        # Try ENV first as override (for special cases like external URLs)
        env_url = os.getenv("MCP_SERVER_URL")
        if env_url:
            return env_url
        # Use Consul discovery with fallback - MCP service registers as "mcp_service"
        return discover_service_url("mcp_service", "http://127.0.0.1:8081")
    
    @property 
    def resolved_isa_api_url(self) -> str:
        """Get resolved ISA API URL with service discovery"""
        url = self.resolve_service_url(self.isa_api_url)
        # Fix httpx IPv6 issue with localhost
        return url.replace("localhost", "127.0.0.1")
    
    @property
    def resolved_mcp_server_url(self) -> str:
        """Get resolved MCP server URL with service discovery"""  
        url = self.resolve_service_url(self.mcp_server_url)
        # Fix httpx IPv6 issue with localhost
        return url.replace("localhost", "127.0.0.1")
    
    # OpenAI Configuration (legacy support)
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_api_base: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")  # Default: fast & cheap
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0"))
    
    
    # Database Configuration
    checkpoint_db_path: str = os.getenv("CHECKPOINT_DB_PATH", "conversation_checkpoints.db")
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("PORT", os.getenv("API_PORT", "8080")))  # Railway uses PORT
    api_debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # Session Configuration
    default_session_timeout: int = int(os.getenv("DEFAULT_SESSION_TIMEOUT", "3600"))  # 1 hour
    max_conversation_history: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "100"))
    
    # Supabase Configuration
    supabase_url: str = os.getenv("SUPABASE_LOCAL_URL", os.getenv("SUPABASE_CLOUD_URL", os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")))
    supabase_anon_key: str = os.getenv("SUPABASE_LOCAL_ANON_KEY", os.getenv("SUPABASE_CLOUD_ANON_KEY", os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")))
    supabase_service_role_key: str = os.getenv("SUPABASE_LOCAL_SERVICE_ROLE_KEY", os.getenv("SUPABASE_CLOUD_SERVICE_ROLE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")))
    supabase_password: str = os.getenv("SUPABASE_PWD", "")
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # Database Schema Configuration
    database_schema: str = os.getenv("DATABASE_SCHEMA", os.getenv("ENVIRONMENT", "dev"))
    
    # Billing Configuration
    credit_to_usd_rate: float = float(os.getenv("CREDIT_TO_USD_RATE", "0.01"))  # 1 credit = $0.01
    min_credits_per_request: float = float(os.getenv("MIN_CREDITS_PER_REQUEST", "0.1"))  # 最小计费 0.1 credit
    token_to_usd_rate: float = float(os.getenv("TOKEN_TO_USD_RATE", "0.00001"))  # $0.00001 per token (估算)
    tokens_per_credit: int = int(os.getenv("TOKENS_PER_CREDIT", "100"))  # 100 tokens ≈ 1 credit (备用估算)
    
    # MCP Tool Billing Rates (per tool call)
    mcp_tool_base_credits: float = float(os.getenv("MCP_TOOL_BASE_CREDITS", "0.5"))  # 基础 MCP 工具调用费用
    image_generation_credits: float = float(os.getenv("IMAGE_GENERATION_CREDITS", "5.0"))  # 图像生成费用
    web_search_credits: float = float(os.getenv("WEB_SEARCH_CREDITS", "1.0"))  # 网络搜索费用
    
    # Logging Configuration (Centralized via Loki)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_file: str = os.getenv("LOG_FILE", "")  # Deprecated - using Loki for centralized logging
    
    # Security Configuration
    api_master_key: Optional[str] = os.getenv("API_MASTER_KEY")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:8080,http://127.0.0.1:8080,http://localhost:8888")
    cors_credentials: bool = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "dev")

    # Application Version
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Service Discovery via Consul (no ENV needed!)
    @computed_field
    @property
    def auth_service_url(self) -> str:
        """Discover auth service via Consul"""
        from app.components.consul_discovery import discover_service_url
        # Try Consul first, fallback to ENV only if explicitly set
        env_url = os.getenv("AUTH_SERVICE_URL")
        if env_url:
            return env_url  # Allow override for special cases
        return discover_service_url("authorization_service", "http://localhost:8204") + "/api/v1/authorization"
    
    @computed_field
    @property
    def account_service_url(self) -> str:
        """Discover account service via Consul"""
        from app.components.consul_discovery import discover_service_url
        env_url = os.getenv("ACCOUNT_SERVICE_URL")
        if env_url:
            return env_url
        return discover_service_url("account_service", "http://localhost:8202")
    
    @computed_field
    @property
    def wallet_service_url(self) -> str:
        """Discover wallet service via Consul"""
        from app.components.consul_discovery import discover_service_url
        env_url = os.getenv("WALLET_SERVICE_URL")
        if env_url:
            return env_url
        return discover_service_url("wallet_service", "http://localhost:8208")
    
    @computed_field
    @property
    def session_service_url(self) -> str:
        """Discover session service via Consul"""
        from app.components.consul_discovery import discover_service_url
        env_url = os.getenv("SESSION_SERVICE_URL")
        if env_url:
            return env_url
        return discover_service_url("session_service", "http://localhost:8203")
    
    @computed_field
    @property
    def storage_service_url(self) -> str:
        """Discover storage service via Consul"""
        from app.components.consul_discovery import discover_service_url
        env_url = os.getenv("STORAGE_SERVICE_URL")
        if env_url:
            return env_url
        return discover_service_url("storage_service", "http://localhost:8209")
    
    # CLI Configuration
    cli_api_base_url: str = os.getenv("CLI_API_BASE_URL", "http://localhost:8080")

    @property
    def is_production(self) -> bool:
        return self.environment in ("production", "staging")
    
    @property
    def allowed_origins(self) -> list[str]:
        """Get allowed CORS origins based on environment"""
        if self.is_production:
            # Production: only specific domains
            origins = self.cors_origins.split(",")
            return [origin.strip() for origin in origins if origin.strip()]
        else:
            # Development: allow localhost variants including 5173
            default_origins = [
                "http://localhost:5173",  # Vite dev server
                "http://localhost:3000",  # React dev server
                "http://localhost:8080",  # Our API server
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000", 
                "http://127.0.0.1:8080",
                "http://0.0.0.0:8080"
            ]
            if self.cors_origins != "http://localhost:5173,http://localhost:3000,http://localhost:8080,http://127.0.0.1:8080":
                origins = self.cors_origins.split(",")
                custom_origins = [origin.strip() for origin in origins if origin.strip()]
                return list(set(default_origins + custom_origins))
            return default_origins
    
    class Config:
        env_file = ".env.local"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_openai_api_key() -> Optional[SecretStr]:
    """Get OpenAI API key as SecretStr"""
    if settings.openai_api_key:
        return SecretStr(settings.openai_api_key)
    return None 