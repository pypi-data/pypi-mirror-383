"""Custom node example - demonstrates creating a custom node class."""

import asyncio
from typing import Dict, Any
from openworkflows import Workflow, Node, ExecutionContext, register_node


@register_node("reverse_text")
class ReverseTextNode(Node):
    """Reverses the input text."""

    inputs = {"text": str}
    outputs = {"reversed": str}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        text = ctx.input("text")
        return {"reversed": text[::-1]}


async def main():
    # Create workflow
    workflow = Workflow("Custom Node Example")

    # Add nodes
    workflow.add_node("input", "input", {"name": "text"})
    workflow.add_node("reverse", "reverse_text")
    workflow.add_node("output", "output")

    # Connect nodes
    workflow.connect("input.value", "reverse.text")
    workflow.connect("reverse.reversed", "output.value")

    # Run workflow
    result = await workflow.run(inputs={"text": "Hello World"})
    print(result["output"]["result"])


if __name__ == "__main__":
    asyncio.run(main())
