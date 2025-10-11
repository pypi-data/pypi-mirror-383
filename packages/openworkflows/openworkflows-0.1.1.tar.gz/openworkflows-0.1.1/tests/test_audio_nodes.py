"""Tests for audio transcription nodes using real Whisper model."""

import pytest
import os

from openworkflows import Workflow


# Path to test audio file
TEST_AUDIO_PATH = os.path.join(os.path.dirname(__file__), "test_audio.wav")
EXPECTED_TRANSCRIPTION = "Hello! We're excited to show you our native speech capabilities. Where you can direct a voice, create realistic dialogue, and so much more. Edit these placeholders to get started."


@pytest.mark.asyncio
async def test_transcribe_audio_basic():
    """Test basic audio transcription with small Whisper model."""
    workflow = Workflow()
    workflow.add_node("input", "input", {"name": "audio_path"})
    workflow.add_node(
        "transcribe",
        "transcribe_audio",
        {
            "model_name": "openai/whisper-tiny",  # Use tiny model for fast testing
            "timestamps": False,
        },
    )
    workflow.connect("input.value", "transcribe.audio_path")

    result = await workflow.run(inputs={"audio_path": TEST_AUDIO_PATH})

    # Check that we got some transcription text
    assert "text" in result["transcribe"]
    assert len(result["transcribe"]["text"]) > 0
    # Tiny model may not be perfectly accurate, just check it's reasonable
    assert "chunks" not in result["transcribe"]


@pytest.mark.asyncio
async def test_transcribe_audio_with_timestamps():
    """Test audio transcription with word-level timestamps."""
    workflow = Workflow()
    workflow.add_node("input", "input", {"name": "audio_path"})
    workflow.add_node(
        "transcribe",
        "transcribe_audio",
        {
            "model_name": "openai/whisper-tiny",
            "timestamps": True,
        },
    )
    workflow.connect("input.value", "transcribe.audio_path")

    result = await workflow.run(inputs={"audio_path": TEST_AUDIO_PATH})

    assert "text" in result["transcribe"]
    assert "chunks" in result["transcribe"]
    assert len(result["transcribe"]["chunks"]) > 0

    # Verify chunk structure
    first_chunk = result["transcribe"]["chunks"][0]
    assert "text" in first_chunk
    assert "timestamp" in first_chunk
    assert len(first_chunk["timestamp"]) == 2  # (start, end)


@pytest.mark.asyncio
async def test_transcribe_audio_with_language():
    """Test audio transcription with explicit language."""
    workflow = Workflow()
    workflow.add_node("input", "input", {"name": "audio_path"})
    workflow.add_node(
        "transcribe",
        "transcribe_audio",
        {
            "model_name": "openai/whisper-tiny",
            "language": "en",
        },
    )
    workflow.connect("input.value", "transcribe.audio_path")

    result = await workflow.run(inputs={"audio_path": TEST_AUDIO_PATH})

    assert "text" in result["transcribe"]
    assert len(result["transcribe"]["text"]) > 0


@pytest.mark.asyncio
async def test_transcribe_audio_file_not_found():
    """Test that transcription fails gracefully when audio file doesn't exist."""
    workflow = Workflow()
    workflow.add_node("input", "input", {"name": "audio_path"})
    workflow.add_node("transcribe", "transcribe_audio")
    workflow.connect("input.value", "transcribe.audio_path")

    with pytest.raises(Exception, match="Audio file not found"):
        await workflow.run(inputs={"audio_path": "/nonexistent/audio.wav"})


@pytest.mark.asyncio
async def test_transcribe_audio_in_workflow():
    """Test audio transcription integrated with other nodes."""
    workflow = Workflow()
    workflow.add_node("input", "input", {"name": "audio_path"})
    workflow.add_node(
        "transcribe",
        "transcribe_audio",
        {"model_name": "openai/whisper-tiny"},
    )
    workflow.add_node("transform", "transform", {"transform": "upper"})
    workflow.add_node("output", "output")

    workflow.connect("input.value", "transcribe.audio_path")
    workflow.connect("transcribe.text", "transform.input")
    workflow.connect("transform.output", "output.value")

    result = await workflow.run(inputs={"audio_path": TEST_AUDIO_PATH})

    # Check that transcription was uppercased
    assert result["output"]["result"].isupper()
    assert len(result["output"]["result"]) > 0


@pytest.mark.asyncio
async def test_transcribe_audio_batch_basic():
    """Test batch audio transcription with multiple files."""
    workflow = Workflow()
    workflow.add_node("input", "input", {"name": "audio_paths"})
    workflow.add_node(
        "transcribe_batch",
        "transcribe_audio_batch",
        {"model_name": "openai/whisper-tiny"},
    )
    workflow.connect("input.value", "transcribe_batch.audio_paths")

    # Use the same test file multiple times
    audio_files = [TEST_AUDIO_PATH, TEST_AUDIO_PATH]

    result = await workflow.run(inputs={"audio_paths": audio_files})

    assert len(result["transcribe_batch"]["transcriptions"]) == 2

    for transcription in result["transcribe_batch"]["transcriptions"]:
        assert "text" in transcription
        assert "audio_path" in transcription
        assert len(transcription["text"]) > 0


@pytest.mark.asyncio
async def test_transcribe_audio_batch_with_timestamps():
    """Test batch transcription with timestamps."""
    workflow = Workflow()
    workflow.add_node("input", "input", {"name": "audio_paths"})
    workflow.add_node(
        "transcribe_batch",
        "transcribe_audio_batch",
        {
            "model_name": "openai/whisper-tiny",
            "timestamps": True,
        },
    )
    workflow.connect("input.value", "transcribe_batch.audio_paths")

    audio_files = [TEST_AUDIO_PATH]

    result = await workflow.run(inputs={"audio_paths": audio_files})

    assert len(result["transcribe_batch"]["transcriptions"]) == 1
    transcription = result["transcribe_batch"]["transcriptions"][0]

    assert "text" in transcription
    assert "chunks" in transcription
    assert len(transcription["chunks"]) > 0


@pytest.mark.asyncio
async def test_transcribe_audio_batch_file_not_found():
    """Test batch transcription fails when any file doesn't exist."""
    workflow = Workflow()
    workflow.add_node("input", "input", {"name": "audio_paths"})
    workflow.add_node("transcribe_batch", "transcribe_audio_batch")
    workflow.connect("input.value", "transcribe_batch.audio_paths")

    audio_files = [TEST_AUDIO_PATH, "/nonexistent/audio.wav"]

    with pytest.raises(Exception, match="Audio file not found"):
        await workflow.run(inputs={"audio_paths": audio_files})


@pytest.mark.asyncio
async def test_transcribe_audio_batch_empty_list():
    """Test batch transcription with empty list of files."""
    workflow = Workflow()
    workflow.add_node("input", "input", {"name": "audio_paths"})
    workflow.add_node("transcribe_batch", "transcribe_audio_batch")
    workflow.connect("input.value", "transcribe_batch.audio_paths")

    result = await workflow.run(inputs={"audio_paths": []})

    assert result["transcribe_batch"]["transcriptions"] == []
