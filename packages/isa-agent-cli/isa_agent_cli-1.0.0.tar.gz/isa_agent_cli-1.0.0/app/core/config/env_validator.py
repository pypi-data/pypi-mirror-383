"""
Environment Variable Validation
Ensures all required environment variables are set and valid
"""
import os
import sys
from typing import Dict, List, Optional, Any
from ...utils.logger import api_logger


class EnvironmentValidator:
    """Validates environment variables for production readiness"""
    
    def __init__(self):
        self.required_vars: Dict[str, Dict[str, Any]] = {}
        self.optional_vars: Dict[str, Dict[str, Any]] = {}
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
        
        self._define_variables()
    
    def _define_variables(self):
        """Define required and optional environment variables"""
        
        # Required variables
        self.required_vars = {
            "SUPABASE_LOCAL_URL": {
                "description": "Supabase database URL",
                "example": "http://127.0.0.1:54321",
                "validator": self._validate_url
            },
            "SUPABASE_LOCAL_ANON_KEY": {
                "description": "Supabase anonymous key",
                "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "validator": self._validate_jwt_like
            }
        }
        
        # Optional variables with defaults
        self.optional_vars = {
            "ENVIRONMENT": {
                "description": "Application environment",
                "default": "dev",
                "valid_values": ["dev", "test", "staging", "production"],
                "validator": self._validate_choice
            },
            "API_HOST": {
                "description": "API host address",
                "default": "0.0.0.0",
                "validator": self._validate_host
            },
            "API_PORT": {
                "description": "API port number",
                "default": "8080",
                "validator": self._validate_port
            },
            "LOG_LEVEL": {
                "description": "Logging level",
                "default": "INFO",
                "valid_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                "validator": self._validate_choice
            },
            "API_MASTER_KEY": {
                "description": "Master API key for admin operations",
                "required_for_production": True,
                "validator": self._validate_api_key
            },
            "CORS_ORIGINS": {
                "description": "Allowed CORS origins (comma-separated)",
                "default": "http://localhost:5173,http://localhost:3000",
                "validator": self._validate_cors_origins
            }
        }
    
    def validate_all(self, strict: bool = False) -> bool:
        """Validate all environment variables"""
        self.validation_errors.clear()
        self.validation_warnings.clear()

        environment = os.getenv("ENVIRONMENT", "dev")
        is_production = environment == "production"  # Only production, not staging
        
        # Validate required variables
        for var_name, config in self.required_vars.items():
            value = os.getenv(var_name)
            
            if not value:
                self.validation_errors.append(
                    f"❌ Missing required environment variable: {var_name}\n"
                    f"   Description: {config['description']}\n"
                    f"   Example: {config.get('example', 'N/A')}"
                )
                continue
            
            # Run custom validator
            if "validator" in config:
                try:
                    if not config["validator"](value, config):
                        self.validation_errors.append(
                            f"❌ Invalid value for {var_name}: {value[:50]}..."
                        )
                except Exception as e:
                    self.validation_errors.append(
                        f"❌ Validation error for {var_name}: {e}"
                    )
        
        # Validate optional variables
        for var_name, config in self.optional_vars.items():
            value = os.getenv(var_name)
            
            # Check if required for production
            if (is_production and config.get("required_for_production", False) and not value):
                self.validation_errors.append(
                    f"❌ Missing production-required variable: {var_name}\n"
                    f"   Description: {config['description']}"
                )
                continue
            
            # Use default if not set
            if not value:
                if "default" in config:
                    os.environ[var_name] = config["default"]
                    self.validation_warnings.append(
                        f"⚠️  Using default value for {var_name}: {config['default']}"
                    )
                continue
            
            # Run custom validator
            if "validator" in config:
                try:
                    if not config["validator"](value, config):
                        if strict:
                            self.validation_errors.append(
                                f"❌ Invalid value for {var_name}: {value[:50]}..."
                            )
                        else:
                            self.validation_warnings.append(
                                f"⚠️  Questionable value for {var_name}: {value[:50]}..."
                            )
                except Exception as e:
                    self.validation_warnings.append(
                        f"⚠️  Validation warning for {var_name}: {e}"
                    )
        
        # Production-specific validations
        if is_production:
            self._validate_production_security()
        
        return len(self.validation_errors) == 0
    
    def _validate_production_security(self):
        """Additional security validations for production"""
        cors_origins = os.getenv("CORS_ORIGINS", "")
        
        if "*" in cors_origins:
            self.validation_errors.append(
                "❌ Production security violation: CORS_ORIGINS contains wildcard '*'"
            )
        
        if "localhost" in cors_origins:
            self.validation_warnings.append(
                "⚠️  Production warning: CORS_ORIGINS contains localhost"
            )
        
        api_debug = os.getenv("API_DEBUG", "").lower()
        if api_debug == "true":
            self.validation_errors.append(
                "❌ Production security violation: API_DEBUG is enabled"
            )
    
    def _validate_url(self, value: str, config: Dict) -> bool:
        """Validate URL format"""
        return value.startswith(("http://", "https://")) and len(value) > 10
    
    def _validate_jwt_like(self, value: str, config: Dict) -> bool:
        """Validate JWT-like string"""
        return len(value) > 50 and value.count(".") >= 2
    
    def _validate_choice(self, value: str, config: Dict) -> bool:
        """Validate value is in allowed choices"""
        valid_values = config.get("valid_values", [])
        return value in valid_values if valid_values else True
    
    def _validate_host(self, value: str, config: Dict) -> bool:
        """Validate host address"""
        return value in ["0.0.0.0", "127.0.0.1", "localhost"] or "." in value
    
    def _validate_port(self, value: str, config: Dict) -> bool:
        """Validate port number"""
        try:
            port = int(value)
            return 1 <= port <= 65535
        except ValueError:
            return False
    
    def _validate_api_key(self, value: str, config: Dict) -> bool:
        """Validate API key strength"""
        if len(value) < 32:
            return False
        if value in ["changeme", "password", "secret", "key"]:
            return False
        return True
    
    def _validate_cors_origins(self, value: str, config: Dict) -> bool:
        """Validate CORS origins"""
        origins = [origin.strip() for origin in value.split(",")]
        for origin in origins:
            if origin and not (origin == "*" or origin.startswith(("http://", "https://"))):
                return False
        return True
    
    def print_report(self):
        """Print validation report"""
        api_logger.info("🔍 Environment Variable Validation Report")
        api_logger.info("=" * 50)
        
        if self.validation_errors:
            api_logger.error("❌ VALIDATION ERRORS:")
            for error in self.validation_errors:
                api_logger.error(error)
        
        if self.validation_warnings:
            api_logger.warning("⚠️  VALIDATION WARNINGS:")
            for warning in self.validation_warnings:
                api_logger.warning(warning)
        
        if not self.validation_errors and not self.validation_warnings:
            api_logger.info("✅ All environment variables are valid!")
        
        environment = os.getenv("ENVIRONMENT", "dev")
        api_logger.info(f"🌍 Current environment: {environment}")
        api_logger.info("=" * 50)
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """Get summary of environment configuration"""
        return {
            "environment": os.getenv("ENVIRONMENT", "dev"),
            "api_host": os.getenv("API_HOST", "0.0.0.0"),
            "api_port": os.getenv("API_PORT", "8080"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "has_master_key": bool(os.getenv("API_MASTER_KEY")),
            "cors_origins_count": len(os.getenv("CORS_ORIGINS", "").split(",")),
            "validation_status": {
                "errors": len(self.validation_errors),
                "warnings": len(self.validation_warnings),
                "is_valid": len(self.validation_errors) == 0
            }
        }


# Global validator instance
env_validator = EnvironmentValidator()


def validate_environment(strict: bool = False) -> bool:
    """Validate environment variables"""
    return env_validator.validate_all(strict)


def print_environment_report():
    """Print environment validation report"""
    env_validator.print_report()


def get_environment_status() -> Dict[str, Any]:
    """Get environment status for health checks"""
    return env_validator.get_environment_summary()