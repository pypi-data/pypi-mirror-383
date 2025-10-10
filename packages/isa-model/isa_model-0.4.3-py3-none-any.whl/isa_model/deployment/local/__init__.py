"""
Local GPU deployment module

This module provides local GPU model deployment capabilities including:
- Direct GPU resource management
- vLLM integration for high-performance inference
- TensorRT-LLM native deployment (non-containerized)
- HuggingFace Transformers direct deployment
- Local service monitoring and health checks
"""

from .provider import LocalGPUProvider
from .config import (
    LocalGPUConfig, LocalServiceType, LocalBackend,
    create_vllm_config, create_tensorrt_config, create_transformers_config,
    create_vision_config, create_embedding_config
)
from .health_checker import LocalHealthChecker

__all__ = [
    'LocalGPUProvider',
    'LocalGPUConfig', 
    'LocalServiceType',
    'LocalBackend',
    'LocalHealthChecker',
    'create_vllm_config',
    'create_tensorrt_config', 
    'create_transformers_config',
    'create_vision_config',
    'create_embedding_config'
]