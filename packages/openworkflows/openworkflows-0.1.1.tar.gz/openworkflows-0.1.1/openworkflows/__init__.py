"""OpenWorkflows - A simple, developer-friendly Python package for creating AI workflows."""

from openworkflows.workflow import Workflow
from openworkflows.node import Node, node
from openworkflows.context import ExecutionContext
from openworkflows.registry import register_node, get_node, create_node, list_nodes, get_node_info
from openworkflows.parameters import Parameter, ParameterSpec
from openworkflows.providers import LLMProvider, MockLLMProvider
from openworkflows.schema import get_node_schema, get_all_node_schemas
from openworkflows.nodes import (
    InputNode,
    OutputNode,
    TemplateNode,
    TransformNode,
    MergeNode,
    TranscribeAudioNode,
    TranscribeAudioBatchNode,
)
from openworkflows.nodes.http import HTTPRequestNode, HTTPGetNode, HTTPPostNode
from openworkflows.nodes.llm import GenerateTextNode

# Register built-in nodes
register_node("input")(InputNode)
register_node("output")(OutputNode)
register_node("template")(TemplateNode)
register_node("transform")(TransformNode)
register_node("merge")(MergeNode)

# Rregister LLM nodes

register_node("generate_text")(GenerateTextNode)

# Register HTTP nodes
register_node("http_request")(HTTPRequestNode)
register_node("http_get")(HTTPGetNode)
register_node("http_post")(HTTPPostNode)

# Register Audio nodes
register_node("transcribe_audio")(TranscribeAudioNode)
register_node("transcribe_audio_batch")(TranscribeAudioBatchNode)

__version__ = "0.1.0"

__all__ = [
    "Workflow",
    "Node",
    "node",
    "ExecutionContext",
    "register_node",
    "get_node",
    "create_node",
    "list_nodes",
    "get_node_info",
    "Parameter",
    "ParameterSpec",
    "LLMProvider",
    "MockLLMProvider",
    "get_node_schema",
    "get_all_node_schemas",
    "InputNode",
    "OutputNode",
    "TemplateNode",
    "TransformNode",
    "MergeNode",
    "GenerateTextNode",
    "HTTPRequestNode",
    "HTTPGetNode",
    "HTTPPostNode",
    "TranscribeAudioNode",
    "TranscribeAudioBatchNode",
]
