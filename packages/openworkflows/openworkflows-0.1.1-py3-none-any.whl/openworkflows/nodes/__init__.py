"""Built-in nodes for OpenWorkflows."""

from openworkflows.nodes.input import InputNode
from openworkflows.nodes.output import OutputNode
from openworkflows.nodes.transform import TemplateNode, TransformNode, MergeNode
from openworkflows.nodes.audio import TranscribeAudioNode, TranscribeAudioBatchNode

__all__ = [
    "InputNode",
    "OutputNode",
    "TemplateNode",
    "TransformNode",
    "MergeNode",
    "TranscribeAudioNode",
    "TranscribeAudioBatchNode",
]
