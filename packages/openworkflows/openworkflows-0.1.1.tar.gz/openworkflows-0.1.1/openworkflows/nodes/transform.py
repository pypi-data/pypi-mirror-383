"""Transform nodes for data manipulation."""

from typing import Dict, Any, Optional, Literal

from openworkflows.node import Node
from openworkflows.context import ExecutionContext
from openworkflows.parameters import Parameter


class TemplateNode(Node):
    """Node that fills a template with values.

    Accepts any number of named inputs via wildcard matching.
    Connect inputs with names matching the template placeholders.

    Parameters:
        template: Template string with {variable} placeholders (required)
        strict: If True, raise error on missing variables (default: True)

    Example:
        Template: "Hello {name}, you are {age} years old"
        Connect: source1.output -> template.name
                 source2.output -> template.age
    """

    inputs = {"*": Optional[str]}  # Accept any input name
    outputs = {"text": str}
    tags = ["transform", "text"]
    parameters = {
        "template": Parameter(
            name="template",
            type=str,
            required=True,
            description="Template string with {variable} placeholders",
        ),
        "strict": Parameter(
            name="strict",
            type=bool,
            default=True,
            required=False,
            description="Raise error on missing variables",
        ),
    }
    schema = {
        "label": {
            "en": "Template",
            "pl": "Szablon"
        },
        "description": {
            "en": "Fill a text template with dynamic values using {variable} placeholders",
            "pl": "Wypełnij szablon tekstowy dynamicznymi wartościami używając symboli zastępczych {zmienna}"
        },
        "category": "text",
        "icon": "📝",
        "outputs": {
            "text": {
                "label": {"en": "Text", "pl": "Tekst"},
                "description": {"en": "Filled template text", "pl": "Wypełniony tekst szablonu"}
            }
        },
        "parameters": {
            "template": {
                "label": {"en": "Template", "pl": "Szablon"},
                "description": {"en": "Text template with {variable} placeholders", "pl": "Szablon tekstu z symbolami zastępczymi {zmienna}"},
                "placeholder": {"en": "Hello {name}!", "pl": "Witaj {imie}!"}
            },
            "strict": {
                "label": {"en": "Strict Mode", "pl": "Tryb Ścisły"},
                "description": {"en": "Raise error if variables are missing", "pl": "Zgłoś błąd jeśli brakuje zmiennych"}
            }
        }
    }

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Fill template with variables.

        Args:
            ctx: Execution context

        Returns:
            Dictionary with 'text' key containing filled template
        """
        template = self.param("template")
        strict = self.param("strict")

        # Get all connected inputs
        variables = ctx.all_inputs()

        # Fallback to workflow inputs if no inputs connected
        if not variables:
            variables = ctx.workflow_inputs

        try:
            filled = template.format(**variables)
        except KeyError as e:
            if strict:
                raise ValueError(f"Missing template variable: {e}")
            else:
                # Return template with unfilled variables
                filled = template

        return {"text": filled}


class TransformNode(Node):
    """Node that applies a transformation function to input.

    Parameters:
        transform: Name of built-in transform (required)

    Available transforms:
        - identity: Pass through unchanged
        - upper: Convert to uppercase
        - lower: Convert to lowercase
        - strip: Remove leading/trailing whitespace
        - length: Get length
        - str: Convert to string
        - int: Convert to integer
        - float: Convert to float
    """

    inputs = {"input": Any}
    outputs = {"output": Any}
    tags = ["transform"]
    parameters = {
        "transform": Parameter(
            name="transform",
            type=str,
            default="identity",
            required=False,
            description="Transformation to apply",
            choices=[
                "identity",
                "upper",
                "lower",
                "strip",
                "length",
                "str",
                "int",
                "float",
            ],
        ),
    }
    schema = {
        "label": {
            "en": "Transform",
            "pl": "Przekształć"
        },
        "description": {
            "en": "Apply transformations to data (text case, type conversion, etc.)",
            "pl": "Zastosuj przekształcenia do danych (wielkie/małe litery, konwersja typów, itp.)"
        },
        "category": "transform",
        "icon": "🔄",
        "inputs": {
            "input": {
                "label": {"en": "Input", "pl": "Wejście"},
                "description": {"en": "Value to transform", "pl": "Wartość do przekształcenia"}
            }
        },
        "outputs": {
            "output": {
                "label": {"en": "Output", "pl": "Wyjście"},
                "description": {"en": "Transformed value", "pl": "Przekształcona wartość"}
            }
        },
        "parameters": {
            "transform": {
                "label": {"en": "Transform Type", "pl": "Typ Przekształcenia"},
                "description": {"en": "Type of transformation to apply", "pl": "Typ przekształcenia do zastosowania"},
                "choices": {
                    "identity": {"en": "Identity (no change)", "pl": "Identyczność (bez zmian)"},
                    "upper": {"en": "UPPERCASE", "pl": "WIELKIE LITERY"},
                    "lower": {"en": "lowercase", "pl": "małe litery"},
                    "strip": {"en": "Strip whitespace", "pl": "Usuń białe znaki"},
                    "length": {"en": "Get length", "pl": "Pobierz długość"},
                    "str": {"en": "Convert to string", "pl": "Konwertuj na tekst"},
                    "int": {"en": "Convert to integer", "pl": "Konwertuj na liczbę całkowitą"},
                    "float": {"en": "Convert to decimal", "pl": "Konwertuj na liczbę dziesiętną"}
                }
            }
        }
    }

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Apply transformation to input.

        Args:
            ctx: Execution context

        Returns:
            Dictionary with 'output' key containing transformed value
        """
        value = ctx.input("input")
        transform_name = self.param("transform")

        # Built-in transforms
        transforms = {
            "identity": lambda x: x,
            "upper": lambda x: str(x).upper() if x else "",
            "lower": lambda x: str(x).lower() if x else "",
            "strip": lambda x: str(x).strip() if x else "",
            "length": lambda x: len(x) if x else 0,
            "str": lambda x: str(x),
            "int": lambda x: int(x),
            "float": lambda x: float(x),
        }

        transform_fn = transforms[transform_name]
        result = transform_fn(value)
        return {"output": result}


class MergeNode(Node):
    """Node that merges multiple inputs into a dictionary or list.

    Accepts any number of named inputs via wildcard matching.

    Parameters:
        mode: "dict" or "list" (default: "dict")

    Example:
        Connect: source1.output -> merge.value1
                 source2.output -> merge.value2
        Output (dict mode): {"value1": ..., "value2": ...}
        Output (list mode): [..., ...]
    """

    inputs = {"*": Any}  # Accept any input name, any type
    outputs = {"result": Any}
    tags = ["transform", "aggregation"]
    parameters = {
        "mode": Parameter(
            name="mode",
            type=str,
            default="dict",
            required=False,
            description="Output mode",
            choices=["dict", "list"],
        ),
    }
    schema = {
        "label": {
            "en": "Merge",
            "pl": "Scal"
        },
        "description": {
            "en": "Merge multiple inputs into a single dictionary or list",
            "pl": "Scal wiele wejść w jeden słownik lub listę"
        },
        "category": "transform",
        "icon": "🔗",
        "outputs": {
            "result": {
                "label": {"en": "Result", "pl": "Wynik"},
                "description": {"en": "Merged output", "pl": "Scalony wynik"}
            }
        },
        "parameters": {
            "mode": {
                "label": {"en": "Output Mode", "pl": "Tryb Wyjścia"},
                "description": {"en": "How to combine inputs", "pl": "Jak połączyć wejścia"},
                "choices": {
                    "dict": {"en": "Dictionary (with keys)", "pl": "Słownik (z kluczami)"},
                    "list": {"en": "List (values only)", "pl": "Lista (tylko wartości)"}
                }
            }
        }
    }

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Merge inputs.

        Args:
            ctx: Execution context

        Returns:
            Dictionary with 'result' key containing merged values
        """
        mode = self.param("mode")

        # Get all connected inputs
        collected = ctx.all_inputs()

        if mode == "list":
            result = list(collected.values())
        else:
            result = collected

        return {"result": result}
