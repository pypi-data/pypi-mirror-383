"""
Local GPU deployment configuration

Configuration classes for local GPU model deployment.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from pathlib import Path


class LocalServiceType(Enum):
    """Local service types"""
    LLM = "llm"
    VISION = "vision" 
    AUDIO = "audio"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"


class LocalBackend(Enum):
    """Local inference backends"""
    VLLM = "vllm"
    TENSORRT_LLM = "tensorrt_llm"
    TRANSFORMERS = "transformers"
    ONNX = "onnxruntime"
    OPENVINO = "openvino"


@dataclass
class LocalGPUConfig:
    """Configuration for local GPU model deployment"""
    
    # Service identification
    service_name: str
    service_type: LocalServiceType
    model_id: str
    backend: LocalBackend = LocalBackend.TRANSFORMERS
    
    # GPU configuration
    gpu_id: Optional[int] = None  # None = auto-select best GPU
    gpu_memory_fraction: float = 0.9  # Fraction of GPU memory to use
    enable_gpu: bool = True
    
    # Model configuration
    model_precision: str = "float16"  # float32, float16, int8, int4
    max_model_len: int = 2048
    max_batch_size: int = 8
    
    # Performance settings
    enable_chunked_prefill: bool = True
    max_num_seqs: int = 256
    tensor_parallel_size: int = 1
    pipeline_parallel_size: int = 1
    
    # Memory optimization
    enable_prefix_caching: bool = True
    gpu_memory_utilization: float = 0.9
    swap_space: int = 4  # GB
    cpu_offload: bool = False
    
    # Quantization settings
    quantization: Optional[str] = None  # awq, gptq, squeezellm, etc.
    quantization_param_path: Optional[str] = None
    
    # Serving configuration
    host: str = "127.0.0.1"
    port: int = 8000
    api_key: Optional[str] = None
    served_model_name: Optional[str] = None
    
    # Advanced settings
    trust_remote_code: bool = False
    revision: Optional[str] = None
    tokenizer_revision: Optional[str] = None
    
    # Specific backend configurations
    vllm_args: Dict[str, Any] = field(default_factory=dict)
    tensorrt_args: Dict[str, Any] = field(default_factory=dict)
    transformers_args: Dict[str, Any] = field(default_factory=dict)
    
    # Environment and paths
    model_cache_dir: Optional[str] = None
    download_dir: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "service_name": self.service_name,
            "service_type": self.service_type.value,
            "model_id": self.model_id,
            "backend": self.backend.value,
            "gpu_id": self.gpu_id,
            "gpu_memory_fraction": self.gpu_memory_fraction,
            "enable_gpu": self.enable_gpu,
            "model_precision": self.model_precision,
            "max_model_len": self.max_model_len,
            "max_batch_size": self.max_batch_size,
            "enable_chunked_prefill": self.enable_chunked_prefill,
            "max_num_seqs": self.max_num_seqs,
            "tensor_parallel_size": self.tensor_parallel_size,
            "pipeline_parallel_size": self.pipeline_parallel_size,
            "enable_prefix_caching": self.enable_prefix_caching,
            "gpu_memory_utilization": self.gpu_memory_utilization,
            "swap_space": self.swap_space,
            "cpu_offload": self.cpu_offload,
            "quantization": self.quantization,
            "quantization_param_path": self.quantization_param_path,
            "host": self.host,
            "port": self.port,
            "api_key": self.api_key,
            "served_model_name": self.served_model_name,
            "trust_remote_code": self.trust_remote_code,
            "revision": self.revision,
            "tokenizer_revision": self.tokenizer_revision,
            "vllm_args": self.vllm_args,
            "tensorrt_args": self.tensorrt_args,
            "transformers_args": self.transformers_args,
            "model_cache_dir": self.model_cache_dir,
            "download_dir": self.download_dir
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LocalGPUConfig":
        """Create from dictionary"""
        return cls(
            service_name=data["service_name"],
            service_type=LocalServiceType(data["service_type"]),
            model_id=data["model_id"],
            backend=LocalBackend(data.get("backend", "transformers")),
            gpu_id=data.get("gpu_id"),
            gpu_memory_fraction=data.get("gpu_memory_fraction", 0.9),
            enable_gpu=data.get("enable_gpu", True),
            model_precision=data.get("model_precision", "float16"),
            max_model_len=data.get("max_model_len", 2048),
            max_batch_size=data.get("max_batch_size", 8),
            enable_chunked_prefill=data.get("enable_chunked_prefill", True),
            max_num_seqs=data.get("max_num_seqs", 256),
            tensor_parallel_size=data.get("tensor_parallel_size", 1),
            pipeline_parallel_size=data.get("pipeline_parallel_size", 1),
            enable_prefix_caching=data.get("enable_prefix_caching", True),
            gpu_memory_utilization=data.get("gpu_memory_utilization", 0.9),
            swap_space=data.get("swap_space", 4),
            cpu_offload=data.get("cpu_offload", False),
            quantization=data.get("quantization"),
            quantization_param_path=data.get("quantization_param_path"),
            host=data.get("host", "127.0.0.1"),
            port=data.get("port", 8000),
            api_key=data.get("api_key"),
            served_model_name=data.get("served_model_name"),
            trust_remote_code=data.get("trust_remote_code", False),
            revision=data.get("revision"),
            tokenizer_revision=data.get("tokenizer_revision"),
            vllm_args=data.get("vllm_args", {}),
            tensorrt_args=data.get("tensorrt_args", {}),
            transformers_args=data.get("transformers_args", {}),
            model_cache_dir=data.get("model_cache_dir"),
            download_dir=data.get("download_dir")
        )


# Predefined configurations for common use cases
def create_vllm_config(service_name: str, model_id: str,
                       max_model_len: int = 2048,
                       tensor_parallel_size: int = 1) -> LocalGPUConfig:
    """Create optimized vLLM configuration"""
    return LocalGPUConfig(
        service_name=service_name,
        service_type=LocalServiceType.LLM,
        model_id=model_id,
        backend=LocalBackend.VLLM,
        max_model_len=max_model_len,
        tensor_parallel_size=tensor_parallel_size,
        enable_chunked_prefill=True,
        enable_prefix_caching=True,
        gpu_memory_utilization=0.9,
        model_precision="float16"
    )


def create_tensorrt_config(service_name: str, model_id: str,
                          max_batch_size: int = 8,
                          precision: str = "float16") -> LocalGPUConfig:
    """Create TensorRT-LLM configuration"""
    return LocalGPUConfig(
        service_name=service_name,
        service_type=LocalServiceType.LLM,
        model_id=model_id,
        backend=LocalBackend.TENSORRT_LLM,
        max_batch_size=max_batch_size,
        model_precision=precision,
        tensor_parallel_size=1,
        tensorrt_args={
            "enable_kv_cache_reuse": True,
            "remove_input_padding": True,
            "use_gpt_attention_plugin": True
        }
    )


def create_transformers_config(service_name: str, model_id: str,
                             precision: str = "float16",
                             quantization: Optional[str] = None) -> LocalGPUConfig:
    """Create HuggingFace Transformers configuration"""
    return LocalGPUConfig(
        service_name=service_name,
        service_type=LocalServiceType.LLM,
        model_id=model_id,
        backend=LocalBackend.TRANSFORMERS,
        model_precision=precision,
        quantization=quantization,
        max_batch_size=4,  # Lower for memory efficiency
        transformers_args={
            "device_map": "auto",
            "torch_dtype": "auto",
            "low_cpu_mem_usage": True
        }
    )


def create_vision_config(service_name: str, model_id: str,
                        backend: LocalBackend = LocalBackend.TRANSFORMERS) -> LocalGPUConfig:
    """Create vision model configuration"""
    return LocalGPUConfig(
        service_name=service_name,
        service_type=LocalServiceType.VISION,
        model_id=model_id,
        backend=backend,
        max_batch_size=16,
        model_precision="float16",
        gpu_memory_utilization=0.8  # Lower for vision models
    )


def create_embedding_config(service_name: str, model_id: str,
                           max_batch_size: int = 32) -> LocalGPUConfig:
    """Create embedding model configuration"""
    return LocalGPUConfig(
        service_name=service_name,
        service_type=LocalServiceType.EMBEDDING,
        model_id=model_id,
        backend=LocalBackend.TRANSFORMERS,
        max_batch_size=max_batch_size,
        model_precision="float16",
        gpu_memory_utilization=0.7,  # Lower memory usage for embeddings
        cpu_offload=False
    )