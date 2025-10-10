"""
vLLM local inference service

High-performance local model serving using vLLM.
"""

import os
import json
import asyncio
import logging
import subprocess
import signal
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from pathlib import Path
from datetime import datetime
import httpx
import time

from .config import LocalGPUConfig, LocalServiceType, LocalBackend
from ...utils.gpu_utils import get_gpu_manager, GPUInfo

logger = logging.getLogger(__name__)


class VLLMService:
    """vLLM local inference service manager"""
    
    def __init__(self, config: LocalGPUConfig):
        """
        Initialize vLLM service.
        
        Args:
            config: Local GPU configuration for vLLM
        """
        if config.backend != LocalBackend.VLLM:
            raise ValueError("Config must use VLLM backend")
            
        self.config = config
        self.gpu_manager = get_gpu_manager()
        self.process: Optional[subprocess.Popen] = None
        self.service_url = f"http://{config.host}:{config.port}"
        self.is_running = False
        self.startup_time: Optional[datetime] = None
        
        # Service info
        self.service_info = {
            "service_name": config.service_name,
            "model_id": config.model_id,
            "backend": "vllm",
            "status": "stopped",
            "url": self.service_url
        }
    
    async def start(self) -> Dict[str, Any]:
        """
        Start vLLM inference server.
        
        Returns:
            Service startup result
        """
        if self.is_running:
            return {
                "success": False,
                "error": "Service already running",
                "service_info": self.service_info
            }
        
        try:
            logger.info(f"Starting vLLM service: {self.config.service_name}")
            
            # Check GPU availability
            gpu_check = await self._check_gpu_requirements()
            if not gpu_check["compatible"]:
                return {
                    "success": False,
                    "error": f"GPU requirements not met: {', '.join(gpu_check['warnings'])}",
                    "gpu_check": gpu_check
                }
            
            # Prepare vLLM command
            cmd = self._build_vllm_command()
            logger.info(f"vLLM command: {' '.join(cmd)}")
            
            # Start vLLM process
            self.startup_time = datetime.now()
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self._get_environment()
            )
            
            # Wait for service to be ready
            startup_result = await self._wait_for_startup()
            
            if startup_result["success"]:
                self.is_running = True
                self.service_info.update({
                    "status": "running",
                    "pid": self.process.pid,
                    "started_at": self.startup_time.isoformat(),
                    "model_info": await self._get_model_info()
                })
                
                logger.info(f"vLLM service started successfully: {self.service_url}")
                return {
                    "success": True,
                    "service_info": self.service_info,
                    "startup_time_seconds": startup_result["startup_time"],
                    "gpu_info": gpu_check["selected_gpu"]
                }
            else:
                await self.stop()
                return {
                    "success": False,
                    "error": startup_result["error"],
                    "logs": startup_result.get("logs", [])
                }
                
        except Exception as e:
            logger.error(f"Failed to start vLLM service: {e}")
            await self.stop()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop(self) -> Dict[str, Any]:
        """
        Stop vLLM inference server.
        
        Returns:
            Service shutdown result
        """
        if not self.is_running:
            return {
                "success": True,
                "message": "Service was not running"
            }
        
        try:
            logger.info(f"Stopping vLLM service: {self.config.service_name}")
            
            if self.process:
                # Graceful shutdown
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    logger.warning("Graceful shutdown timed out, force killing process")
                    self.process.kill()
                    self.process.wait(timeout=5)
                
                self.process = None
            
            self.is_running = False
            self.service_info.update({
                "status": "stopped",
                "pid": None,
                "stopped_at": datetime.now().isoformat()
            })
            
            logger.info(f"vLLM service stopped: {self.config.service_name}")
            return {
                "success": True,
                "service_info": self.service_info
            }
            
        except Exception as e:
            logger.error(f"Failed to stop vLLM service: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def restart(self) -> Dict[str, Any]:
        """Restart vLLM service"""
        stop_result = await self.stop()
        if not stop_result["success"]:
            return stop_result
        
        # Wait a moment before restart
        await asyncio.sleep(2)
        
        return await self.start()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        if not self.is_running:
            return {
                "healthy": False,
                "status": "stopped"
            }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.service_url}/health")
                
                if response.status_code == 200:
                    return {
                        "healthy": True,
                        "status": "running",
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "service_info": self.service_info
                    }
                else:
                    return {
                        "healthy": False,
                        "status": "unhealthy",
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            return {
                "healthy": False,
                "status": "error",
                "error": str(e)
            }
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using vLLM service"""
        if not self.is_running:
            return {
                "success": False,
                "error": "Service not running"
            }
        
        try:
            request_data = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 512),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "stream": kwargs.get("stream", False)
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.service_url}/generate",
                    json=request_data
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        **response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def chat_completions(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """OpenAI-compatible chat completions endpoint"""
        if not self.is_running:
            return {
                "success": False,
                "error": "Service not running"
            }
        
        try:
            request_data = {
                "model": self.config.served_model_name or self.config.model_id,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 512),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "stream": kwargs.get("stream", False)
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.service_url}/v1/chat/completions",
                    json=request_data,
                    headers={"Authorization": f"Bearer {self.config.api_key}"} if self.config.api_key else {}
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        **response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_vllm_command(self) -> List[str]:
        """Build vLLM server command"""
        cmd = ["python", "-m", "vllm.entrypoints.openai.api_server"]
        
        # Basic model configuration
        cmd.extend(["--model", self.config.model_id])
        cmd.extend(["--host", self.config.host])
        cmd.extend(["--port", str(self.config.port)])
        
        # Model configuration
        if self.config.served_model_name:
            cmd.extend(["--served-model-name", self.config.served_model_name])
        
        cmd.extend(["--max-model-len", str(self.config.max_model_len)])
        cmd.extend(["--max-num-seqs", str(self.config.max_num_seqs)])
        
        # GPU configuration
        if self.config.gpu_id is not None:
            cmd.extend(["--tensor-parallel-size", str(self.config.tensor_parallel_size)])
        
        cmd.extend(["--gpu-memory-utilization", str(self.config.gpu_memory_utilization)])
        cmd.extend(["--swap-space", str(self.config.swap_space)])
        
        # Performance settings
        if self.config.enable_chunked_prefill:
            cmd.append("--enable-chunked-prefill")
        
        if self.config.enable_prefix_caching:
            cmd.append("--enable-prefix-caching")
        
        # Precision and quantization
        if self.config.model_precision == "float16":
            cmd.extend(["--dtype", "float16"])
        elif self.config.model_precision == "bfloat16":
            cmd.extend(["--dtype", "bfloat16"])
        
        if self.config.quantization:
            cmd.extend(["--quantization", self.config.quantization])
            if self.config.quantization_param_path:
                cmd.extend(["--quantization-param-path", self.config.quantization_param_path])
        
        # Trust remote code
        if self.config.trust_remote_code:
            cmd.append("--trust-remote-code")
        
        # Model revisions
        if self.config.revision:
            cmd.extend(["--revision", self.config.revision])
        if self.config.tokenizer_revision:
            cmd.extend(["--tokenizer-revision", self.config.tokenizer_revision])
        
        # Additional vLLM arguments
        for key, value in self.config.vllm_args.items():
            if isinstance(value, bool):
                if value:
                    cmd.append(f"--{key}")
            else:
                cmd.extend([f"--{key}", str(value)])
        
        return cmd
    
    def _get_environment(self) -> Dict[str, str]:
        """Get environment variables for vLLM"""
        env = os.environ.copy()
        
        # CUDA configuration
        if self.config.gpu_id is not None:
            env["CUDA_VISIBLE_DEVICES"] = str(self.config.gpu_id)
        
        # Cache directories
        if self.config.model_cache_dir:
            env["TRANSFORMERS_CACHE"] = self.config.model_cache_dir
            env["HF_HOME"] = self.config.model_cache_dir
        
        if self.config.download_dir:
            env["HF_HUB_CACHE"] = self.config.download_dir
        
        # Performance optimizations
        env["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
        env["OMP_NUM_THREADS"] = "8"
        
        return env
    
    async def _check_gpu_requirements(self) -> Dict[str, Any]:
        """Check GPU requirements for the model"""
        self.gpu_manager.refresh()
        
        if not self.gpu_manager.cuda_available:
            return {
                "compatible": False,
                "warnings": ["CUDA not available"],
                "selected_gpu": None
            }
        
        # Estimate memory requirements
        estimated_memory = self.gpu_manager.estimate_model_memory(
            self.config.model_id, 
            self.config.model_precision
        )
        
        # Find suitable GPU
        if self.config.gpu_id is not None:
            selected_gpu = self.gpu_manager.get_gpu_info(self.config.gpu_id)
            if not selected_gpu:
                return {
                    "compatible": False,
                    "warnings": [f"Specified GPU {self.config.gpu_id} not found"],
                    "selected_gpu": None
                }
        else:
            selected_gpu = self.gpu_manager.get_best_gpu(estimated_memory)
            if selected_gpu:
                self.config.gpu_id = selected_gpu.gpu_id
        
        if not selected_gpu:
            return {
                "compatible": False,
                "warnings": [
                    f"No suitable GPU found. Required: {estimated_memory}MB, "
                    f"Available: {max(gpu.memory_free for gpu in self.gpu_manager.gpus) if self.gpu_manager.gpus else 0}MB"
                ],
                "selected_gpu": None
            }
        
        warnings = []
        
        # Check memory requirements
        required_memory = int(estimated_memory * self.config.gpu_memory_utilization)
        if selected_gpu.memory_free < required_memory:
            warnings.append(f"GPU memory may be insufficient: {selected_gpu.memory_free}MB available, {required_memory}MB required")
        
        # Check utilization
        if selected_gpu.utilization > 80:
            warnings.append(f"GPU utilization is high: {selected_gpu.utilization}%")
        
        return {
            "compatible": True,
            "warnings": warnings,
            "selected_gpu": {
                "gpu_id": selected_gpu.gpu_id,
                "name": selected_gpu.name,
                "memory_total": selected_gpu.memory_total,
                "memory_free": selected_gpu.memory_free,
                "utilization": selected_gpu.utilization,
                "estimated_memory_required": estimated_memory
            }
        }
    
    async def _wait_for_startup(self, timeout: int = 300) -> Dict[str, Any]:
        """Wait for vLLM service to start"""
        start_time = time.time()
        logs = []
        
        while time.time() - start_time < timeout:
            # Check if process is still running
            if self.process and self.process.poll() is not None:
                # Process died
                stdout, stderr = self.process.communicate()
                return {
                    "success": False,
                    "error": "vLLM process died during startup",
                    "logs": logs + [stdout, stderr]
                }
            
            # Try to connect to service
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(f"{self.service_url}/health")
                    if response.status_code == 200:
                        startup_time = time.time() - start_time
                        return {
                            "success": True,
                            "startup_time": startup_time
                        }
            except:
                pass
            
            # Collect logs
            if self.process:
                try:
                    # Non-blocking read of logs
                    import select
                    if hasattr(select, 'select'):
                        ready, _, _ = select.select([self.process.stdout], [], [], 0.1)
                        if ready:
                            line = self.process.stdout.readline()
                            if line:
                                logs.append(line.strip())
                                logger.debug(f"vLLM: {line.strip()}")
                except:
                    pass
            
            await asyncio.sleep(2)
        
        return {
            "success": False,
            "error": f"Startup timeout after {timeout} seconds",
            "logs": logs
        }
    
    async def _get_model_info(self) -> Optional[Dict[str, Any]]:
        """Get model information from vLLM service"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.service_url}/v1/models")
                if response.status_code == 200:
                    return response.json()
        except:
            pass
        return None
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get current service information"""
        return {
            **self.service_info,
            "config": self.config.to_dict(),
            "process_id": self.process.pid if self.process else None,
            "is_running": self.is_running,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None
        }