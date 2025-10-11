"""JSON export/import example - demonstrates saving and loading workflows."""

import asyncio
from openworkflows import Workflow


async def main():
    # Create workflow
    workflow = Workflow("Export Example")
    workflow.add_node("input", "input", {"name": "text"})
    workflow.add_node("uppercase", "transform", {"transform": "upper"})
    workflow.add_node("output", "output")
    workflow.connect("input.value", "uppercase.input")
    workflow.connect("uppercase.output", "output.value")

    # Export to JSON
    json_str = workflow.to_json()
    print("Exported JSON:")
    print(json_str)

    # Import from JSON
    imported = Workflow.from_json(json_str)

    # Verify it works
    result = await imported.run(inputs={"text": "hello"})
    print(f"\nResult: {result['output']['result']}")


if __name__ == "__main__":
    asyncio.run(main())
