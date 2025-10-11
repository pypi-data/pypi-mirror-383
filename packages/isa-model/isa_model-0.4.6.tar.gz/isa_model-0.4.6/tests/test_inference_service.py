#!/usr/bin/env python
"""
Simple Integration Tests for All ISA Model Services

Tests all services documented in docs/services/ using ISAModelClient with real data
"""

import asyncio
from isa_model.client import ISAModelClient

# Initialize Client
client = ISAModelClient()


async def test_llm_service():
    """Test LLM service - docs/services/llm.md"""
    print("\n" + "="*60)
    print("🧪 Testing LLM Service")
    print("="*60)

    # Test simple chat - disable streaming for immediate response
    result = await client.invoke(
        "What is 2+2? Answer in one sentence.",
        "chat",
        "text",
        stream=False  # Disable streaming to get result directly
    )

    # Check if request was successful
    if not result.get("success", False):
        print(f"❌ LLM Error: {result.get('error', 'Unknown error')}")
        raise AssertionError(f"LLM service failed: {result.get('error')}")

    print(f"✅ Chat: {result['result'][:100]}")
    assert result["result"]


async def test_vision_service():
    """Test Vision service - docs/services/vision.md"""
    print("\n" + "="*60)
    print("👁️  Testing Vision Service")
    print("="*60)

    # Test image analysis - use a reliable, direct image URL
    # Using a stable image from a CDN
    image_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"

    result = await client.invoke(
        input_data=image_url,  # Pass URL directly, not in a dict
        task="analyze",
        service_type="vision",
        prompt="Describe this image in one sentence"  # Prompt as kwarg
    )

    # Check if request was successful
    if not result.get("success", False):
        print(f"❌ Vision Error: {result.get('error', 'Unknown error')}")
        raise AssertionError(f"Vision service failed: {result.get('error')}")

    # Vision returns a dict with 'text' key
    vision_result = result['result']
    if isinstance(vision_result, dict):
        text_result = vision_result.get('text', str(vision_result))
    else:
        text_result = str(vision_result)

    print(f"✅ Vision: {text_result[:100]}")
    assert text_result


async def test_image_generation_service():
    """Test Image Generation service - docs/services/image-generation.md"""
    print("\n" + "="*60)
    print("🎨 Testing Image Generation Service")
    print("="*60)

    result = await client.invoke(
        "A minimalist logo of a robot",
        "generate",  # Changed from "image_generation" to "generate"
        "image"
    )
    print(f"✅ Image Generated: {str(result['result'])[:100]}")
    assert result["result"]


async def test_audio_tts_service():
    """Test Audio TTS service - docs/services/audio.md"""
    print("\n" + "="*60)
    print("🔊 Testing Audio TTS Service")
    print("="*60)

    # Use OpenAI TTS (default) as per docs
    result = await client.invoke(
        "Hello, this is a test",
        "synthesize",
        "audio",
        provider="openai",  # Explicitly use OpenAI for TTS
        voice="nova"        # OpenAI voice
    )

    # Check if request was successful
    if not result.get("success", False):
        print(f"❌ TTS Error: {result.get('error', 'Unknown error')}")
        raise AssertionError(f"TTS service failed: {result.get('error')}")

    # Result contains audio_data_base64 (not audio_data as in docs)
    audio_result = result['result']
    if isinstance(audio_result, dict):
        audio_data = audio_result.get('audio_data_base64', audio_result.get('audio_data', audio_result.get('audio', '')))
    else:
        audio_data = audio_result

    print(f"✅ TTS Generated: {len(str(audio_data))} bytes")
    assert audio_data, "Audio data is empty"


async def test_audio_stt_service():
    """Test Audio STT service - docs/services/audio.md"""
    print("\n" + "="*60)
    print("🎤 Testing Audio STT Service")
    print("="*60)

    # First generate audio with OpenAI TTS, then transcribe it
    tts_result = await client.invoke(
        "Testing speech to text",
        "synthesize",
        "audio",
        provider="openai",  # Use OpenAI for TTS
        voice="nova"
    )

    # Save to temp file - handle dict result
    import tempfile
    import os
    import base64

    # Extract audio data from result (key is audio_data_base64, not audio_data)
    if isinstance(tts_result['result'], dict):
        audio_data = tts_result['result'].get('audio_data_base64', tts_result['result'].get('audio_data', ''))
        # Decode base64 if it's a string
        if isinstance(audio_data, str) and audio_data:
            audio_bytes = base64.b64decode(audio_data)
        else:
            audio_bytes = audio_data
    else:
        audio_bytes = tts_result['result']

    # OpenAI TTS returns different format, save as proper audio file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(audio_bytes)
        audio_path = f.name

    try:
        # Use OpenAI Whisper for STT (default, but explicit is better)
        result = await client.invoke(
            audio_path,
            "transcribe",
            "audio",
            provider="openai",  # Explicitly use OpenAI Whisper
            model="whisper-1"
        )

        # Check if request was successful
        if not result.get("success", False):
            print(f"❌ STT Error: {result.get('error', 'Unknown error')}")
            raise AssertionError(f"STT service failed: {result.get('error')}")

        # According to docs: result["result"]["text"]
        stt_result = result['result']
        if isinstance(stt_result, dict):
            text_result = stt_result.get('text', stt_result.get('transcription', ''))
        else:
            text_result = stt_result

        print(f"✅ STT Result: {text_result}")
        assert text_result, "Transcription is empty"
    finally:
        os.unlink(audio_path)


async def test_embedding_service():
    """Test Embedding service - docs/services/embedding.md"""
    print("\n" + "="*60)
    print("📊 Testing Embedding Service")
    print("="*60)

    # Test single embedding
    result = await client.invoke(
        "Machine learning is fascinating",
        "embed",  # Changed from "embedding" to "embed"
        "embedding"
    )
    vector = result["result"]
    print(f"✅ Embedding: {len(vector)} dimensions")
    assert isinstance(vector, list)
    assert len(vector) > 0


async def run_all_tests():
    """Run all service tests"""
    print("\n" + "="*60)
    print("🚀 ISA Model Service Integration Tests")
    print("="*60)

    tests = [
        test_llm_service,
        test_vision_service,
        test_image_generation_service,
        test_audio_tts_service,
        test_audio_stt_service,
        test_embedding_service
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"❌ Test Failed: {test.__name__}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
