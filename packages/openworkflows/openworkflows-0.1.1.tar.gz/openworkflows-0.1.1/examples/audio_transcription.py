"""Audio transcription example - demonstrates transcribing audio files with Whisper."""

import asyncio
from openworkflows import Workflow


async def main():
    # Create workflow
    workflow = Workflow("Audio Transcription")

    # Add nodes
    workflow.add_node("input", "input", {"name": "audio_file"})
    workflow.add_node("transcribe", "transcribe_audio", {"model_name": "openai/whisper-large-v3-turbo"})
    workflow.add_node("output", "output")

    # Connect nodes
    workflow.connect("input.value", "transcribe.audio_path")
    workflow.connect("transcribe.text", "output.value")

    # Run workflow (replace with your audio file path)
    result = await workflow.run(inputs={"audio_file": "audio.wav"})
    print(result["output"]["result"])


if __name__ == "__main__":
    asyncio.run(main())
