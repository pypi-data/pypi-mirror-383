"""
Local GPU deployment provider

Unified provider for local GPU model deployment with support for multiple backends:
- vLLM for high-performance LLM inference
- TensorRT-LLM for maximum optimization
- HuggingFace Transformers for universal compatibility
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime

from .config import LocalGPUConfig, LocalServiceType, LocalBackend
from .vllm_service import VLLMService
from .tensorrt_service import TensorRTLLMService
from .transformers_service import TransformersService
from .health_checker import get_health_checker, ServiceStatus
from ...utils.gpu_utils import get_gpu_manager

logger = logging.getLogger(__name__)


class LocalGPUProvider:
    """
    Unified local GPU deployment provider.
    
    This provider manages local GPU model deployments with support for:
    - Multiple inference backends (vLLM, TensorRT-LLM, Transformers)
    - Automatic GPU resource management
    - Service health monitoring
    - Performance optimization
    
    Example:
        ```python
        from isa_model.deployment.local import LocalGPUProvider, create_vllm_config
        
        # Initialize provider
        provider = LocalGPUProvider()
        
        # Create service configuration
        config = create_vllm_config(
            service_name="llama2-7b",
            model_id="meta-llama/Llama-2-7b-chat-hf"
        )
        
        # Deploy service
        result = await provider.deploy(config)
        print(f"Service deployed: {result['service_url']}")
        
        # Use the service
        response = await provider.generate_text(
            service_name="llama2-7b",
            prompt="Hello, how are you?"
        )
        ```
    """
    
    def __init__(self, workspace_dir: str = "./local_deployments"):
        """
        Initialize local GPU provider.
        
        Args:
            workspace_dir: Directory for deployment artifacts and logs
        """
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Component managers
        self.gpu_manager = get_gpu_manager()
        self.health_checker = get_health_checker()
        
        # Service tracking
        self.services: Dict[str, Any] = {}  # service_name -> service instance
        self.configs: Dict[str, LocalGPUConfig] = {}  # service_name -> config
        self.deployments: Dict[str, Dict[str, Any]] = {}  # deployment tracking
        
        # Service registry file
        self.registry_file = self.workspace_dir / "service_registry.json"
        self._load_registry()
        
        logger.info("Local GPU provider initialized")
        logger.info(f"Workspace directory: {self.workspace_dir}")
        logger.info(f"Available GPUs: {len(self.gpu_manager.gpus)}")
    
    async def deploy(self, config: LocalGPUConfig) -> Dict[str, Any]:
        """
        Deploy a model service with the specified configuration.
        
        Args:
            config: Local GPU deployment configuration
            
        Returns:
            Deployment result with service information
        """
        service_name = config.service_name
        
        logger.info("=" * 60)
        logger.info(f"STARTING LOCAL DEPLOYMENT: {service_name}")
        logger.info(f"MODEL: {config.model_id}")
        logger.info(f"BACKEND: {config.backend.value}")
        logger.info("=" * 60)
        
        try:
            # Check if service already exists
            if service_name in self.services:
                return {
                    "success": False,
                    "error": f"Service {service_name} already deployed",
                    "existing_service": self.get_service_info(service_name)
                }
            
            # Validate configuration
            validation_result = await self._validate_config(config)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Configuration validation failed: {validation_result['error']}",
                    "validation_details": validation_result
                }
            
            # Create service instance
            service = await self._create_service(config)
            if not service:
                return {
                    "success": False,
                    "error": f"Failed to create service for backend: {config.backend.value}"
                }
            
            # Deploy based on backend type
            deployment_start_time = datetime.now()
            
            if config.backend == LocalBackend.VLLM:
                deploy_result = await self._deploy_vllm_service(service, config)
            elif config.backend == LocalBackend.TENSORRT_LLM:
                deploy_result = await self._deploy_tensorrt_service(service, config)
            elif config.backend == LocalBackend.TRANSFORMERS:
                deploy_result = await self._deploy_transformers_service(service, config)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported backend: {config.backend.value}"
                }
            
            if deploy_result["success"]:
                # Register service
                self.services[service_name] = service
                self.configs[service_name] = config
                
                # Track deployment
                deployment_info = {
                    "service_name": service_name,
                    "config": config.to_dict(),
                    "backend": config.backend.value,
                    "deployed_at": deployment_start_time.isoformat(),
                    "status": "deployed",
                    **deploy_result
                }
                self.deployments[service_name] = deployment_info
                
                # Register with health checker
                self.health_checker.register_service(service_name, service)
                await self.health_checker.start_monitoring(service_name)
                
                # Save registry
                self._save_registry()
                
                logger.info("=" * 60)
                logger.info("LOCAL DEPLOYMENT COMPLETED SUCCESSFULLY!")
                logger.info("=" * 60)
                logger.info(f"Service: {service_name}")
                logger.info(f"Backend: {config.backend.value}")
                
                return {
                    "success": True,
                    "service_name": service_name,
                    "backend": config.backend.value,
                    "deployment_info": deployment_info,
                    **deploy_result
                }
            else:
                return deploy_result
                
        except Exception as e:
            logger.error("=" * 60)
            logger.error("LOCAL DEPLOYMENT FAILED!")
            logger.error("=" * 60)
            logger.error(f"Error: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "service_name": service_name
            }
    
    async def undeploy(self, service_name: str) -> Dict[str, Any]:
        """
        Stop and remove a deployed service.
        
        Args:
            service_name: Name of service to undeploy
            
        Returns:
            Undeploy result
        """
        if service_name not in self.services:
            return {
                "success": False,
                "error": f"Service {service_name} not found"
            }
        
        try:
            logger.info(f"Undeploying service: {service_name}")
            
            service = self.services[service_name]
            
            # Stop monitoring
            await self.health_checker.stop_monitoring(service_name)
            self.health_checker.unregister_service(service_name)
            
            # Stop service
            if hasattr(service, 'stop'):
                stop_result = await service.stop()
            elif hasattr(service, 'unload_model'):
                stop_result = await service.unload_model()
            else:
                stop_result = {"success": True}
            
            # Clean up
            if hasattr(service, 'cleanup'):
                await service.cleanup()
            
            # Remove from tracking
            del self.services[service_name]
            del self.configs[service_name]
            if service_name in self.deployments:
                del self.deployments[service_name]
            
            # Save registry
            self._save_registry()
            
            logger.info(f"Service undeployed: {service_name}")
            
            return {
                "success": True,
                "service_name": service_name,
                "stop_result": stop_result
            }
            
        except Exception as e:
            logger.error(f"Failed to undeploy service {service_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_services(self) -> List[Dict[str, Any]]:
        """List all deployed services"""
        services = []
        
        for service_name, service in self.services.items():
            try:
                config = self.configs[service_name]
                health = await self.health_checker.check_service_health(service_name)
                metrics = self.health_checker.get_service_metrics(service_name)
                
                service_info = {
                    "service_name": service_name,
                    "model_id": config.model_id,
                    "backend": config.backend.value,
                    "service_type": config.service_type.value,
                    "status": health.get("status", "unknown"),
                    "healthy": health.get("healthy", False),
                    "response_time_ms": health.get("response_time_ms"),
                    "error_count": metrics.error_count if metrics else 0,
                    "uptime_seconds": metrics.uptime_seconds if metrics else None,
                    "deployed_at": self.deployments.get(service_name, {}).get("deployed_at")
                }
                
                # Add service-specific info
                if hasattr(service, 'get_service_info'):
                    service_info.update(service.get_service_info())
                
                services.append(service_info)
                
            except Exception as e:
                logger.error(f"Error getting info for service {service_name}: {e}")
                services.append({
                    "service_name": service_name,
                    "status": "error",
                    "error": str(e)
                })
        
        return services
    
    async def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific service"""
        if service_name not in self.services:
            return None
        
        try:
            service = self.services[service_name]
            config = self.configs[service_name]
            health = await self.health_checker.check_service_health(service_name)
            metrics = self.health_checker.get_service_metrics(service_name)
            
            info = {
                "service_name": service_name,
                "config": config.to_dict(),
                "health": health,
                "metrics": {
                    "status": metrics.status.value if metrics else "unknown",
                    "last_check": metrics.last_check.isoformat() if metrics else None,
                    "error_count": metrics.error_count if metrics else 0,
                    "consecutive_failures": metrics.consecutive_failures if metrics else 0,
                    "uptime_seconds": metrics.uptime_seconds if metrics else None,
                    "last_error": metrics.last_error if metrics else None
                } if metrics else {},
                "deployment_info": self.deployments.get(service_name, {})
            }
            
            # Add service-specific info
            if hasattr(service, 'get_service_info'):
                info["service_details"] = service.get_service_info()
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting service info for {service_name}: {e}")
            return {
                "service_name": service_name,
                "error": str(e)
            }
    
    async def generate_text(self, service_name: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using a deployed service"""
        if service_name not in self.services:
            return {
                "success": False,
                "error": f"Service {service_name} not found"
            }
        
        try:
            service = self.services[service_name]
            
            # Check service health
            health = await self.health_checker.check_service_health(service_name)
            if not health.get("healthy", False):
                return {
                    "success": False,
                    "error": f"Service {service_name} is not healthy: {health.get('error', 'Unknown error')}"
                }
            
            # Generate text
            if hasattr(service, 'generate'):
                return await service.generate(prompt, **kwargs)
            elif hasattr(service, 'generate_text'):
                return await service.generate_text(prompt, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Service {service_name} does not support text generation"
                }
                
        except Exception as e:
            logger.error(f"Text generation failed for service {service_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def chat_completion(self, service_name: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate chat completion using a deployed service"""
        if service_name not in self.services:
            return {
                "success": False,
                "error": f"Service {service_name} not found"
            }
        
        try:
            service = self.services[service_name]
            
            # Check service health
            health = await self.health_checker.check_service_health(service_name)
            if not health.get("healthy", False):
                return {
                    "success": False,
                    "error": f"Service {service_name} is not healthy"
                }
            
            # Generate chat completion
            if hasattr(service, 'chat_completions'):
                return await service.chat_completions(messages, **kwargs)
            elif hasattr(service, 'chat_completion'):
                return await service.chat_completion(messages, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Service {service_name} does not support chat completion"
                }
                
        except Exception as e:
            logger.error(f"Chat completion failed for service {service_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        system_health = self.health_checker.get_system_health()
        
        return {
            **system_health,
            "provider": "local_gpu",
            "workspace_dir": str(self.workspace_dir),
            "total_deployments": len(self.services),
            "available_backends": [backend.value for backend in LocalBackend],
            "gpu_status": {
                "cuda_available": self.gpu_manager.cuda_available,
                "nvidia_smi_available": self.gpu_manager.nvidia_smi_available,
                "gpu_count": len(self.gpu_manager.gpus)
            }
        }
    
    async def _validate_config(self, config: LocalGPUConfig) -> Dict[str, Any]:
        """Validate deployment configuration"""
        try:
            # Check GPU requirements
            compatibility = self.gpu_manager.check_gpu_compatibility(
                config.model_id,
                config.model_precision
            )
            
            if not compatibility[0]:
                return {
                    "valid": False,
                    "error": f"GPU compatibility check failed: {', '.join(compatibility[1])}"
                }
            
            # Check backend availability
            backend_available = await self._check_backend_availability(config.backend)
            if not backend_available["available"]:
                return {
                    "valid": False,
                    "error": f"Backend {config.backend.value} not available: {backend_available['error']}"
                }
            
            # Check port availability
            if config.backend == LocalBackend.VLLM:
                port_available = await self._check_port_available(config.port)
                if not port_available:
                    return {
                        "valid": False,
                        "error": f"Port {config.port} is not available"
                    }
            
            return {
                "valid": True,
                "gpu_compatibility": compatibility,
                "backend_check": backend_available
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def _check_backend_availability(self, backend: LocalBackend) -> Dict[str, Any]:
        """Check if a backend is available"""
        try:
            if backend == LocalBackend.VLLM:
                try:
                    import vllm
                    return {"available": True}
                except ImportError:
                    return {"available": False, "error": "vLLM not installed"}
            
            elif backend == LocalBackend.TENSORRT_LLM:
                try:
                    import tensorrt_llm
                    return {"available": True}
                except ImportError:
                    return {"available": False, "error": "TensorRT-LLM not installed"}
            
            elif backend == LocalBackend.TRANSFORMERS:
                try:
                    import transformers
                    return {"available": True}
                except ImportError:
                    return {"available": False, "error": "Transformers not installed"}
            
            else:
                return {"available": False, "error": f"Unknown backend: {backend.value}"}
                
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    async def _check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', port))
                return result != 0  # Port is available if connection fails
        except:
            return False
    
    async def _create_service(self, config: LocalGPUConfig) -> Optional[Any]:
        """Create service instance based on backend"""
        try:
            if config.backend == LocalBackend.VLLM:
                return VLLMService(config)
            elif config.backend == LocalBackend.TENSORRT_LLM:
                return TensorRTLLMService(config)
            elif config.backend == LocalBackend.TRANSFORMERS:
                return TransformersService(config)
            else:
                logger.error(f"Unsupported backend: {config.backend.value}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create service: {e}")
            return None
    
    async def _deploy_vllm_service(self, service: VLLMService, config: LocalGPUConfig) -> Dict[str, Any]:
        """Deploy vLLM service"""
        result = await service.start()
        if result["success"]:
            return {
                **result,
                "service_url": f"http://{config.host}:{config.port}",
                "api_base": f"http://{config.host}:{config.port}/v1"
            }
        return result
    
    async def _deploy_tensorrt_service(self, service: TensorRTLLMService, config: LocalGPUConfig) -> Dict[str, Any]:
        """Deploy TensorRT-LLM service"""
        # Build engine first
        build_result = await service.build_engine()
        if not build_result["success"]:
            return build_result
        
        # Load model
        load_result = await service.load_model()
        return load_result
    
    async def _deploy_transformers_service(self, service: TransformersService, config: LocalGPUConfig) -> Dict[str, Any]:
        """Deploy Transformers service"""
        return await service.load_model()
    
    def _load_registry(self):
        """Load service registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    registry_data = json.load(f)
                    
                # Note: We don't automatically reload services on startup
                # This would require more complex state management
                logger.info(f"Service registry loaded: {len(registry_data)} entries")
                
            except Exception as e:
                logger.warning(f"Failed to load service registry: {e}")
    
    def _save_registry(self):
        """Save service registry to file"""
        try:
            registry_data = {}
            for service_name, deployment in self.deployments.items():
                registry_data[service_name] = {
                    "config": deployment["config"],
                    "deployed_at": deployment["deployed_at"],
                    "backend": deployment["backend"]
                }
            
            with open(self.registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save service registry: {e}")