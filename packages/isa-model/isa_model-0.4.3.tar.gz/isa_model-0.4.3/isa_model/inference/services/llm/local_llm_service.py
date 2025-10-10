#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Local LLM Service - Direct local GPU inference service
Provides high-performance local model inference using vLLM, TensorRT-LLM, and Transformers
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from isa_model.inference.services.base_service import BaseService
from isa_model.core.models.model_manager import ModelManager
from isa_model.core.config import ConfigManager
from isa_model.core.dependencies import DependencyChecker, is_torch_available, is_transformers_available

# Conditional imports for local deployment
try:
    from isa_model.deployment.local import (
        LocalGPUProvider, LocalGPUConfig, LocalServiceType, LocalBackend,
        create_vllm_config, create_tensorrt_config, create_transformers_config
    )
    LOCAL_DEPLOYMENT_AVAILABLE = True
except ImportError:
    LOCAL_DEPLOYMENT_AVAILABLE = False
    LocalGPUProvider = None
    LocalGPUConfig = None
    LocalServiceType = None
    LocalBackend = None
    
# Conditional import for GPU utilities
try:
    from isa_model.utils.gpu_utils import get_gpu_manager
    GPU_UTILS_AVAILABLE = True
except ImportError:
    GPU_UTILS_AVAILABLE = False
    get_gpu_manager = None

logger = logging.getLogger(__name__)


class LocalLLMService(BaseService):
    """
    Local LLM Service - Direct local GPU inference
    
    Features:
    - Multiple inference backends (vLLM, TensorRT-LLM, Transformers)
    - Automatic GPU resource management
    - Model deployment and lifecycle management
    - High-performance local inference
    - No cloud dependency
    
    Example:
        ```python
        service = LocalLLMService()
        
        # Deploy a model
        await service.deploy_model("meta-llama/Llama-2-7b-chat-hf", backend="vllm")
        
        # Generate text
        result = await service.complete("Hello, how are you?")
        print(result['text'])
        ```
    """
    
    def __init__(
        self,
        provider_name: str = "local",
        model_name: str = None,
        model_manager: ModelManager = None,
        config_manager: ConfigManager = None,
        workspace_dir: str = "./local_llm_services",
        auto_deploy_models: List[str] = None,
        preferred_backend: str = "transformers",
        **kwargs
    ):
        # Check dependencies based on preferred backend
        if preferred_backend == "transformers":
            if not is_torch_available() or not is_transformers_available():
                install_cmd = DependencyChecker.get_install_command(group="local_llm")
                raise ImportError(
                    f"Local LLM inference requires PyTorch and Transformers.\n"
                    f"Install with: {install_cmd}"
                )
        elif preferred_backend == "vllm":
            available, missing = DependencyChecker.check_group("vllm")
            if not available:
                install_cmd = DependencyChecker.get_install_command(group="vllm")
                raise ImportError(
                    f"vLLM backend requires additional dependencies: {', '.join(missing)}.\n"
                    f"Install with: {install_cmd}"
                )
        
        # Check if local deployment is available
        if not LOCAL_DEPLOYMENT_AVAILABLE:
            logger.warning(
                "Local deployment modules are not available. "
                "Some features may be limited. "
                "Install with: pip install 'isa-model[local]'"
            )
        
        # Initialize base service
        self.provider_name = provider_name
        self.model_name = model_name or "local-llm"
        self.workspace_dir = Path(workspace_dir)
        self.preferred_backend = preferred_backend
        self.auto_deploy_models = auto_deploy_models or []
        
        # Initialize local GPU provider if available
        try:
            if LOCAL_DEPLOYMENT_AVAILABLE and GPU_UTILS_AVAILABLE:
                self.local_provider = LocalGPUProvider(str(self.workspace_dir))
                self.gpu_manager = get_gpu_manager()
                self.gpu_available = self.gpu_manager.cuda_available
                logger.info("✅ Local GPU provider initialized")
            else:
                logger.warning("⚠️ Local GPU provider not available - CPU inference only")
                self.local_provider = None
                self.gpu_manager = None
                self.gpu_available = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize local GPU provider: {e}")
            self.local_provider = None
            self.gpu_manager = None
            self.gpu_available = False
        
        # Service state
        self.deployed_models: Dict[str, str] = {}  # model_id -> service_name
        self.default_service: Optional[str] = None
        self.request_count = 0
        
        # Configuration
        self.config_manager = config_manager or ConfigManager()
        self.local_config = self.config_manager.get_local_gpu_config()
        
        logger.info(f"Local LLM Service initialized (GPU Available: {self.gpu_available})")
    
    async def initialize(self):
        """Initialize the service and auto-deploy models if configured"""
        if not self.gpu_available:
            logger.warning("⚠️ No GPU available, local inference will be limited")
            return
        
        # Auto-deploy models if specified
        for model_id in self.auto_deploy_models:
            try:
                logger.info(f"🚀 Auto-deploying model: {model_id}")
                result = await self.deploy_model(model_id, backend=self.preferred_backend)
                if result.get("success"):
                    logger.info(f"✅ Auto-deployed: {model_id}")
                else:
                    logger.warning(f"❌ Auto-deploy failed for {model_id}: {result.get('error')}")
            except Exception as e:
                logger.error(f"❌ Auto-deploy error for {model_id}: {e}")
    
    async def deploy_model(
        self,
        model_id: str,
        backend: str = None,
        service_name: str = None,
        **config_kwargs
    ) -> Dict[str, Any]:
        """
        Deploy a model to local GPU
        
        Args:
            model_id: HuggingFace model ID
            backend: Inference backend (vllm, tensorrt_llm, transformers)
            service_name: Custom service name
            **config_kwargs: Additional configuration parameters
            
        Returns:
            Deployment result
        """
        if not self.local_provider:
            return {
                "success": False,
                "error": "Local GPU provider not available"
            }
        
        try:
            # Generate service name
            if not service_name:
                service_name = f"local-{model_id.replace('/', '-').replace('_', '-')}"
            
            # Select backend
            backend = backend or self.preferred_backend
            backend_enum = LocalBackend(backend)
            
            # Create configuration based on backend
            if backend_enum == LocalBackend.VLLM:
                config = create_vllm_config(
                    service_name=service_name,
                    model_id=model_id,
                    **config_kwargs
                )
            elif backend_enum == LocalBackend.TENSORRT_LLM:
                config = create_tensorrt_config(
                    service_name=service_name,
                    model_id=model_id,
                    **config_kwargs
                )
            else:  # Transformers
                config = create_transformers_config(
                    service_name=service_name,
                    model_id=model_id,
                    **config_kwargs
                )
            
            logger.info(f"🚀 Deploying {model_id} with {backend} backend...")
            
            # Deploy the model
            result = await self.local_provider.deploy(config)
            
            if result.get("success"):
                # Track deployed model
                self.deployed_models[model_id] = service_name
                
                # Set as default if first model
                if not self.default_service:
                    self.default_service = service_name
                
                logger.info(f"✅ Model deployed successfully: {model_id} -> {service_name}")
                
                return {
                    "success": True,
                    "model_id": model_id,
                    "service_name": service_name,
                    "backend": backend,
                    "deployment_info": result
                }
            else:
                logger.error(f"❌ Deployment failed for {model_id}: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Deploy model error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def undeploy_model(self, model_id: str) -> Dict[str, Any]:
        """
        Undeploy a model from local GPU
        
        Args:
            model_id: Model ID to undeploy
            
        Returns:
            Undeploy result
        """
        if model_id not in self.deployed_models:
            return {
                "success": False,
                "error": f"Model {model_id} not deployed"
            }
        
        try:
            service_name = self.deployed_models[model_id]
            
            # Undeploy from local provider
            result = await self.local_provider.undeploy(service_name)
            
            if result.get("success"):
                # Remove from tracking
                del self.deployed_models[model_id]
                
                # Update default service if needed
                if self.default_service == service_name:
                    self.default_service = next(iter(self.deployed_models.values()), None)
                
                logger.info(f"✅ Model undeployed: {model_id}")
                
            return result
            
        except Exception as e:
            logger.error(f"❌ Undeploy error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def complete(
        self,
        prompt: str,
        model_id: str = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text completion using local model
        
        Args:
            prompt: Input text prompt
            model_id: Specific model to use (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling
            top_k: Top-k sampling
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text result
        """
        if not self.local_provider:
            return {
                "success": False,
                "error": "Local GPU provider not available",
                "provider": "local",
                "service": "local-llm"
            }
        
        try:
            # Select service to use
            service_name = None
            if model_id and model_id in self.deployed_models:
                service_name = self.deployed_models[model_id]
            elif self.default_service:
                service_name = self.default_service
            else:
                return {
                    "success": False,
                    "error": "No models deployed locally",
                    "provider": "local",
                    "service": "local-llm"
                }
            
            logger.info(f"🔄 Generating text with service: {service_name}")
            
            # Generate text
            result = await self.local_provider.generate_text(
                service_name=service_name,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                **kwargs
            )
            
            if result.get("success"):
                self.request_count += 1
                
                # Format response
                return {
                    "success": True,
                    "text": result.get("text", ""),
                    "generated_text": result.get("text", ""),
                    "full_text": prompt + " " + result.get("text", ""),
                    "prompt": prompt,
                    "model_id": model_id or "local-default",
                    "provider": "local",
                    "service": "local-llm",
                    "backend": result.get("backend", "unknown"),
                    "generation_config": {
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": top_p,
                        "top_k": top_k,
                        **kwargs
                    },
                    "metadata": {
                        "processing_time": result.get("generation_time", 0),
                        "service_name": service_name,
                        "input_tokens": result.get("input_tokens", 0),
                        "output_tokens": result.get("output_tokens", 0),
                        "total_tokens": result.get("total_tokens", 0),
                        "gpu_accelerated": True,
                        "local_inference": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Local inference failed"),
                    "provider": "local",
                    "service": "local-llm",
                    "details": result
                }
                
        except Exception as e:
            logger.error(f"❌ Local completion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "local",
                "service": "local-llm"
            }
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat completion using local model
        
        Args:
            messages: List of chat messages
            model_id: Specific model to use (optional)
            **kwargs: Additional generation parameters
            
        Returns:
            Chat completion result
        """
        if not self.local_provider:
            return {
                "success": False,
                "error": "Local GPU provider not available",
                "provider": "local",
                "service": "local-llm"
            }
        
        try:
            # Select service to use
            service_name = None
            if model_id and model_id in self.deployed_models:
                service_name = self.deployed_models[model_id]
            elif self.default_service:
                service_name = self.default_service
            else:
                return {
                    "success": False,
                    "error": "No models deployed locally",
                    "provider": "local",
                    "service": "local-llm"
                }
            
            logger.info(f"💬 Chat completion with service: {service_name}")
            
            # Generate chat completion
            result = await self.local_provider.chat_completion(
                service_name=service_name,
                messages=messages,
                **kwargs
            )
            
            if result.get("success"):
                self.request_count += 1
                
                # Format response
                response_content = ""
                if "choices" in result and result["choices"]:
                    response_content = result["choices"][0].get("message", {}).get("content", "")
                elif "text" in result:
                    response_content = result["text"]
                
                return {
                    "success": True,
                    "text": response_content,
                    "content": response_content,
                    "role": "assistant",
                    "messages": messages,
                    "response": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "model_id": model_id or "local-default",
                    "provider": "local",
                    "service": "local-llm",
                    "metadata": {
                        "processing_time": result.get("generation_time", 0),
                        "service_name": service_name,
                        "usage": result.get("usage", {}),
                        "gpu_accelerated": True,
                        "local_inference": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Local chat completion failed"),
                    "provider": "local",
                    "service": "local-llm",
                    "details": result
                }
                
        except Exception as e:
            logger.error(f"❌ Local chat completion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "local",
                "service": "local-llm"
            }
    
    async def get_model_info(self, model_id: str = None) -> Dict[str, Any]:
        """Get information about deployed models"""
        try:
            if not self.local_provider:
                return {
                    "success": False,
                    "error": "Local GPU provider not available"
                }
            
            if model_id and model_id in self.deployed_models:
                # Get info for specific model
                service_name = self.deployed_models[model_id]
                service_info = await self.local_provider.get_service_info(service_name)
                
                return {
                    "success": True,
                    "model_id": model_id,
                    "service_name": service_name,
                    "provider": "local",
                    "service": "local-llm",
                    "service_info": service_info
                }
            else:
                # Get info for all deployed models
                all_services = await self.local_provider.list_services()
                
                return {
                    "success": True,
                    "provider": "local",
                    "service": "local-llm",
                    "deployed_models": self.deployed_models,
                    "default_service": self.default_service,
                    "services": all_services,
                    "gpu_status": self.gpu_manager.get_system_info() if self.gpu_manager else None
                }
                
        except Exception as e:
            logger.error(f"❌ Get model info failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check local LLM service health"""
        try:
            if not self.local_provider:
                return {
                    "success": False,
                    "status": "error",
                    "provider": "local",
                    "service": "local-llm",
                    "error": "Local GPU provider not available"
                }
            
            # Get system status
            system_status = await self.local_provider.get_system_status()
            
            # Check deployed services
            services = await self.local_provider.list_services()
            healthy_services = [s for s in services if s.get("healthy", False)]
            
            return {
                "success": True,
                "status": "healthy" if len(healthy_services) > 0 else "no_services",
                "provider": "local",
                "service": "local-llm",
                "deployed_models": len(self.deployed_models),
                "healthy_services": len(healthy_services),
                "total_services": len(services),
                "gpu_available": self.gpu_available,
                "system_status": system_status,
                "usage_stats": {
                    "total_requests": self.request_count,
                    "deployed_models": list(self.deployed_models.keys()),
                    "default_service": self.default_service
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "success": False,
                "status": "error",
                "provider": "local",
                "service": "local-llm",
                "error": str(e)
            }
    
    def get_supported_tasks(self) -> List[str]:
        """Get supported task list"""
        return [
            "generate",     # Text generation
            "chat",         # Chat completion
            "complete",     # Text completion
            "deploy",       # Model deployment
            "undeploy"      # Model undeployment
        ]
    
    def get_supported_models(self) -> List[str]:
        """Get supported model types"""
        return [
            "llama",        # Llama models
            "mistral",      # Mistral models
            "qwen",         # Qwen models
            "gpt2",         # GPT-2 models
            "dialogpt",     # DialoGPT models
            "custom"        # Custom trained models
        ]
    
    def get_supported_backends(self) -> List[str]:
        """Get supported inference backends"""
        return ["vllm", "tensorrt_llm", "transformers"]
    
    async def invoke(self, input_data: str, task: str = "chat", **kwargs) -> Dict[str, Any]:
        """
        Unified invoke method for compatibility with ISA Model client interface
        """
        try:
            if task in ["chat", "generate", "complete"]:
                if task == "chat":
                    if isinstance(input_data, str):
                        messages = [{"role": "user", "content": input_data}]
                    elif isinstance(input_data, list):
                        messages = input_data
                    else:
                        messages = [{"role": "user", "content": str(input_data)}]
                    
                    result = await self.chat(messages, **kwargs)
                else:
                    result = await self.complete(input_data, **kwargs)
                
                # Convert to unified format
                if result.get("success"):
                    response_text = result.get("text", "") or result.get("content", "")
                    
                    return {
                        "success": True,
                        "result": {
                            "content": response_text,
                            "tool_calls": [],
                            "response_metadata": result.get("metadata", {})
                        },
                        "error": None,
                        "metadata": {
                            "model_used": result.get("model_id", self.model_name),
                            "provider": self.provider_name,
                            "task": task,
                            "service_type": "text",
                            "processing_time": result.get("metadata", {}).get("processing_time", 0),
                            "local_inference": True,
                            "gpu_accelerated": True
                        }
                    }
                else:
                    return {
                        "success": False,
                        "result": None,
                        "error": result.get("error", "Unknown error"),
                        "metadata": {
                            "model_used": self.model_name,
                            "provider": self.provider_name,
                            "task": task,
                            "service_type": "text",
                            "local_inference": True
                        }
                    }
            else:
                return {
                    "success": False,
                    "result": None,
                    "error": f"Unsupported task: {task}. Supported tasks: {self.get_supported_tasks()}",
                    "metadata": {
                        "model_used": self.model_name,
                        "provider": self.provider_name,
                        "task": task,
                        "service_type": "text"
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Local LLM invoke failed: {e}")
            return {
                "success": False,
                "result": None,
                "error": str(e),
                "metadata": {
                    "model_used": self.model_name,
                    "provider": self.provider_name,
                    "task": task,
                    "service_type": "text",
                    "local_inference": True
                }
            }


# Convenience function for quick setup
async def create_local_llm_service(
    models_to_deploy: List[str] = None,
    backend: str = "transformers",
    workspace_dir: str = "./local_llm_services"
) -> LocalLLMService:
    """
    Convenience function to create and initialize a local LLM service
    
    Args:
        models_to_deploy: List of model IDs to auto-deploy
        backend: Preferred inference backend
        workspace_dir: Working directory for services
        
    Returns:
        Initialized LocalLLMService instance
    """
    service = LocalLLMService(
        auto_deploy_models=models_to_deploy or [],
        preferred_backend=backend,
        workspace_dir=workspace_dir
    )
    
    await service.initialize()
    return service


# Example usage and testing
if __name__ == "__main__":
    async def test_local_llm_service():
        """Test the local LLM service"""
        
        # Create service
        service = await create_local_llm_service(
            models_to_deploy=["microsoft/DialoGPT-medium"],
            backend="transformers"
        )
        
        # Check health
        health = await service.health_check()
        print(f"Health: {health}")
        
        # Generate text
        if health.get("success"):
            result = await service.complete(
                prompt="Hello, how are you today?",
                max_tokens=50
            )
            print(f"Generation result: {result}")
            
            # Chat completion
            chat_result = await service.chat([
                {"role": "user", "content": "What is artificial intelligence?"}
            ])
            print(f"Chat result: {chat_result}")
    
    # Run test
    asyncio.run(test_local_llm_service())