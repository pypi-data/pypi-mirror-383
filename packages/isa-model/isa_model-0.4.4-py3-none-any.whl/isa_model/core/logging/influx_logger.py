"""
InfluxDB-based Inference Logging System for ISA Model

This module provides comprehensive logging for model inference requests,
optimized for time-series analysis and monitoring.

Data Model:
- measurement: 'inference_requests' (main table)
- tags: indexed fields for fast queries (provider, model, service_type, etc.)
- fields: numerical and text data (tokens, costs, response_time, etc.)
- timestamp: automatic time-based partitioning

Key Features:
- Automatic data retention (30 days default)
- Cost-effective storage with compression
- Real-time monitoring capabilities
- Aggregated metrics generation
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import uuid

logger = logging.getLogger(__name__)

@dataclass
class InferenceLogEntry:
    """
    Structure for inference log data
    """
    # Required fields
    request_id: str
    service_type: str  # 'text', 'vision', 'audio', 'image', 'embedding'
    task: str         # 'chat', 'analyze_image', 'generate_speech', etc.
    provider: str     # 'openai', 'replicate', 'anthropic', etc.
    model_name: str   # Actual model used
    status: str       # 'completed', 'failed', 'timeout'
    
    # Timing data
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    queue_time_ms: Optional[int] = None
    
    # Token and usage data
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    # Cost data
    estimated_cost_usd: Optional[float] = None
    actual_cost_usd: Optional[float] = None
    cost_breakdown: Optional[Dict[str, Any]] = None
    
    # Request/response data (optional, for debugging)
    input_data_hash: Optional[str] = None
    input_size_bytes: Optional[int] = None
    output_size_bytes: Optional[int] = None
    
    # Streaming data
    is_streaming: bool = False
    stream_start_time: Optional[datetime] = None
    stream_chunks_count: Optional[int] = None
    time_to_first_token_ms: Optional[int] = None
    
    # Error information
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # Context and metadata
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    client_ip: Optional[str] = None
    model_version: Optional[str] = None
    cache_hit: bool = False
    
    # Quality metrics
    quality_score: Optional[float] = None
    user_feedback: Optional[int] = None  # 1-5 rating
    
    # Additional metadata
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

class InfluxInferenceLogger:
    """
    InfluxDB-based logger for model inference activities
    
    Features:
    - Time-series storage optimized for metrics
    - Automatic data retention and compression
    - Real-time query capabilities
    - Cost tracking and analysis
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize InfluxDB connection"""
        self.enabled = os.getenv('ENABLE_INFERENCE_LOGGING', 'false').lower() == 'true'
        
        # Logging configuration - always set these regardless of enabled status
        self.retention_days = int(os.getenv('LOG_RETENTION_DAYS', '30'))
        self.log_detailed_requests = os.getenv('LOG_DETAILED_REQUESTS', 'true').lower() == 'true'
        self.log_sensitive_data = os.getenv('LOG_SENSITIVE_DATA', 'false').lower() == 'true'
        
        if not self.enabled:
            logger.info("Inference logging disabled via ENABLE_INFERENCE_LOGGING")
            return
        
        # InfluxDB configuration
        from ..config.config_manager import ConfigManager
        config_manager = ConfigManager()
        # Use Consul discovery for InfluxDB URL with fallback
        self.url = os.getenv('INFLUXDB_URL', config_manager.get_influxdb_url())
        self.token = os.getenv('INFLUXDB_TOKEN', 'dev-token-isa-model-12345')
        self.org = os.getenv('INFLUXDB_ORG', 'isa-model')
        self.bucket = os.getenv('INFLUXDB_BUCKET', 'isa-model-logs')
        
        try:
            # Initialize InfluxDB client
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            
            # Test connection
            self._test_connection()
            logger.info(f"InfluxDB inference logger initialized: {self.url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize InfluxDB logger: {e}")
            self.enabled = False
    
    def _test_connection(self):
        """Test InfluxDB connection"""
        try:
            health = self.client.health()
            if health.status == "pass":
                logger.debug("InfluxDB connection healthy")
            else:
                raise Exception(f"InfluxDB health check failed: {health.message}")
        except Exception as e:
            raise Exception(f"InfluxDB connection test failed: {e}")
    
    def _create_data_hash(self, data: Any) -> str:
        """Create SHA-256 hash of input data for deduplication"""
        try:
            if isinstance(data, (dict, list)):
                data_str = json.dumps(data, sort_keys=True)
            else:
                data_str = str(data)
            return hashlib.sha256(data_str.encode()).hexdigest()
        except Exception:
            return None
    
    def log_inference_start(
        self,
        request_id: str,
        service_type: str,
        task: str,
        provider: str,
        model_name: str,
        input_data: Any = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        is_streaming: bool = False,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log the start of an inference request
        """
        if not self.enabled:
            return
        
        try:
            start_time = datetime.now(timezone.utc)
            
            # Create data hash for input
            input_hash = None
            input_size = None
            if input_data and self.log_detailed_requests:
                input_hash = self._create_data_hash(input_data)
                try:
                    input_size = len(str(input_data).encode('utf-8'))
                except:
                    input_size = None
            
            # Create InfluxDB point
            point = Point("inference_requests") \
                .tag("service_type", service_type) \
                .tag("task", task) \
                .tag("provider", provider) \
                .tag("model_name", model_name) \
                .tag("status", "started") \
                .field("request_id", request_id) \
                .field("is_streaming", is_streaming) \
                .time(start_time, WritePrecision.MS)
            
            # Add optional tags and fields
            if session_id:
                point = point.tag("session_id", session_id)
            if user_id:
                point = point.tag("user_id", user_id)
            if client_ip and not self.log_sensitive_data:
                # Hash IP for privacy
                ip_hash = hashlib.md5(client_ip.encode()).hexdigest()[:8]
                point = point.field("client_ip_hash", ip_hash)
            if input_hash:
                point = point.field("input_data_hash", input_hash)
            if input_size:
                point = point.field("input_size_bytes", input_size)
            if custom_metadata:
                for key, value in custom_metadata.items():
                    point = point.field(f"meta_{key}", str(value))
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            logger.debug(f"Logged inference start: {request_id}")
            
        except Exception as e:
            logger.error(f"Failed to log inference start: {e}")
    
    def log_inference_complete(
        self,
        request_id: str,
        status: str = "completed",
        execution_time_ms: Optional[int] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        estimated_cost_usd: Optional[float] = None,
        output_data: Any = None,
        stream_chunks_count: Optional[int] = None,
        time_to_first_token_ms: Optional[int] = None,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
        cache_hit: bool = False,
        quality_score: Optional[float] = None,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log the completion of an inference request
        """
        if not self.enabled:
            return
        
        try:
            end_time = datetime.now(timezone.utc)
            
            # Calculate output data size
            output_size = None
            if output_data and self.log_detailed_requests:
                try:
                    output_size = len(str(output_data).encode('utf-8'))
                except:
                    output_size = None
            
            # Create InfluxDB point
            point = Point("inference_requests") \
                .tag("status", status) \
                .field("request_id", request_id) \
                .field("cache_hit", cache_hit) \
                .time(end_time, WritePrecision.MS)
            
            # Add timing data
            if execution_time_ms is not None:
                point = point.field("execution_time_ms", execution_time_ms)
            
            # Add token data
            if input_tokens is not None:
                point = point.field("input_tokens", input_tokens)
            if output_tokens is not None:
                point = point.field("output_tokens", output_tokens)
            if input_tokens and output_tokens:
                point = point.field("total_tokens", input_tokens + output_tokens)
            
            # Add cost data
            if estimated_cost_usd is not None:
                point = point.field("estimated_cost_usd", float(estimated_cost_usd))
            
            # Add output data size
            if output_size:
                point = point.field("output_size_bytes", output_size)
            
            # Add streaming metrics
            if stream_chunks_count is not None:
                point = point.field("stream_chunks_count", stream_chunks_count)
            if time_to_first_token_ms is not None:
                point = point.field("time_to_first_token_ms", time_to_first_token_ms)
            
            # Add error information
            if error_message:
                point = point.field("error_message", error_message[:500])  # Limit length
            if error_code:
                point = point.field("error_code", error_code)
            
            # Add quality metrics
            if quality_score is not None:
                point = point.field("quality_score", float(quality_score))
            
            # Add custom metadata
            if custom_metadata:
                for key, value in custom_metadata.items():
                    point = point.field(f"meta_{key}", str(value))
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            logger.debug(f"Logged inference completion: {request_id} ({status})")
            
        except Exception as e:
            logger.error(f"Failed to log inference completion: {e}")
    
    def log_token_usage(
        self,
        request_id: str,
        provider: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        prompt_cost_usd: Optional[float] = None,
        completion_cost_usd: Optional[float] = None
    ) -> None:
        """
        Log detailed token usage data
        """
        if not self.enabled:
            return
        
        try:
            timestamp = datetime.now(timezone.utc)
            total_tokens = prompt_tokens + completion_tokens
            total_cost = (prompt_cost_usd or 0) + (completion_cost_usd or 0)
            
            point = Point("token_usage") \
                .tag("provider", provider) \
                .tag("model_name", model_name) \
                .field("request_id", request_id) \
                .field("prompt_tokens", prompt_tokens) \
                .field("completion_tokens", completion_tokens) \
                .field("total_tokens", total_tokens) \
                .time(timestamp, WritePrecision.MS)
            
            if prompt_cost_usd is not None:
                point = point.field("prompt_cost_usd", float(prompt_cost_usd))
            if completion_cost_usd is not None:
                point = point.field("completion_cost_usd", float(completion_cost_usd))
            if total_cost > 0:
                point = point.field("total_cost_usd", float(total_cost))
                point = point.field("cost_per_token_usd", float(total_cost / total_tokens))
            
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            logger.debug(f"Logged token usage: {request_id}")
            
        except Exception as e:
            logger.error(f"Failed to log token usage: {e}")
    
    def log_error(
        self,
        request_id: str,
        error_type: str,
        error_message: str,
        error_code: Optional[str] = None,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        retry_count: int = 0
    ) -> None:
        """
        Log error events
        """
        if not self.enabled:
            return
        
        try:
            timestamp = datetime.now(timezone.utc)
            
            point = Point("inference_errors") \
                .tag("error_type", error_type) \
                .field("request_id", request_id) \
                .field("error_message", error_message[:500]) \
                .field("retry_count", retry_count) \
                .time(timestamp, WritePrecision.MS)
            
            if error_code:
                point = point.field("error_code", error_code)
            if provider:
                point = point.tag("provider", provider)
            if model_name:
                point = point.tag("model_name", model_name)
            
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            logger.debug(f"Logged error: {request_id} - {error_type}")
            
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
    
    def get_recent_requests(
        self,
        limit: int = 100,
        hours: int = 24,
        service_type: Optional[str] = None,
        provider: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query recent inference requests
        """
        if not self.enabled:
            return []
        
        try:
            # Build query with simpler filtering
            filters = []
            if service_type:
                filters.append(f'r.service_type == "{service_type}"')
            if provider:
                filters.append(f'r.provider == "{provider}"')
            if status:
                filters.append(f'r.status == "{status}"')
            
            # Build filter clause
            if filters:
                filter_clause = " and " + " and ".join(filters)
            else:
                filter_clause = ""
            
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -{hours}h)
                |> filter(fn: (r) => r._measurement == "inference_requests"{filter_clause})
                |> filter(fn: (r) => r._field == "request_id")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: {limit})
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            # Process results - get unique request IDs first
            request_ids = []
            for table in result:
                for record in table.records:
                    request_id = record.get_value()
                    if request_id not in [r.get('request_id') for r in request_ids]:
                        request_ids.append({
                            'request_id': request_id,
                            'time': record.get_time(),
                            'service_type': record.values.get('service_type'),
                            'provider': record.values.get('provider'),
                            'model_name': record.values.get('model_name'),
                            'status': record.values.get('status'),
                            'task': record.values.get('task')
                        })
            
            return request_ids
            
        except Exception as e:
            logger.error(f"Failed to query recent requests: {e}")
            return []
    
    def get_usage_statistics(
        self,
        hours: int = 24,
        group_by: str = "provider"  # "provider", "model_name", "service_type"
    ) -> Dict[str, Any]:
        """
        Get usage statistics and metrics
        """
        if not self.enabled:
            return {}
        
        try:
            # Simplified query to count unique request IDs by group
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -{hours}h)
                |> filter(fn: (r) => r._measurement == "inference_requests")
                |> filter(fn: (r) => r._field == "request_id")
                |> group(columns: ["{group_by}"])
                |> count()
                |> yield(name: "request_counts")
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            # Process results into statistics
            stats = {}
            for table in result:
                for record in table.records:
                    key = record.values.get(group_by, 'unknown')
                    stats[key] = {
                        'total_requests': record.get_value() or 0,
                        'group_by': group_by,
                        'time_range_hours': hours
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get usage statistics: {e}")
            return {}
    
    def close(self):
        """Close InfluxDB connection"""
        if self.enabled and hasattr(self, 'client'):
            self.client.close()

# Global logger instance
_inference_logger: Optional[InfluxInferenceLogger] = None

def get_inference_logger() -> InfluxInferenceLogger:
    """Get or create global inference logger instance"""
    global _inference_logger
    if _inference_logger is None:
        _inference_logger = InfluxInferenceLogger()
    return _inference_logger

def generate_request_id() -> str:
    """Generate unique request ID"""
    return f"req_{uuid.uuid4().hex[:12]}"