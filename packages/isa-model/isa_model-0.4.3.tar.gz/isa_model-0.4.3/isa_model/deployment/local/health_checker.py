"""
Local service health monitoring and management

Provides health checking, monitoring, and management for local GPU services.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ...utils.gpu_utils import get_gpu_manager

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    UNHEALTHY = "unhealthy"
    STOPPING = "stopping"


@dataclass
class HealthMetrics:
    """Health metrics for a service"""
    service_name: str
    status: ServiceStatus
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_count: int = 0
    consecutive_failures: int = 0
    uptime_seconds: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    gpu_utilization: Optional[float] = None
    request_count: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LocalHealthChecker:
    """Health checker for local GPU services"""
    
    def __init__(self, check_interval: int = 30, failure_threshold: int = 3):
        """
        Initialize health checker.
        
        Args:
            check_interval: Health check interval in seconds
            failure_threshold: Number of consecutive failures before marking unhealthy
        """
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold
        self.gpu_manager = get_gpu_manager()
        
        # Service tracking
        self.services: Dict[str, Any] = {}  # service_name -> service instance
        self.metrics: Dict[str, HealthMetrics] = {}  # service_name -> metrics
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}  # service_name -> task
        
        # Global monitoring
        self.monitoring_enabled = False
        self.global_monitor_task: Optional[asyncio.Task] = None
        
        logger.info("Local health checker initialized")
    
    def register_service(self, service_name: str, service_instance: Any) -> bool:
        """
        Register a service for health monitoring.
        
        Args:
            service_name: Unique service name
            service_instance: Service instance with health_check() method
            
        Returns:
            Registration success
        """
        try:
            if not hasattr(service_instance, 'health_check'):
                logger.error(f"Service {service_name} does not have health_check method")
                return False
            
            self.services[service_name] = service_instance
            self.metrics[service_name] = HealthMetrics(
                service_name=service_name,
                status=ServiceStatus.STOPPED,
                last_check=datetime.now()
            )
            
            logger.info(f"Service registered for health monitoring: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service_name}: {e}")
            return False
    
    def unregister_service(self, service_name: str) -> bool:
        """
        Unregister a service from health monitoring.
        
        Args:
            service_name: Service name to unregister
            
        Returns:
            Unregistration success
        """
        try:
            # Stop monitoring task
            if service_name in self.monitoring_tasks:
                self.monitoring_tasks[service_name].cancel()
                del self.monitoring_tasks[service_name]
            
            # Remove from tracking
            if service_name in self.services:
                del self.services[service_name]
            if service_name in self.metrics:
                del self.metrics[service_name]
            
            logger.info(f"Service unregistered from health monitoring: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service {service_name}: {e}")
            return False
    
    async def start_monitoring(self, service_name: Optional[str] = None) -> bool:
        """
        Start health monitoring for a specific service or all services.
        
        Args:
            service_name: Service to monitor, or None for all services
            
        Returns:
            Start success
        """
        try:
            if service_name:
                # Start monitoring for specific service
                if service_name not in self.services:
                    logger.error(f"Service {service_name} not registered")
                    return False
                
                if service_name not in self.monitoring_tasks:
                    task = asyncio.create_task(self._monitor_service(service_name))
                    self.monitoring_tasks[service_name] = task
                    logger.info(f"Started monitoring service: {service_name}")
                
            else:
                # Start monitoring for all services
                for svc_name in self.services:
                    if svc_name not in self.monitoring_tasks:
                        task = asyncio.create_task(self._monitor_service(svc_name))
                        self.monitoring_tasks[svc_name] = task
                
                # Start global monitoring
                if not self.monitoring_enabled:
                    self.monitoring_enabled = True
                    self.global_monitor_task = asyncio.create_task(self._global_monitor())
                    logger.info("Started global health monitoring")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    async def stop_monitoring(self, service_name: Optional[str] = None) -> bool:
        """
        Stop health monitoring for a specific service or all services.
        
        Args:
            service_name: Service to stop monitoring, or None for all services
            
        Returns:
            Stop success
        """
        try:
            if service_name:
                # Stop monitoring for specific service
                if service_name in self.monitoring_tasks:
                    self.monitoring_tasks[service_name].cancel()
                    del self.monitoring_tasks[service_name]
                    logger.info(f"Stopped monitoring service: {service_name}")
                
            else:
                # Stop all monitoring
                for task in self.monitoring_tasks.values():
                    task.cancel()
                self.monitoring_tasks.clear()
                
                # Stop global monitoring
                self.monitoring_enabled = False
                if self.global_monitor_task:
                    self.global_monitor_task.cancel()
                    self.global_monitor_task = None
                
                logger.info("Stopped all health monitoring")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Perform immediate health check for a service.
        
        Args:
            service_name: Service to check
            
        Returns:
            Health check result
        """
        if service_name not in self.services:
            return {
                "healthy": False,
                "error": f"Service {service_name} not registered"
            }
        
        try:
            start_time = time.time()
            service = self.services[service_name]
            
            # Perform health check
            health_result = await service.health_check()
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Update metrics
            metrics = self.metrics[service_name]
            metrics.last_check = datetime.now()
            metrics.response_time_ms = response_time
            
            if health_result.get("healthy", False):
                metrics.status = ServiceStatus.RUNNING
                metrics.consecutive_failures = 0
                
                # Update additional metrics if available
                if "memory_usage_mb" in health_result:
                    metrics.memory_usage_mb = health_result["memory_usage_mb"]
                if "gpu_utilization" in health_result:
                    metrics.gpu_utilization = health_result["gpu_utilization"]
                if "uptime_seconds" in health_result:
                    metrics.uptime_seconds = health_result["uptime_seconds"]
                if "request_count" in health_result:
                    metrics.request_count = health_result["request_count"]
                
            else:
                metrics.consecutive_failures += 1
                metrics.error_count += 1
                metrics.last_error = health_result.get("error", "Unknown error")
                
                if metrics.consecutive_failures >= self.failure_threshold:
                    metrics.status = ServiceStatus.UNHEALTHY
                else:
                    metrics.status = ServiceStatus.ERROR
            
            return {
                **health_result,
                "response_time_ms": response_time,
                "consecutive_failures": metrics.consecutive_failures,
                "service_name": service_name
            }
            
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            
            # Update metrics on exception
            metrics = self.metrics[service_name]
            metrics.last_check = datetime.now()
            metrics.consecutive_failures += 1
            metrics.error_count += 1
            metrics.last_error = str(e)
            metrics.status = ServiceStatus.ERROR
            
            return {
                "healthy": False,
                "error": str(e),
                "service_name": service_name,
                "consecutive_failures": metrics.consecutive_failures
            }
    
    def get_service_metrics(self, service_name: str) -> Optional[HealthMetrics]:
        """Get metrics for a specific service"""
        return self.metrics.get(service_name)
    
    def get_all_metrics(self) -> Dict[str, HealthMetrics]:
        """Get metrics for all services"""
        return self.metrics.copy()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        total_services = len(self.services)
        healthy_services = sum(1 for m in self.metrics.values() if m.status == ServiceStatus.RUNNING)
        unhealthy_services = sum(1 for m in self.metrics.values() if m.status == ServiceStatus.UNHEALTHY)
        error_services = sum(1 for m in self.metrics.values() if m.status == ServiceStatus.ERROR)
        
        # Get GPU status
        self.gpu_manager.refresh()
        gpu_info = [
            {
                "gpu_id": gpu.gpu_id,
                "name": gpu.name,
                "memory_used_mb": gpu.memory_used,
                "memory_total_mb": gpu.memory_total,
                "memory_free_mb": gpu.memory_free,
                "utilization_percent": gpu.utilization,
                "temperature_c": gpu.temperature
            }
            for gpu in self.gpu_manager.gpus
        ]
        
        overall_status = "healthy"
        if unhealthy_services > 0:
            overall_status = "degraded"
        elif error_services > 0:
            overall_status = "warning"
        elif healthy_services == 0 and total_services > 0:
            overall_status = "down"
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "total": total_services,
                "healthy": healthy_services,
                "unhealthy": unhealthy_services,
                "error": error_services,
                "stopped": total_services - healthy_services - unhealthy_services - error_services
            },
            "gpu_info": gpu_info,
            "monitoring_enabled": self.monitoring_enabled,
            "check_interval": self.check_interval
        }
    
    async def restart_unhealthy_services(self) -> Dict[str, Any]:
        """Attempt to restart unhealthy services"""
        restart_results = {}
        
        for service_name, metrics in self.metrics.items():
            if metrics.status == ServiceStatus.UNHEALTHY:
                try:
                    logger.info(f"Attempting to restart unhealthy service: {service_name}")
                    service = self.services[service_name]
                    
                    # Check if service has restart method
                    if hasattr(service, 'restart'):
                        result = await service.restart()
                        restart_results[service_name] = result
                    elif hasattr(service, 'stop') and hasattr(service, 'start'):
                        # Manual restart
                        await service.stop()
                        await asyncio.sleep(2)
                        result = await service.start()
                        restart_results[service_name] = result
                    else:
                        restart_results[service_name] = {
                            "success": False,
                            "error": "Service does not support restart"
                        }
                        
                except Exception as e:
                    logger.error(f"Failed to restart service {service_name}: {e}")
                    restart_results[service_name] = {
                        "success": False,
                        "error": str(e)
                    }
        
        return restart_results
    
    async def _monitor_service(self, service_name: str):
        """Background monitoring task for a service"""
        logger.info(f"Starting background monitoring for service: {service_name}")
        
        try:
            while True:
                await self.check_service_health(service_name)
                await asyncio.sleep(self.check_interval)
                
        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled for service: {service_name}")
        except Exception as e:
            logger.error(f"Monitoring error for service {service_name}: {e}")
    
    async def _global_monitor(self):
        """Global monitoring task for system-wide health"""
        logger.info("Starting global health monitoring")
        
        try:
            while self.monitoring_enabled:
                # Check system resources
                self.gpu_manager.refresh()
                
                # Log system health periodically
                system_health = self.get_system_health()
                if system_health["overall_status"] != "healthy":
                    logger.warning(f"System health: {system_health['overall_status']}")
                
                # Auto-restart unhealthy services if configured
                unhealthy_count = system_health["services"]["unhealthy"]
                if unhealthy_count > 0:
                    logger.info(f"Found {unhealthy_count} unhealthy services, attempting restart...")
                    await self.restart_unhealthy_services()
                
                await asyncio.sleep(self.check_interval * 2)  # Less frequent than individual checks
                
        except asyncio.CancelledError:
            logger.info("Global monitoring cancelled")
        except Exception as e:
            logger.error(f"Global monitoring error: {e}")


# Global health checker instance
_health_checker = None

def get_health_checker() -> LocalHealthChecker:
    """Get global health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = LocalHealthChecker()
    return _health_checker