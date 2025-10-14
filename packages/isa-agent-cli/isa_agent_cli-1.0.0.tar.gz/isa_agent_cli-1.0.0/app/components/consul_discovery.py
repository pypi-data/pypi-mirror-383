#!/usr/bin/env python3
"""
Consul Service Discovery Client
"""

import logging
import consul
from typing import Optional, Dict, List
import os

logger = logging.getLogger(__name__)

class ConsulServiceDiscovery:
    """Consul service discovery client"""
    
    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        """Initialize Consul client"""
        self.consul_host = consul_host
        self.consul_port = consul_port
        self._consul = consul.Consul(host=consul_host, port=consul_port)
        
    def get_service_url(self, service_name: str, default_url: Optional[str] = None) -> Optional[str]:
        """
        Get service URL from Consul by service name
        
        Args:
            service_name: Name of the service to discover (e.g., 'mcp', 'models')
            default_url: Fallback URL if service not found
            
        Returns:
            Service URL or default_url if not found
        """
        try:
            # Get all services (temporarily disabled health check for staging)
            services = self._consul.health.service(service_name, passing=False)[1]
            
            if not services:
                logger.warning(f"No service instances found for service '{service_name}'")
                return default_url
                
            # Use first available service instance (health check disabled for staging)
            service = services[0]
            service_info = service['Service']
            address = service_info['Address']
            port = service_info['Port']
            
            service_url = f"http://{address}:{port}"
            logger.info(f"Discovered service '{service_name}' at {service_url}")
            return service_url
            
        except Exception as e:
            logger.error(f"Failed to discover service '{service_name}': {e}")
            return default_url
    
    def get_all_services(self) -> Dict[str, List[str]]:
        """Get all registered services"""
        try:
            services = self._consul.agent.services()
            result = {}
            for service_id, service_info in services.items():
                service_name = service_info['Service']
                if service_name not in result:
                    result[service_name] = []
                service_url = f"http://{service_info['Address']}:{service_info['Port']}"
                result[service_name].append(service_url)
            return result
        except Exception as e:
            logger.error(f"Failed to get all services: {e}")
            return {}

# Global discovery instance
_discovery_instance = None

def get_consul_discovery() -> ConsulServiceDiscovery:
    """Get global Consul discovery instance"""
    global _discovery_instance
    if _discovery_instance is None:
        consul_host = os.getenv("CONSUL_HOST", "localhost")
        consul_port = int(os.getenv("CONSUL_PORT", "8500"))
        _discovery_instance = ConsulServiceDiscovery(consul_host, consul_port)
    return _discovery_instance

def discover_service_url(service_name: str, default_url: Optional[str] = None) -> Optional[str]:
    """Convenient function to discover service URL"""
    discovery = get_consul_discovery()
    return discovery.get_service_url(service_name, default_url)