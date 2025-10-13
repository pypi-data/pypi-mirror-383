"""
Unified API Route - Single endpoint for all AI services

This is the main API that handles all types of AI requests:
- Vision tasks (image analysis, OCR, UI detection)
- Text tasks (chat, generation, translation) 
- Audio tasks (TTS, STT)
- Image generation tasks
- Embedding tasks
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union, List, AsyncGenerator
import logging
from ..middleware.auth import optional_auth, require_read_access, require_write_access
from ..middleware.security import rate_limit_standard, rate_limit_heavy, sanitize_input
import asyncio
import json
import time
from pathlib import Path

from isa_model.client import ISAModelClient

logger = logging.getLogger(__name__)
router = APIRouter()

class UnifiedRequest(BaseModel):
    """
    **统一请求模型 - 支持所有AI服务类型**
    
    这个模型为所有AI服务（文本、视觉、音频、图像生成、嵌入）提供统一的请求接口。
    
    **支持的服务类型**:
    - `text`: 文本服务 (聊天、生成、翻译)
    - `vision`: 视觉服务 (图像分析、OCR、UI检测)
    - `audio`: 音频服务 (TTS、STT、转录)
    - `image`: 图像生成服务 (文本生成图像、图像转换)
    - `embedding`: 嵌入服务 (文本向量化、相似度计算)
    
    **请求示例**:
    ```json
    {
        "input_data": "你好，世界！",
        "task": "chat",
        "service_type": "text",
        "model": "gpt-4o-mini",
        "provider": "openai"
    }
    ```
    """
    input_data: Union[str, Dict[str, Any]] = Field(
        ..., 
        description="输入数据，支持多种格式：文本字符串、LangChain消息列表、图像URL/路径、音频文件路径等。根据service_type确定具体格式。",
        examples=["你好，世界！", "https://example.com/image.jpg", "/path/to/audio.mp3"]
    )
    task: str = Field(
        ..., 
        description="要执行的任务类型。常见任务：chat(聊天)、analyze_image(图像分析)、generate_speech(语音生成)、create_embedding(创建嵌入)等。",
        examples=["chat", "analyze_image", "generate_speech", "transcribe", "generate_image", "create_embedding"]
    )
    service_type: str = Field(
        ..., 
        description="服务类型，决定使用哪种AI服务。可选值：text、vision、audio、image、embedding。",
        examples=["text", "vision", "audio", "image", "embedding"]
    )
    model: Optional[str] = Field(
        None, 
        description="可选的模型指定。如果指定，系统将尝试使用该模型。常见模型：gpt-4o-mini、gpt-4o、whisper-1、flux-schnell等。",
        examples=["gpt-4o-mini", "gpt-4o", "whisper-1", "tts-1", "flux-schnell", "text-embedding-3-small"]
    )
    provider: Optional[str] = Field(
        None, 
        description="可选的服务提供商指定。如果指定，系统将尝试使用该提供商。常见提供商：openai、replicate、anthropic等。",
        examples=["openai", "replicate", "anthropic"]
    )
    stream: Optional[bool] = Field(
        None, 
        description="是否启用流式响应。仅适用于文本服务。text+chat任务默认启用流式。当使用工具调用时会自动禁用流式响应以确保完整性。"
    )
    tools: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="可选的工具列表，用于函数调用功能。仅适用于文本服务。工具格式遵循LangChain工具规范。使用工具时会自动禁用流式响应。",
        examples=[[
            {
                "name": "get_weather",
                "description": "获取天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "城市名称"}
                    },
                    "required": ["location"]
                }
            }
        ]]
    )
    output_format: Optional[str] = Field(
        None, 
        description="输出格式控制。支持的格式：json(JSON结构化输出)、markdown(Markdown格式)、code(代码块提取)、structured(智能结构化解析)。主要用于文本服务的响应格式化。",
        examples=["json", "markdown", "code", "structured"]
    )
    json_schema: Optional[Dict[str, Any]] = Field(
        None, 
        description="JSON模式验证。当output_format='json'时使用，用于验证和约束JSON输出格式。遵循JSON Schema规范。",
        examples=[{
            "type": "object",
            "properties": {
                "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["sentiment", "confidence"]
        }]
    )
    repair_attempts: Optional[int] = Field(
        3, 
        ge=0, 
        le=10,
        description="JSON修复尝试次数。当解析JSON失败时，系统会尝试修复常见的JSON格式错误。0表示不进行修复尝试。",
        examples=[3, 0, 5]
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="额外的任务参数，用于精细控制服务行为。参数内容根据具体服务类型而定，如temperature、max_tokens、voice等。",
        examples=[{"temperature": 0.7, "max_tokens": 1000}, {"voice": "alloy", "speed": 1.0}, {"width": 1024, "height": 1024}]
    )

class UnifiedResponse(BaseModel):
    """
    **统一响应模型 - 所有AI服务的标准响应格式**
    
    提供一致的成功/失败状态、结果数据和元数据信息。
    
    **成功响应示例**:
    ```json
    {
        "success": true,
        "result": {
            "content": "你好！我是AI助手。",
            "tool_calls": [],
            "response_metadata": {
                "token_usage": {
                    "prompt_tokens": 15,
                    "completion_tokens": 10,
                    "total_tokens": 25
                }
            }
        },
        "error": null,
        "metadata": {
            "model_used": "gpt-4o-mini",
            "provider": "openai",
            "task": "chat",
            "service_type": "text",
            "processing_time": 1.23
        }
    }
    ```
    
    **错误响应示例**:
    ```json
    {
        "success": false,
        "result": null,
        "error": "Model 'invalid-model' not found",
        "metadata": {
            "error_code": "MODEL_NOT_FOUND",
            "task": "chat",
            "service_type": "text"
        }
    }
    ```
    """
    success: bool = Field(
        ..., 
        description="请求是否成功执行。true表示成功，false表示失败。"
    )
    result: Optional[Any] = Field(
        None, 
        description="服务执行结果。成功时包含实际数据，失败时为null。数据类型根据服务类型而定：文本服务返回AIMessage对象，视觉服务返回分析文本，音频服务返回文件路径或文本，图像服务返回图像URL，嵌入服务返回向量数组。"
    )
    error: Optional[str] = Field(
        None, 
        description="错误信息描述。成功时为null，失败时包含详细的错误说明。"
    )
    metadata: Dict[str, Any] = Field(
        ..., 
        description="响应元数据，包含执行信息如使用的模型、提供商、处理时间、token使用量等。元数据内容根据服务类型和执行情况而定。"
    )

# Global ISA client instance for server-side processing
_isa_client = None

def get_isa_client():
    """Get or create ISA client for service processing"""
    global _isa_client
    if _isa_client is None:
        _isa_client = ISAModelClient()  # Use direct service mode
    return _isa_client

@router.get("/")
async def unified_info():
    """API information"""
    return {
        "service": "unified_api",
        "status": "active",
        "description": "Single endpoint for all AI services",
        "supported_service_types": ["vision", "text", "audio", "image", "embedding"],
        "version": "1.0.0"
    }

@router.post("/invoke")
@rate_limit_standard()
async def unified_invoke(request: Request, user: Dict = Depends(require_read_access)):
    """
    **Unified API endpoint for all AI services**
    
    Supports both JSON and multipart/form-data requests:
    - JSON: Standard API request with UnifiedRequest body
    - Form: File upload with form parameters
    
    This single endpoint handles:
    - Vision: image analysis, OCR, UI detection
    - Text: chat, generation, translation
    - Audio: TTS, STT, transcription
    - Image: generation, img2img
    - Embedding: text embedding, similarity
    
    **Uses ISAModelClient in local mode - all the complex logic is in client.py**
    """
    try:
        # Get ISA client instance (service mode)
        client = get_isa_client()
        
        # Check content type to determine request format
        content_type = request.headers.get("content-type", "")
        
        if content_type.startswith("multipart/form-data"):
            # Handle form data with file upload
            form = await request.form()
            
            # Extract required fields
            task = form.get("task")
            service_type = form.get("service_type")
            model = form.get("model")
            provider = form.get("provider")
            parameters = form.get("parameters")
            file = form.get("file")
            
            if not task or not service_type:
                raise HTTPException(status_code=400, detail="task and service_type are required")
            
            if file is None:
                raise HTTPException(status_code=400, detail="file is required for multipart requests")
            
            # Read file data
            file_data = await file.read()
            
            # Parse parameters if provided as JSON string
            parsed_params = {}
            if parameters:
                try:
                    parsed_params = json.loads(parameters)
                except json.JSONDecodeError:
                    parsed_params = {}
            
            result = await client._invoke_service(
                input_data=file_data,
                task=task,
                service_type=service_type,
                model_hint=model,
                provider_hint=provider,
                filename=file.filename,
                content_type=file.content_type,
                file_size=len(file_data),
                **parsed_params
            )
            
            # Return the result in our API format
            return UnifiedResponse(
                success=result["success"],
                result=result.get("result"),
                error=result.get("error"),
                metadata={
                    **result["metadata"],
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "file_size": len(file_data)
                }
            )
        
        else:
            # Handle JSON request
            try:
                json_body = await request.json()
                unified_request = UnifiedRequest(**json_body)
                
                # Sanitize string inputs to prevent XSS and injection attacks
                if isinstance(unified_request.input_data, str):
                    unified_request.input_data = sanitize_input(unified_request.input_data)
                
            except Exception as e:
                from ..error_handlers import handle_validation_error, create_http_exception, ErrorCode
                if hasattr(e, 'errors'):  # Pydantic validation error
                    error_response = handle_validation_error(e)
                    raise HTTPException(status_code=400, detail=error_response)
                else:
                    raise create_http_exception(
                        f"请求JSON格式错误: {str(e)}",
                        400,
                        ErrorCode.INVALID_INPUT,
                        {"suggestion": "请检查JSON格式和必需字段"}
                    )
            
            # Prepare parameters, ensuring tools isn't duplicated
            params = dict(unified_request.parameters) if unified_request.parameters else {}
            if unified_request.tools:
                params.pop("tools", None)  # Remove tools from parameters if present
                params["tools"] = unified_request.tools
            
            # Add JSON output formatting parameters
            if unified_request.output_format:
                params["output_format"] = unified_request.output_format
            if unified_request.json_schema:
                params["json_schema"] = unified_request.json_schema
            if unified_request.repair_attempts is not None:
                params["repair_attempts"] = unified_request.repair_attempts
            
            # Check if this should be a streaming response
            # Default to streaming for text+chat unless explicitly disabled
            is_text_chat = (unified_request.service_type == "text" and unified_request.task == "chat")
            stream_setting = unified_request.stream if unified_request.stream is not None else is_text_chat
            
            should_stream = (
                is_text_chat and 
                not unified_request.tools and  # No tools
                stream_setting  # Stream enabled by default for text+chat or explicitly
            )
            
            
            if should_stream:
                # Return streaming response for text chat
                async def generate_stream():
                    try:
                        # Use streaming invoke but track metadata manually
                        collected_tokens = []
                        selected_model = None
                        service_info = None
                        start_time = time.time()
                        
                        # Get model selection info first (lightweight operation)
                        try:
                            selected_model = await client._select_model(
                                input_data=unified_request.input_data,
                                task=unified_request.task,
                                service_type=unified_request.service_type,
                                model_hint=unified_request.model,
                                provider_hint=unified_request.provider
                            )
                            service_info = {
                                "model_used": selected_model["model_id"],
                                "provider": selected_model["provider"],
                                "task": unified_request.task,
                                "service_type": unified_request.service_type,
                                "selection_reason": selected_model.get("reason", "Default selection"),
                                "streaming": True
                            }
                        except Exception:
                            pass
                        
                        # Stream the tokens and get metadata
                        processing_time = 0
                        async for item in client.invoke_stream(
                            input_data=unified_request.input_data,
                            task=unified_request.task,
                            service_type=unified_request.service_type,
                            model=unified_request.model,
                            provider=unified_request.provider,
                            return_metadata=True,  # Request metadata with billing info
                            **params
                        ):
                            if isinstance(item, tuple) and item[0] == 'metadata':
                                # This is the final metadata with billing info
                                metadata = item[1]
                                processing_time = time.time() - start_time
                                metadata["processing_time"] = processing_time
                                yield f"data: {json.dumps({'metadata': metadata})}\n\n"
                            else:
                                # This is a token
                                collected_tokens.append(item)
                                yield f"data: {json.dumps({'token': item})}\n\n"
                        
                    except Exception as e:
                        from ..error_handlers import create_error_response, ErrorCode
                        # Create detailed error response for streaming
                        error_response = create_error_response(
                            error=e,
                            error_code=ErrorCode.INFERENCE_FAILED,
                            details={
                                "service_type": unified_request.service_type,
                                "model": unified_request.model,
                                "provider": unified_request.provider,
                                "streaming": True
                            }
                        )
                        # Send structured error as final event
                        yield f"data: {json.dumps({'error': error_response})}\n\n"
                    finally:
                        # Send end-of-stream marker
                        yield f"data: {json.dumps({'done': True})}\n\n"
                
                return StreamingResponse(
                    generate_stream(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no"  # Disable nginx buffering
                    }
                )
            else:
                # Non-streaming response (original behavior)
                result = await client._invoke_service(
                    input_data=unified_request.input_data,
                    task=unified_request.task,
                    service_type=unified_request.service_type,
                    model_hint=unified_request.model,
                    provider_hint=unified_request.provider,
                    **params
                )
                
                # Return the result in our API format
                return UnifiedResponse(
                    success=result["success"],
                    result=result.get("result"),
                    error=result.get("error"),
                    metadata=result["metadata"]
                )
        
    except HTTPException:
        raise
    except Exception as e:
        from ..error_handlers import create_error_response, ErrorCode
        logger.error(f"Unified invoke failed: {e}")
        
        # Create detailed error response
        error_response = create_error_response(
            error=e,
            status_code=500,
            error_code=ErrorCode.INFERENCE_FAILED,
            details={
                "service_type": getattr(unified_request, 'service_type', 'unknown'),
                "model": getattr(unified_request, 'model', 'unknown'),
                "provider": getattr(unified_request, 'provider', 'unknown'),
                "task": getattr(unified_request, 'task', 'unknown')
            }
        )
        
        return UnifiedResponse(
            success=False,
            error=error_response.get("error"),
            metadata={
                "error_code": error_response.get("error_code"),
                "user_message": error_response.get("user_message"),
                "details": error_response.get("details", {})
            }
        )



@router.get("/models")
async def get_available_models(service_type: Optional[str] = None):
    """Get available models (optional filter by service type)"""
    try:
        from ..cache_manager import cached, model_list_cache_key
        
        @cached(ttl=600.0, cache_key_func=lambda st=service_type: model_list_cache_key(st))  # 10 minutes cache
        async def _get_models(service_type_param):
            client = get_isa_client()
            return await client.get_available_models(service_type_param)
        
        models_list = await _get_models(service_type)
        
        # Ensure we return the expected format
        if isinstance(models_list, list):
            return {
                "success": True,
                "models": models_list,
                "total_count": len(models_list),
                "service_type_filter": service_type
            }
        elif isinstance(models_list, dict) and "models" in models_list:
            # Already in correct format
            return models_list
        else:
            # Unknown format, convert to expected format
            return {
                "success": True,
                "models": models_list if isinstance(models_list, list) else [],
                "total_count": len(models_list) if isinstance(models_list, list) else 0,
                "service_type_filter": service_type
            }
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        # Fallback static model list
        # Load custom models
        custom_models = []
        try:
            from isa_model.inference.services.custom_model_manager import get_custom_model_manager
            custom_model_manager = get_custom_model_manager()
            custom_models = custom_model_manager.get_models_for_api()
            logger.debug(f"Loaded {len(custom_models)} custom models")
        except Exception as e:
            logger.warning(f"Failed to load custom models: {e}")
        
        # Base fallback models
        base_models = [
            {"service_type": "vision", "provider": "openai", "model_id": "gpt-4o-mini"},
            {"service_type": "text", "provider": "openai", "model_id": "gpt-4o-mini"},
            {"service_type": "audio", "provider": "openai", "model_id": "whisper-1"},
            {"service_type": "audio", "provider": "openai", "model_id": "tts-1"},
            {"service_type": "embedding", "provider": "openai", "model_id": "text-embedding-3-small"},
            {"service_type": "image", "provider": "replicate", "model_id": "black-forest-labs/flux-schnell"}
        ]
        
        # Combine base models with custom models
        fallback_models = base_models + custom_models
        
        # Filter by service_type if provided
        if service_type:
            fallback_models = [m for m in fallback_models if m["service_type"] == service_type]
        
        return {
            "success": False,
            "error": f"Failed to get models: {str(e)}",
            "models": fallback_models,
            "total_count": len(fallback_models),
            "service_type_filter": service_type,
            "fallback": True
        }

@router.get("/health")
async def health_check():
    """Health check for unified API"""
    try:
        client = get_isa_client()
        health_result = await client.health_check()
        return {
            "api": "healthy",
            "client_health": health_result
        }
    except Exception as e:
        return {
            "api": "error",
            "error": str(e)
        }

# Enhanced Model Management API Endpoints

@router.get("/models/search")
async def search_models(
    query: str = Query(..., description="Search query"),
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    capabilities: Optional[List[str]] = Query(None, description="Filter by capabilities"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    user = Depends(optional_auth)
):
    """Search models by query and filters"""
    try:
        # Try database search first
        try:
            from isa_model.core.models.model_repo import ModelRepo
            
            repo = ModelRepo()
            
            # Convert capabilities from query parameter
            capability_list = None
            if capabilities:
                capability_list = [cap.strip() for cap in capabilities if cap.strip()]
            
            results = repo.search_models(
                query=query,
                model_type=model_type,
                provider=provider,
                capabilities=capability_list,
                limit=limit
            )
            
            # If we got results from the database, return them
            if results:
                return {
                    "success": True,
                    "query": query,
                    "filters": {
                        "model_type": model_type,
                        "provider": provider,
                        "capabilities": capability_list
                    },
                    "results": [
                        {
                            "model_id": model.model_id,
                            "model_type": model.model_type,
                            "provider": model.provider,
                            "description": model.metadata.get("description", ""),
                            "capabilities": model.capabilities,
                            "updated_at": model.updated_at.isoformat() if model.updated_at else None
                        }
                        for model in results
                    ],
                    "total_results": len(results)
                }
            
        except Exception as db_error:
            logger.warning(f"Database search failed, using fallback: {db_error}")
        
        # Fallback: search in our hardcoded model list + custom models
        # Load custom models
        custom_models_for_search = []
        try:
            from isa_model.inference.services.custom_model_manager import get_custom_model_manager
            custom_model_manager = get_custom_model_manager()
            custom_models_for_search = custom_model_manager.get_models_for_api()
            # Convert format for search
            for model in custom_models_for_search:
                model["model_type"] = model.get("service_type", "text")
        except Exception as e:
            logger.warning(f"Failed to load custom models for search: {e}")
        
        fallback_models = [
            {
                "model_id": "gpt-4o-mini",
                "model_type": "text",
                "provider": "openai",
                "description": "Small, fast GPT-4 model optimized for efficiency",
                "capabilities": ["chat", "text_generation", "reasoning"],
                "service_type": "text"
            },
            {
                "model_id": "gpt-4o",
                "model_type": "text", 
                "provider": "openai",
                "description": "Large GPT-4 model with enhanced capabilities",
                "capabilities": ["chat", "text_generation", "reasoning", "image_understanding"],
                "service_type": "text"
            },
            {
                "model_id": "text-embedding-3-small",
                "model_type": "embedding",
                "provider": "openai", 
                "description": "Small embedding model for text vectorization",
                "capabilities": ["embedding", "similarity"],
                "service_type": "embedding"
            },
            {
                "model_id": "whisper-1",
                "model_type": "audio",
                "provider": "openai",
                "description": "Speech recognition and transcription model",
                "capabilities": ["speech_to_text", "audio_transcription"],
                "service_type": "audio"
            },
            {
                "model_id": "tts-1",
                "model_type": "audio",
                "provider": "openai",
                "description": "Text-to-speech generation model",
                "capabilities": ["text_to_speech"],
                "service_type": "audio"
            },
            {
                "model_id": "flux-schnell",
                "model_type": "image",
                "provider": "replicate",
                "description": "Fast image generation model",
                "capabilities": ["image_generation"],
                "service_type": "image"
            },
            {
                "model_id": "isa-llm-service",
                "model_type": "text",
                "provider": "isa",
                "description": "ISA custom LLM service for trained models",
                "capabilities": ["chat", "text_generation"],
                "service_type": "text"
            },
            {
                "model_id": "isa-omniparser-ui-detection",
                "model_type": "vision",
                "provider": "isa",
                "description": "UI element detection and analysis",
                "capabilities": ["ui_detection", "image_analysis"],
                "service_type": "vision"
            }
        ]
        
        # Add custom models to search list
        fallback_models.extend(custom_models_for_search)
        
        # Apply search filters
        query_lower = query.lower()
        filtered_models = []
        
        for model in fallback_models:
            # Check if query matches
            query_match = (
                query_lower in model["model_id"].lower() or
                query_lower in model["provider"].lower() or
                query_lower in model["description"].lower() or
                any(query_lower in cap.lower() for cap in model["capabilities"])
            )
            
            if not query_match:
                continue
                
            # Apply type filter
            if model_type and model["model_type"] != model_type:
                continue
                
            # Apply provider filter 
            if provider and model["provider"] != provider:
                continue
                
            # Apply capabilities filter
            if capabilities:
                if not any(cap in model["capabilities"] for cap in capabilities):
                    continue
            
            filtered_models.append({
                "model_id": model["model_id"],
                "model_type": model["model_type"],
                "provider": model["provider"],
                "description": model["description"],
                "capabilities": model["capabilities"],
                "updated_at": None
            })
        
        # Apply limit
        limited_results = filtered_models[:limit]
        
        return {
            "success": True,
            "query": query,
            "filters": {
                "model_type": model_type,
                "provider": provider,
                "capabilities": capabilities
            },
            "results": limited_results,
            "total_results": len(limited_results),
            "fallback": True,
            "message": "Using fallback search - database search unavailable"
        }
        
    except Exception as e:
        logger.error(f"Failed to search models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search models: {str(e)}")

@router.get("/models/providers")
async def get_model_providers(user = Depends(optional_auth)):
    """Get list of available model providers"""
    try:
        from ..cache_manager import cached, provider_list_cache_key
        
        @cached(ttl=600.0, cache_key_func=lambda: provider_list_cache_key())  # 10 minutes cache
        async def _get_providers():
            try:
                from isa_model.core.models.model_repo import ModelRepo
                repo = ModelRepo()
                return repo.get_providers_summary()
            except Exception as e:
                logger.warning(f"ModelRepo failed, using fallback: {e}")
                # Fallback to basic provider list
                return [
                    {
                        "provider": "openai",
                        "model_count": 4,
                        "model_types": ["text", "vision", "audio", "embedding"],
                        "capabilities": ["chat", "completion", "embedding", "vision", "audio"]
                    },
                    {
                        "provider": "isa",
                        "model_count": 3,
                        "model_types": ["text", "vision", "embedding"],
                        "capabilities": ["chat", "completion", "ui_detection", "ocr"]
                    },
                    {
                        "provider": "replicate",
                        "model_count": 2,
                        "model_types": ["image", "video"],
                        "capabilities": ["image_generation", "video_generation"]
                    }
                ]
        
        providers = await _get_providers()
        
        return {
            "success": True,
            "providers": providers,
            "total_count": len(providers),
            "cached": True
        }
        
    except Exception as e:
        logger.error(f"Failed to get model providers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model providers: {str(e)}")

@router.get("/models/custom")
async def get_custom_models(
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    user = Depends(optional_auth)
):
    """Get list of custom trained models"""
    try:
        from ..cache_manager import cached, custom_models_cache_key
        from isa_model.inference.services.custom_model_manager import get_custom_model_manager
        
        @cached(ttl=300.0, cache_key_func=lambda mt=model_type, p=provider: custom_models_cache_key(mt, p))  # 5 minutes cache
        async def _get_custom_models(model_type_param, provider_param):
            custom_model_manager = get_custom_model_manager()
            return custom_model_manager.list_models(model_type=model_type_param, provider=provider_param)
        
        models = await _get_custom_models(model_type, provider)
        
        # Convert to API format
        api_models = []
        for model in models:
            api_model = {
                "model_id": model.model_id,
                "model_name": model.model_name,
                "model_type": model.model_type,
                "provider": model.provider,
                "base_model": model.base_model,
                "training_date": model.training_date,
                "description": model.metadata.get("description", ""),
                "capabilities": model.capabilities,
                "custom": True
            }
            
            if model.performance_metrics:
                api_model["performance_metrics"] = model.performance_metrics
            
            if model.deployment_config:
                api_model["deployment_status"] = "configured"
            
            api_models.append(api_model)
        
        return {
            "success": True,
            "custom_models": api_models,
            "total_count": len(api_models),
            "filters": {
                "model_type": model_type,
                "provider": provider
            },
            "stats": custom_model_manager.get_stats()
        }
        
    except Exception as e:
        logger.error(f"Failed to get custom models: {e}")
        return {
            "success": False,
            "error": str(e),
            "custom_models": [],
            "total_count": 0
        }

@router.get("/models/capabilities")
async def get_model_capabilities(user = Depends(optional_auth)):
    """Get list of all available model capabilities"""
    try:
        from ..cache_manager import cached
        
        @cached(ttl=3600.0, cache_key_func=lambda: "model_capabilities")  # 1 hour cache (static data)
        async def _get_capabilities():
            from isa_model.core.models.model_repo import ModelCapability
            
            return [
                {
                    "capability": cap.value,
                    "description": cap.value.replace("_", " ").title()
                }
                for cap in ModelCapability
            ]
        
        capabilities = await _get_capabilities()
        
        return {
            "success": True,
            "capabilities": capabilities
        }
        
    except Exception as e:
        logger.error(f"Failed to get model capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model capabilities: {str(e)}")

@router.get("/models/{model_id}")
async def get_model_details(model_id: str, user = Depends(optional_auth)):
    """Get detailed information about a specific model"""
    try:
        from ..cache_manager import cached
        from isa_model.core.models.model_repo import ModelRepo
        
        @cached(ttl=900.0, cache_key_func=lambda mid=model_id: f"model_details_{mid}")  # 15 minutes cache
        async def _get_model_details(model_id_param):
            repo = ModelRepo()
            return repo.get_model_by_id(model_id_param)
        
        model = await _get_model_details(model_id)
        
        if not model:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        return {
            "success": True,
            "model": {
                "model_id": model.model_id,
                "model_type": model.model_type,
                "provider": model.provider,
                "metadata": model.metadata,
                "capabilities": model.capabilities,
                "created_at": model.created_at.isoformat() if model.created_at else None,
                "updated_at": model.updated_at.isoformat() if model.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model details for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model details: {str(e)}")

@router.get("/models/{model_id}/versions")
async def get_model_versions(model_id: str, user = Depends(optional_auth)):
    """Get version history for a specific model"""
    try:
        from isa_model.core.models.model_version_manager import ModelVersionManager
        
        version_manager = ModelVersionManager()
        versions = version_manager.get_model_versions(model_id)
        
        return {
            "success": True,
            "model_id": model_id,
            "versions": [
                {
                    "version": v.version,
                    "created_at": v.created_at.isoformat(),
                    "metadata": v.metadata,
                    "is_active": v.is_active
                }
                for v in versions
            ],
            "total_versions": len(versions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get model versions for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model versions: {str(e)}")

@router.post("/models/{model_id}/versions")
async def create_model_version(
    model_id: str,
    version_data: Dict[str, Any],
    user = Depends(require_write_access)
):
    """Create a new version for a model"""
    try:
        from isa_model.core.models.model_version_manager import ModelVersionManager
        
        version_manager = ModelVersionManager()
        new_version = version_manager.create_version(
            model_id=model_id,
            metadata=version_data.get("metadata", {}),
            user_id=user.get("user_id") if user else None
        )
        
        return {
            "success": True,
            "message": f"New version created for model {model_id}",
            "version": {
                "version": new_version.version,
                "created_at": new_version.created_at.isoformat(),
                "metadata": new_version.metadata
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create model version for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create model version: {str(e)}")

@router.get("/models/{model_id}/billing")
async def get_model_billing_info(
    model_id: str,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    user = Depends(optional_auth)
):
    """Get billing information for a specific model"""
    try:
        from isa_model.core.models.model_billing_tracker import ModelBillingTracker
        from datetime import datetime, timedelta
        
        # Parse dates
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start_dt = datetime.now() - timedelta(days=30)
            
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            end_dt = datetime.now()
        
        billing_tracker = ModelBillingTracker()
        billing_info = billing_tracker.get_model_billing_summary(
            model_id=model_id,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return {
            "success": True,
            "model_id": model_id,
            "billing_period": {
                "start_date": start_dt.isoformat(),
                "end_date": end_dt.isoformat()
            },
            "billing_summary": billing_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get billing info for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get billing info: {str(e)}")

@router.put("/models/{model_id}/metadata")
async def update_model_metadata(
    model_id: str,
    metadata_update: Dict[str, Any],
    user = Depends(require_write_access)
):
    """Update metadata for a specific model"""
    try:
        from isa_model.core.models.model_repo import ModelRepo
        
        repo = ModelRepo()
        success = repo.update_model_metadata(
            model_id=model_id,
            metadata_updates=metadata_update,
            updated_by=user.get("user_id") if user else None
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        return {
            "success": True,
            "message": f"Metadata updated for model {model_id}",
            "updated_fields": list(metadata_update.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update metadata for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update metadata: {str(e)}")

@router.get("/models/{model_id}/statistics")
async def get_model_statistics(
    model_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    user = Depends(optional_auth)
):
    """Get usage statistics for a specific model"""
    try:
        from isa_model.core.models.model_statistics_tracker import ModelStatisticsTracker
        
        stats_tracker = ModelStatisticsTracker()
        statistics = stats_tracker.get_model_statistics(
            model_id=model_id,
            days=days
        )
        
        return {
            "success": True,
            "model_id": model_id,
            "period_days": days,
            "statistics": statistics
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model statistics: {str(e)}")