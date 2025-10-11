"""Audio processing nodes for transcription."""

from typing import Dict, Any, Optional, List, Union
import os

from openworkflows.node import Node
from openworkflows.context import ExecutionContext
from openworkflows.parameters import Parameter


class TranscribeAudioNode(Node):
    """Node that transcribes audio files using Whisper via insanely-fast-whisper.

    This node uses OpenAI's Whisper models for speech-to-text transcription,
    optimized for speed using insanely-fast-whisper library.

    Parameters:
        model_name: Whisper model size (default: openai/whisper-large-v3)
        batch_size: Batch size for inference (default: 24)
        timestamps: Whether to return word-level timestamps (default: False)
        language: Target language code (e.g., "en", "es", "fr", None for auto-detect)
        task: Task type - "transcribe" or "translate" (default: transcribe)
        device_id: CUDA device ID (default: 0)
    """

    inputs = {"audio_path": str}
    outputs = {"text": str, "chunks": Optional[List[Dict[str, Any]]]}
    tags = ["audio", "ml"]
    parameters = {
        "model_name": Parameter(
            name="model_name",
            type=str,
            default="openai/whisper-large-v3",
            required=False,
            description="Whisper model name (e.g., openai/whisper-large-v3, openai/whisper-medium)",
        ),
        "batch_size": Parameter(
            name="batch_size",
            type=int,
            default=24,
            required=False,
            description="Batch size for inference",
        ),
        "timestamps": Parameter(
            name="timestamps",
            type=bool,
            default=False,
            required=False,
            description="Whether to return word-level timestamps",
        ),
        "language": Parameter(
            name="language",
            type=Optional[str],
            default=None,
            required=False,
            description="Target language code (e.g., en, es, fr). None for auto-detect.",
        ),
        "task": Parameter(
            name="task",
            type=str,
            default="transcribe",
            required=False,
            description="Task type: 'transcribe' or 'translate'",
        ),
        "device_id": Parameter(
            name="device_id",
            type=int,
            default=0,
            required=False,
            description="CUDA device ID",
        ),
    }
    schema = {
        "label": {
            "en": "Transcribe Audio",
            "pl": "Transkrybuj Audio"
        },
        "description": {
            "en": "Convert speech in audio files to text using Whisper AI",
            "pl": "Konwertuj mowę w plikach audio na tekst używając Whisper AI"
        },
        "category": "audio",
        "icon": "🎤",
        "inputs": {
            "audio_path": {
                "label": {"en": "Audio File", "pl": "Plik Audio"},
                "description": {"en": "Path to audio file to transcribe", "pl": "Ścieżka do pliku audio do transkrypcji"},
                "placeholder": {"en": "/path/to/audio.mp3", "pl": "/sciezka/do/audio.mp3"}
            }
        },
        "outputs": {
            "text": {
                "label": {"en": "Transcription", "pl": "Transkrypcja"},
                "description": {"en": "Transcribed text from audio", "pl": "Transkrybowany tekst z audio"}
            },
            "chunks": {
                "label": {"en": "Chunks", "pl": "Fragmenty"},
                "description": {"en": "Timestamped text chunks", "pl": "Fragmenty tekstu z znacznikami czasu"}
            }
        },
        "parameters": {
            "model_name": {
                "label": {"en": "Model", "pl": "Model"},
                "description": {"en": "Whisper model to use", "pl": "Model Whisper do użycia"}
            },
            "batch_size": {
                "label": {"en": "Batch Size", "pl": "Rozmiar Partii"},
                "description": {"en": "Number of samples per batch", "pl": "Liczba próbek na partię"}
            },
            "timestamps": {
                "label": {"en": "Include Timestamps", "pl": "Dołącz Znaczniki Czasu"},
                "description": {"en": "Return word-level timestamps", "pl": "Zwróć znaczniki czasu dla każdego słowa"}
            },
            "language": {
                "label": {"en": "Language", "pl": "Język"},
                "description": {"en": "Audio language (auto-detect if empty)", "pl": "Język audio (automatyczne wykrywanie jeśli puste)"},
                "placeholder": {"en": "en, pl, es...", "pl": "en, pl, es..."}
            },
            "task": {
                "label": {"en": "Task", "pl": "Zadanie"},
                "description": {"en": "Transcribe or translate to English", "pl": "Transkrybuj lub przetłumacz na angielski"}
            },
            "device_id": {
                "label": {"en": "Device ID", "pl": "ID Urządzenia"},
                "description": {"en": "GPU device ID", "pl": "ID urządzenia GPU"}
            }
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._pipeline = None
        self._model_name = None

    def _load_pipeline(self, model_name: str, device_id: int):
        """Lazy load the Whisper pipeline."""
        if self._pipeline is None or self._model_name != model_name:
            try:
                import torch
                from transformers import pipeline
            except ImportError:
                raise ImportError(
                    "transformers and torch are required for audio transcription. "
                    "Install with: pip install insanely-fast-whisper"
                )

            device = f"cuda:{device_id}" if torch.cuda.is_available() else "cpu"
            self._pipeline = pipeline(
                "automatic-speech-recognition",
                model=model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device=device,
            )
            self._model_name = model_name

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Transcribe audio file to text.

        Args:
            ctx: Execution context with audio_path input

        Returns:
            Dictionary with 'text' key containing transcription,
            and optionally 'chunks' key with word-level timing info

        Raises:
            FileNotFoundError: If audio file doesn't exist
            ImportError: If required dependencies are missing
        """
        audio_path = ctx.input("audio_path")
        model_name = self.param("model_name")
        batch_size = self.param("batch_size")
        return_timestamps = self.param("timestamps")
        language = self.param("language")
        task = self.param("task")
        device_id = self.param("device_id")

        # Validate audio file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load pipeline if needed
        self._load_pipeline(model_name, device_id)

        # Prepare generation kwargs
        generate_kwargs = {"task": task, "language": language} if language else {"task": task}

        # Transcribe with insanely-fast-whisper pipeline
        result = self._pipeline(
            audio_path,
            chunk_length_s=30,
            batch_size=batch_size,
            return_timestamps=return_timestamps,
            generate_kwargs=generate_kwargs,
        )

        output = {"text": result["text"]}

        # Add chunks if timestamps were requested
        if return_timestamps and "chunks" in result:
            output["chunks"] = result["chunks"]

        return output


class TranscribeAudioBatchNode(Node):
    """Node that transcribes multiple audio files in batch using Whisper.

    Parameters:
        model_name: Whisper model size (default: openai/whisper-large-v3)
        batch_size: Batch size for inference (default: 24)
        timestamps: Whether to return word-level timestamps (default: False)
        language: Target language code (e.g., "en", "es", "fr", None for auto-detect)
        task: Task type - "transcribe" or "translate" (default: transcribe)
        device_id: CUDA device ID (default: 0)
    """

    inputs = {"audio_paths": List[str]}
    outputs = {"transcriptions": List[Dict[str, Any]]}
    tags = ["audio", "ml"]
    parameters = {
        "model_name": Parameter(
            name="model_name",
            type=str,
            default="openai/whisper-large-v3",
            required=False,
            description="Whisper model name (e.g., openai/whisper-large-v3, openai/whisper-medium)",
        ),
        "batch_size": Parameter(
            name="batch_size",
            type=int,
            default=24,
            required=False,
            description="Batch size for inference",
        ),
        "timestamps": Parameter(
            name="timestamps",
            type=bool,
            default=False,
            required=False,
            description="Whether to return word-level timestamps",
        ),
        "language": Parameter(
            name="language",
            type=Optional[str],
            default=None,
            required=False,
            description="Target language code (e.g., en, es, fr). None for auto-detect.",
        ),
        "task": Parameter(
            name="task",
            type=str,
            default="transcribe",
            required=False,
            description="Task type: 'transcribe' or 'translate'",
        ),
        "device_id": Parameter(
            name="device_id",
            type=int,
            default=0,
            required=False,
            description="CUDA device ID",
        ),
    }
    schema = {
        "label": {
            "en": "Transcribe Audio Batch",
            "pl": "Transkrybuj Partię Audio"
        },
        "description": {
            "en": "Transcribe multiple audio files at once using Whisper AI",
            "pl": "Transkrybuj wiele plików audio jednocześnie używając Whisper AI"
        },
        "category": "audio",
        "icon": "🎙️",
        "inputs": {
            "audio_paths": {
                "label": {"en": "Audio Files", "pl": "Pliki Audio"},
                "description": {"en": "List of audio file paths to transcribe", "pl": "Lista ścieżek plików audio do transkrypcji"}
            }
        },
        "outputs": {
            "transcriptions": {
                "label": {"en": "Transcriptions", "pl": "Transkrypcje"},
                "description": {"en": "List of transcriptions with text and metadata", "pl": "Lista transkrypcji z tekstem i metadanymi"}
            }
        },
        "parameters": {
            "model_name": {
                "label": {"en": "Model", "pl": "Model"},
                "description": {"en": "Whisper model to use", "pl": "Model Whisper do użycia"}
            },
            "batch_size": {
                "label": {"en": "Batch Size", "pl": "Rozmiar Partii"},
                "description": {"en": "Number of samples per batch", "pl": "Liczba próbek na partię"}
            },
            "timestamps": {
                "label": {"en": "Include Timestamps", "pl": "Dołącz Znaczniki Czasu"},
                "description": {"en": "Return word-level timestamps", "pl": "Zwróć znaczniki czasu dla każdego słowa"}
            },
            "language": {
                "label": {"en": "Language", "pl": "Język"},
                "description": {"en": "Audio language (auto-detect if empty)", "pl": "Język audio (automatyczne wykrywanie jeśli puste)"}
            },
            "task": {
                "label": {"en": "Task", "pl": "Zadanie"},
                "description": {"en": "Transcribe or translate to English", "pl": "Transkrybuj lub przetłumacz na angielski"}
            },
            "device_id": {
                "label": {"en": "Device ID", "pl": "ID Urządzenia"},
                "description": {"en": "GPU device ID", "pl": "ID urządzenia GPU"}
            }
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._pipeline = None
        self._model_name = None

    def _load_pipeline(self, model_name: str, device_id: int):
        """Lazy load the Whisper pipeline."""
        if self._pipeline is None or self._model_name != model_name:
            try:
                import torch
                from transformers import pipeline
            except ImportError:
                raise ImportError(
                    "transformers and torch are required for audio transcription. "
                    "Install with: pip install insanely-fast-whisper"
                )

            device = f"cuda:{device_id}" if torch.cuda.is_available() else "cpu"
            self._pipeline = pipeline(
                "automatic-speech-recognition",
                model=model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device=device,
            )
            self._model_name = model_name

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Transcribe multiple audio files in batch.

        Args:
            ctx: Execution context with audio_paths input

        Returns:
            Dictionary with 'transcriptions' key containing list of results,
            each with 'text', 'audio_path', and optional 'chunks' keys

        Raises:
            FileNotFoundError: If any audio file doesn't exist
            ImportError: If required dependencies are missing
        """
        audio_paths = ctx.input("audio_paths")
        model_name = self.param("model_name")
        batch_size = self.param("batch_size")
        return_timestamps = self.param("timestamps")
        language = self.param("language")
        task = self.param("task")
        device_id = self.param("device_id")

        # Validate all files exist
        for path in audio_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Audio file not found: {path}")

        # Load pipeline if needed
        self._load_pipeline(model_name, device_id)

        # Prepare generation kwargs
        generate_kwargs = {"task": task, "language": language} if language else {"task": task}

        # Transcribe all files
        transcriptions = []
        for audio_path in audio_paths:
            result = self._pipeline(
                audio_path,
                chunk_length_s=30,
                batch_size=batch_size,
                return_timestamps=return_timestamps,
                generate_kwargs=generate_kwargs,
            )

            output = {
                "text": result["text"],
                "audio_path": audio_path,
            }

            if return_timestamps and "chunks" in result:
                output["chunks"] = result["chunks"]

            transcriptions.append(output)

        return {"transcriptions": transcriptions}
