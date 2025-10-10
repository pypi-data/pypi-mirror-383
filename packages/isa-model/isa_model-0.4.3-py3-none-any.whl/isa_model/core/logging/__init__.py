"""
Logging module for ISA Model

Provides comprehensive logging capabilities including:
- Loki-based centralized application logging (via loki_logger)
- InfluxDB-based inference metrics logging (via influx_logger)
- Real-time monitoring and alerting

Architecture:
- Loki: General application logs (INFO, WARNING, ERROR, DEBUG)
- InfluxDB: Inference metrics (tokens, costs, performance data)
"""

# InfluxDB inference metrics logging
from .influx_logger import (
    InfluxInferenceLogger,
    InferenceLogEntry,
    get_inference_logger,
    generate_request_id
)

# Loki centralized application logging
from .loki_logger import (
    setup_logger,
    app_logger,
    api_logger,
    client_logger,
    inference_logger,
    training_logger,
    eval_logger,
    db_logger,
    deployment_logger,
    model_logger,
)

__all__ = [
    # InfluxDB inference logging
    'InfluxInferenceLogger',
    'InferenceLogEntry',
    'get_inference_logger',
    'generate_request_id',

    # Loki application logging
    'setup_logger',
    'app_logger',
    'api_logger',
    'client_logger',
    'inference_logger',
    'training_logger',
    'eval_logger',
    'db_logger',
    'deployment_logger',
    'model_logger',
]