"""Pytest configuration and fixtures for OpenWorkflows tests."""

import pytest
from typing import Dict, Any

from openworkflows import Workflow, Node, ExecutionContext, register_node, MockLLMProvider


@pytest.fixture
def mock_llm_provider():
    """Fixture for mock LLM provider."""
    return MockLLMProvider("Mock LLM response for testing")


@pytest.fixture
def workflow():
    """Fixture for a basic workflow."""
    return Workflow("Test Workflow")


# Test nodes for advanced scenarios
@register_node("add")
class AddNode(Node):
    """Node that adds two numbers."""

    inputs = {"a": float, "b": float}
    outputs = {"result": float}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        a = ctx.input("a", 0)
        b = ctx.input("b", 0)
        return {"result": float(a) + float(b)}


@register_node("multiply")
class MultiplyNode(Node):
    """Node that multiplies two numbers."""

    inputs = {"a": float, "b": float}
    outputs = {"result": float}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        a = ctx.input("a", 1)
        b = ctx.input("b", 1)
        return {"result": float(a) * float(b)}


@register_node("conditional")
class ConditionalNode(Node):
    """Node that routes based on a condition."""

    inputs = {"value": float}
    outputs = {"high": float, "low": float, "result": float}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        value = ctx.input("value", 0)
        # Threshold can come from config or input, with default of 10
        threshold = ctx.input("threshold")
        if threshold is None:
            threshold = self.config.get("threshold", 10)

        if value > threshold:
            return {"high": value, "low": 0, "result": value}
        else:
            return {"high": 0, "low": value, "result": value}


@register_node("split")
class SplitNode(Node):
    """Node that splits input into multiple outputs."""

    inputs = {"value": Any}
    outputs = {"out1": Any, "out2": Any, "out3": Any}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        value = ctx.input("value")
        return {"out1": value, "out2": value, "out3": value}


@register_node("merge_sum")
class MergeSumNode(Node):
    """Node that sums all inputs."""

    inputs = {"input1": float, "input2": float, "input3": float}
    outputs = {"result": float}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        total = 0
        for i in range(1, 4):
            val = ctx.input(f"input{i}")
            if val is not None:
                total += float(val)
        return {"result": total}


@register_node("passthrough")
class PassthroughNode(Node):
    """Node that passes input to output unchanged."""

    inputs = {"input": Any}
    outputs = {"output": Any}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        value = ctx.input("input")
        return {"output": value}


@register_node("counter")
class CounterNode(Node):
    """Node that counts how many times it's been executed."""

    outputs = {"count": int}

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.execution_count = 0

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        self.execution_count += 1
        return {"count": self.execution_count}
