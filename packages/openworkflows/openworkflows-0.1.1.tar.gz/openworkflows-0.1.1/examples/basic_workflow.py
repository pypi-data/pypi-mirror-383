"""Basic workflow example - demonstrates creating and running a simple 3-node workflow."""

import asyncio
from openworkflows import Workflow


async def main():
    # Create workflow
    workflow = Workflow("Basic Example")

    # Add nodes
    workflow.add_node("input", "input", {"name": "text"})
    workflow.add_node("uppercase", "transform", {"transform": "upper"})
    workflow.add_node("output", "output")

    # Connect nodes
    workflow.connect("input.value", "uppercase.input")
    workflow.connect("uppercase.output", "output.value")

    # Run workflow
    result = await workflow.run(inputs={"text": "hello world"})
    print(result["output"]["result"])


if __name__ == "__main__":
    asyncio.run(main())
