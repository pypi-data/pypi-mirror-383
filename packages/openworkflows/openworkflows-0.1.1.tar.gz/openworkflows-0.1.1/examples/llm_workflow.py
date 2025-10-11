"""LLM workflow example - demonstrates using template and generate_text nodes."""

import asyncio
from openworkflows import Workflow


async def main():
    # Create workflow
    workflow = Workflow("LLM Example")

    # Add nodes
    workflow.add_node("input", "input", {"name": "topic"})
    workflow.add_node("template", "template", {"template": "Write a story about {topic}"})
    workflow.add_node("generate", "generate_text", {"provider": "openrouter", "model": "z-ai/glm-4.6"})
    workflow.add_node("output", "output")

    # Connect nodes
    workflow.connect("template.text", "generate.prompt")
    workflow.connect("generate.text", "output.value")

    # Run workflow
    result = await workflow.run(inputs={"topic": "dragons"})
    print(result["output"]["result"])


if __name__ == "__main__":
    asyncio.run(main())
