"""Input node for receiving workflow inputs."""

from typing import Dict, Any

from openworkflows.node import Node
from openworkflows.context import ExecutionContext


class InputNode(Node):
    """Node that provides input values to the workflow.

    Config:
        name: The name of the input variable to retrieve
        default: Optional default value if input not provided
    """

    outputs = {"value": Any}
    tags = ["io", "core"]
    schema = {
        "label": {
            "en": "Input",
            "pl": "Wejście"
        },
        "description": {
            "en": "Provides input values to the workflow from external sources",
            "pl": "Dostarcza wartości wejściowe do przepływu pracy z zewnętrznych źródeł"
        },
        "category": "io",
        "icon": "📥",
        "outputs": {
            "value": {
                "label": {"en": "Value", "pl": "Wartość"},
                "description": {"en": "The input value", "pl": "Wartość wejściowa"}
            }
        }
    }

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Get input value from workflow inputs.

        Args:
            ctx: Execution context

        Returns:
            Dictionary with 'value' key containing the input
        """
        input_name = self.config.get("name", "input")
        default = self.config.get("default")

        value = ctx.workflow_inputs.get(input_name, default)

        return {"value": value}
