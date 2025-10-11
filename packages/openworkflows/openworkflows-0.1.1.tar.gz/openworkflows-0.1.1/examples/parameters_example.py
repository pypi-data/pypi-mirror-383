"""Parameters example - demonstrates using node parameters and creating custom parameters."""

import asyncio
from typing import Dict, Any
from openworkflows import Workflow, Node, ExecutionContext, register_node
from openworkflows.parameters import Parameter


@register_node("multiply")
class MultiplyNode(Node):
    """Custom node with a parameter."""

    inputs = {"value": float}
    outputs = {"result": float}
    parameters = {
        "factor": Parameter(
            name="factor",
            type=float,
            default=2.0,
            required=False,
            description="Multiplication factor",
        ),
    }

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        value = ctx.input("value")
        factor = self.param("factor")
        return {"result": value * factor}


async def main():
    # Create workflow
    workflow = Workflow("Parameters Example")

    # Add nodes - note the 'factor' parameter
    workflow.add_node("input", "input", {"name": "x"})
    workflow.add_node("multiply", "multiply", {"factor": 5.0})
    workflow.add_node("output", "output")

    # Connect nodes
    workflow.connect("input.value", "multiply.value")
    workflow.connect("multiply.result", "output.value")

    # Run workflow
    result = await workflow.run(inputs={"x": 3.0})
    print(result["output"]["result"])


if __name__ == "__main__":
    asyncio.run(main())
