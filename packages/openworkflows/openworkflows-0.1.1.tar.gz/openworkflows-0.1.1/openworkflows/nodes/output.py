"""Output node for collecting workflow outputs."""

from typing import Dict, Any

from openworkflows.node import Node
from openworkflows.context import ExecutionContext


class OutputNode(Node):
    """Node that collects output values from the workflow.

    Config:
        name: The name for this output (default: "output")
    """

    inputs = {"value": Any}
    outputs = {"result": Any}
    tags = ["io", "core"]
    schema = {
        "label": {
            "en": "Output",
            "pl": "Wyjście"
        },
        "description": {
            "en": "Collects and returns output values from the workflow",
            "pl": "Zbiera i zwraca wartości wyjściowe z przepływu pracy"
        },
        "category": "io",
        "icon": "📤",
        "inputs": {
            "value": {
                "label": {"en": "Value", "pl": "Wartość"},
                "description": {"en": "The value to output", "pl": "Wartość do wyprowadzenia"}
            }
        },
        "outputs": {
            "result": {
                "label": {"en": "Result", "pl": "Wynik"},
                "description": {"en": "The output result", "pl": "Wynik wyjściowy"}
            }
        }
    }

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Pass through the input value as output.

        Args:
            ctx: Execution context

        Returns:
            Dictionary with 'result' key containing the value
        """
        value = ctx.input("value")
        return {"result": value}
