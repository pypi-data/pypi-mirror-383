"""
GPU Gateway for PaaS/SaaS Platform
本地GPU资源的统一网关和管理服务
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
from aiohttp import web
import time
import json
from pathlib import Path

from .provider import LocalGPUProvider
from .config import LocalGPUConfig, LocalServiceType, LocalBackend
from .health_checker import LocalHealthChecker
from ..core.base_deployment import DeploymentResult


logger = logging.getLogger(__name__)


class GPUPoolStatus(Enum):
    """GPU资源池状态"""
    AVAILABLE = "available"
    BUSY = "busy" 
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class GPUNode:
    """GPU节点信息"""
    node_id: str
    hostname: str
    gpu_count: int
    gpu_memory_total: int  # MB
    gpu_memory_free: int   # MB
    status: GPUPoolStatus = GPUPoolStatus.AVAILABLE
    current_models: List[str] = field(default_factory=list)
    max_concurrent_requests: int = 10
    current_requests: int = 0
    last_heartbeat: float = field(default_factory=time.time)


@dataclass 
class TenantConfig:
    """租户配置"""
    tenant_id: str
    gpu_quota: int  # 分配的GPU数量
    memory_quota: int  # 分配的GPU内存MB
    priority: int = 1  # 优先级 1-10
    allowed_models: List[str] = field(default_factory=list)
    rate_limit: int = 100  # 每分钟请求数


class GPUGateway:
    """
    GPU网关服务 - PaaS平台的本地GPU资源管理
    
    功能:
    1. GPU资源池管理
    2. 多租户资源隔离
    3. 负载均衡和路由
    4. 服务发现和健康检查
    5. 与云端API的通信
    """
    
    def __init__(self, 
                 gateway_port: int = 8888,
                 cloud_api_url: Optional[str] = None,
                 workspace_dir: str = "./gpu_gateway"):
        self.gateway_port = gateway_port
        self.cloud_api_url = cloud_api_url
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        
        # GPU资源管理
        self.gpu_nodes: Dict[str, GPUNode] = {}
        self.gpu_providers: Dict[str, LocalGPUProvider] = {}
        self.health_checkers: Dict[str, LocalHealthChecker] = {}
        
        # 租户管理
        self.tenants: Dict[str, TenantConfig] = {}
        
        # 请求路由和负载均衡
        self.request_queue = asyncio.Queue()
        self.model_routing: Dict[str, List[str]] = {}  # model_id -> [node_ids]
        
        # 监控数据
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_latency": 0.0,
            "gpu_utilization": {}
        }
        
        # 启动标志
        self._running = False
        self._background_tasks = []
    
    async def start(self):
        """启动GPU网关服务"""
        logger.info("🚀 Starting GPU Gateway...")
        
        # 发现本地GPU节点
        await self._discover_gpu_nodes()
        
        # 启动背景任务
        self._running = True
        self._background_tasks = [
            asyncio.create_task(self._heartbeat_monitor()),
            asyncio.create_task(self._resource_balancer()),
            asyncio.create_task(self._metrics_collector()),
            asyncio.create_task(self._cloud_sync()) if self.cloud_api_url else None
        ]
        self._background_tasks = [t for t in self._background_tasks if t]
        
        # 启动HTTP服务
        app = self._create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.gateway_port)
        await site.start()
        
        logger.info(f"✅ GPU Gateway started on port {self.gateway_port}")
        return runner
    
    async def stop(self):
        """停止网关服务"""
        self._running = False
        
        # 停止背景任务
        for task in self._background_tasks:
            task.cancel()
        
        # 停止所有GPU服务
        for provider in self.gpu_providers.values():
            await provider.cleanup()
        
        logger.info("🛑 GPU Gateway stopped")
    
    async def _discover_gpu_nodes(self):
        """发现本地GPU节点"""
        logger.info("🔍 Discovering local GPU nodes...")
        
        try:
            # 检测本地GPU
            from ...utils.gpu_utils import GPUManager
            gpu_manager = GPUManager()
            
            if gpu_manager.is_cuda_available():
                gpu_info = gpu_manager.get_gpu_info()
                
                for i, gpu in enumerate(gpu_info):
                    node_id = f"local-gpu-{i}"
                    node = GPUNode(
                        node_id=node_id,
                        hostname="localhost",
                        gpu_count=1,
                        gpu_memory_total=gpu.get('memory_total_mb', 0),
                        gpu_memory_free=gpu.get('memory_free_mb', 0)
                    )
                    
                    self.gpu_nodes[node_id] = node
                    
                    # 创建GPU Provider
                    provider = LocalGPUProvider(
                        workspace_dir=self.workspace_dir / node_id,
                        gpu_id=i
                    )
                    self.gpu_providers[node_id] = provider
                    
                    # 创建健康检查器
                    health_checker = LocalHealthChecker()
                    self.health_checkers[node_id] = health_checker
                    
                    logger.info(f"✅ Discovered GPU node: {node_id}")
            
            else:
                logger.warning("⚠️ No CUDA GPUs detected")
                
        except Exception as e:
            logger.error(f"❌ GPU discovery failed: {e}")
    
    def register_tenant(self, tenant_config: TenantConfig):
        """注册租户"""
        self.tenants[tenant_config.tenant_id] = tenant_config
        logger.info(f"👤 Registered tenant: {tenant_config.tenant_id}")
    
    async def deploy_model(self, 
                          tenant_id: str,
                          model_id: str, 
                          config: LocalGPUConfig,
                          preferred_node: Optional[str] = None) -> DeploymentResult:
        """为租户部署模型"""
        
        # 验证租户权限
        if tenant_id not in self.tenants:
            return DeploymentResult(
                success=False,
                error=f"Unknown tenant: {tenant_id}"
            )
        
        tenant = self.tenants[tenant_id]
        
        # 检查模型权限
        if tenant.allowed_models and model_id not in tenant.allowed_models:
            return DeploymentResult(
                success=False,
                error=f"Model {model_id} not allowed for tenant {tenant_id}"
            )
        
        # 选择GPU节点
        node_id = preferred_node or await self._select_best_node(config, tenant)
        if not node_id:
            return DeploymentResult(
                success=False,
                error="No available GPU nodes"
            )
        
        # 部署模型
        try:
            provider = self.gpu_providers[node_id]
            result = await provider.deploy_model(config)
            
            if result.success:
                # 更新节点状态
                node = self.gpu_nodes[node_id]
                node.current_models.append(model_id)
                
                # 更新路由表
                if model_id not in self.model_routing:
                    self.model_routing[model_id] = []
                self.model_routing[model_id].append(node_id)
                
                logger.info(f"✅ Deployed {model_id} for tenant {tenant_id} on {node_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return DeploymentResult(
                success=False,
                error=str(e)
            )
    
    async def inference_request(self,
                               tenant_id: str,
                               model_id: str,
                               request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理推理请求"""
        
        # 验证租户
        if tenant_id not in self.tenants:
            return {"error": f"Unknown tenant: {tenant_id}"}
        
        # 检查rate limiting
        tenant = self.tenants[tenant_id]
        # TODO: 实现rate limiting逻辑
        
        # 选择服务节点
        node_id = await self._route_request(model_id, tenant)
        if not node_id:
            return {"error": "No available nodes for model"}
        
        # 执行推理
        try:
            start_time = time.time()
            provider = self.gpu_providers[node_id]
            
            # 根据请求类型调用不同方法
            if "messages" in request_data:
                # Chat completion
                result = await provider.chat_completion(
                    model_id=model_id,
                    **request_data
                )
            else:
                # Text completion
                result = await provider.text_completion(
                    model_id=model_id,
                    **request_data
                )
            
            # 更新指标
            latency = time.time() - start_time
            await self._update_metrics(tenant_id, latency, True)
            
            # 更新节点负载
            node = self.gpu_nodes[node_id]
            node.current_requests = max(0, node.current_requests - 1)
            
            return result
            
        except Exception as e:
            await self._update_metrics(tenant_id, 0, False)
            logger.error(f"❌ Inference failed: {e}")
            return {"error": str(e)}
    
    async def _select_best_node(self, 
                               config: LocalGPUConfig,
                               tenant: TenantConfig) -> Optional[str]:
        """选择最佳GPU节点"""
        available_nodes = []
        
        for node_id, node in self.gpu_nodes.items():
            if (node.status == GPUPoolStatus.AVAILABLE and 
                node.gpu_memory_free > 2000):  # 至少2GB空闲
                
                # 计算节点分数 (内存越多，当前负载越少，分数越高)
                score = (
                    node.gpu_memory_free * 0.6 +  # 内存权重
                    (node.max_concurrent_requests - node.current_requests) * 0.3 +  # 负载权重
                    tenant.priority * 0.1  # 租户优先级权重
                )
                
                available_nodes.append((node_id, score))
        
        if available_nodes:
            # 选择分数最高的节点
            available_nodes.sort(key=lambda x: x[1], reverse=True)
            return available_nodes[0][0]
        
        return None
    
    async def _route_request(self, model_id: str, tenant: TenantConfig) -> Optional[str]:
        """路由推理请求到合适的节点"""
        if model_id not in self.model_routing:
            return None
        
        # 从部署了该模型的节点中选择负载最低的
        candidate_nodes = self.model_routing[model_id]
        best_node = None
        min_load = float('inf')
        
        for node_id in candidate_nodes:
            node = self.gpu_nodes[node_id]
            if (node.status == GPUPoolStatus.AVAILABLE and 
                node.current_requests < node.max_concurrent_requests):
                
                # 考虑租户优先级的负载计算
                load = node.current_requests / node.max_concurrent_requests
                adjusted_load = load / max(tenant.priority, 1)
                
                if adjusted_load < min_load:
                    min_load = adjusted_load
                    best_node = node_id
        
        if best_node:
            # 增加节点负载计数
            self.gpu_nodes[best_node].current_requests += 1
        
        return best_node
    
    async def _heartbeat_monitor(self):
        """监控GPU节点心跳"""
        while self._running:
            try:
                current_time = time.time()
                
                for node_id, node in self.gpu_nodes.items():
                    # 检查心跳超时
                    if current_time - node.last_heartbeat > 30:  # 30秒超时
                        logger.warning(f"⚠️ Node {node_id} heartbeat timeout")
                        node.status = GPUPoolStatus.ERROR
                    
                    # 更新GPU状态
                    if node_id in self.health_checkers:
                        health = await self.health_checkers[node_id].check_service_health("gpu-status")
                        if health.get("success"):
                            node.status = GPUPoolStatus.AVAILABLE
                            node.gpu_memory_free = health.get("gpu_memory_free", 0)
                            node.last_heartbeat = current_time
                
                await asyncio.sleep(10)  # 每10秒检查一次
                
            except Exception as e:
                logger.error(f"❌ Heartbeat monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _resource_balancer(self):
        """资源均衡器"""
        while self._running:
            try:
                # 检查资源使用情况
                for node_id, node in self.gpu_nodes.items():
                    utilization = node.current_requests / node.max_concurrent_requests
                    
                    # 如果节点过载，考虑迁移部分服务
                    if utilization > 0.9:
                        logger.info(f"🔄 Node {node_id} is overloaded ({utilization:.1%})")
                        # TODO: 实现负载迁移逻辑
                
                await asyncio.sleep(30)  # 每30秒平衡一次
                
            except Exception as e:
                logger.error(f"❌ Resource balancer error: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_collector(self):
        """指标收集器"""
        while self._running:
            try:
                # 收集GPU利用率
                for node_id, node in self.gpu_nodes.items():
                    utilization = node.current_requests / node.max_concurrent_requests
                    self.metrics["gpu_utilization"][node_id] = utilization
                
                await asyncio.sleep(5)  # 每5秒收集一次
                
            except Exception as e:
                logger.error(f"❌ Metrics collector error: {e}")
                await asyncio.sleep(10)
    
    async def _cloud_sync(self):
        """与云端API同步"""
        if not self.cloud_api_url:
            return
        
        while self._running:
            try:
                # 向云端报告GPU状态
                status_data = {
                    "gateway_id": "local-gpu-gateway",
                    "nodes": [
                        {
                            "node_id": node.node_id,
                            "status": node.status.value,
                            "gpu_count": node.gpu_count,
                            "memory_free": node.gpu_memory_free,
                            "current_models": node.current_models,
                            "current_load": node.current_requests
                        }
                        for node in self.gpu_nodes.values()
                    ],
                    "metrics": self.metrics
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.cloud_api_url}/api/gpu-gateway/status",
                        json=status_data
                    ) as response:
                        if response.status == 200:
                            logger.debug("✅ Status synced to cloud")
                        else:
                            logger.warning(f"⚠️ Cloud sync failed: {response.status}")
                
                await asyncio.sleep(60)  # 每分钟同步一次
                
            except Exception as e:
                logger.error(f"❌ Cloud sync error: {e}")
                await asyncio.sleep(30)
    
    async def _update_metrics(self, tenant_id: str, latency: float, success: bool):
        """更新指标"""
        self.metrics["total_requests"] += 1
        
        if success:
            self.metrics["successful_requests"] += 1
            # 更新平均延迟
            current_avg = self.metrics["average_latency"]
            total_successful = self.metrics["successful_requests"]
            self.metrics["average_latency"] = (
                (current_avg * (total_successful - 1) + latency) / total_successful
            )
        else:
            self.metrics["failed_requests"] += 1
    
    def _create_app(self) -> web.Application:
        """创建HTTP API应用"""
        app = web.Application()
        
        # API路由
        app.router.add_post('/deploy', self._handle_deploy)
        app.router.add_post('/inference', self._handle_inference)
        app.router.add_get('/status', self._handle_status)
        app.router.add_get('/metrics', self._handle_metrics)
        app.router.add_post('/tenants', self._handle_register_tenant)
        
        return app
    
    async def _handle_deploy(self, request: web.Request) -> web.Response:
        """处理部署请求"""
        try:
            data = await request.json()
            
            config = LocalGPUConfig(
                service_name=data["service_name"],
                service_type=LocalServiceType(data["service_type"]),
                model_id=data["model_id"],
                backend=LocalBackend(data.get("backend", "transformers"))
            )
            
            result = await self.deploy_model(
                tenant_id=data["tenant_id"],
                model_id=data["model_id"],
                config=config,
                preferred_node=data.get("preferred_node")
            )
            
            return web.json_response({
                "success": result.success,
                "error": result.error,
                "service_name": result.service_name,
                "service_info": result.service_info
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=400)
    
    async def _handle_inference(self, request: web.Request) -> web.Response:
        """处理推理请求"""
        try:
            data = await request.json()
            
            result = await self.inference_request(
                tenant_id=data["tenant_id"],
                model_id=data["model_id"],
                request_data=data["request"]
            )
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({
                "error": str(e)
            }, status=400)
    
    async def _handle_status(self, request: web.Request) -> web.Response:
        """获取网关状态"""
        status = {
            "gateway_status": "running" if self._running else "stopped",
            "total_nodes": len(self.gpu_nodes),
            "healthy_nodes": sum(
                1 for node in self.gpu_nodes.values() 
                if node.status == GPUPoolStatus.AVAILABLE
            ),
            "total_tenants": len(self.tenants),
            "deployed_models": len(self.model_routing),
            "nodes": [
                {
                    "node_id": node.node_id,
                    "status": node.status.value,
                    "gpu_memory_free": node.gpu_memory_free,
                    "current_requests": node.current_requests,
                    "models": node.current_models
                }
                for node in self.gpu_nodes.values()
            ]
        }
        
        return web.json_response(status)
    
    async def _handle_metrics(self, request: web.Request) -> web.Response:
        """获取指标数据"""
        return web.json_response(self.metrics)
    
    async def _handle_register_tenant(self, request: web.Request) -> web.Response:
        """注册租户"""
        try:
            data = await request.json()
            
            tenant_config = TenantConfig(
                tenant_id=data["tenant_id"],
                gpu_quota=data.get("gpu_quota", 1),
                memory_quota=data.get("memory_quota", 8192),
                priority=data.get("priority", 1),
                allowed_models=data.get("allowed_models", []),
                rate_limit=data.get("rate_limit", 100)
            )
            
            self.register_tenant(tenant_config)
            
            return web.json_response({
                "success": True,
                "tenant_id": tenant_config.tenant_id
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=400)


# 便捷函数
async def create_gpu_gateway(gateway_port: int = 8888,
                           cloud_api_url: Optional[str] = None,
                           workspace_dir: str = "./gpu_gateway") -> GPUGateway:
    """创建并启动GPU网关"""
    gateway = GPUGateway(
        gateway_port=gateway_port,
        cloud_api_url=cloud_api_url,
        workspace_dir=workspace_dir
    )
    
    await gateway.start()
    return gateway