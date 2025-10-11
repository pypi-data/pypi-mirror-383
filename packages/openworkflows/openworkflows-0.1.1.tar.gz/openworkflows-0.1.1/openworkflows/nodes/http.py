"""HTTP request nodes for making API calls."""

from typing import Dict, Any, Optional
import httpx
import json
import re

from openworkflows.node import Node
from openworkflows.context import ExecutionContext
from openworkflows.parameters import Parameter


class HTTPRequestNode(Node):
    """Node that makes HTTP requests with templated URL and body.

    Parameters:
        method: HTTP method (GET, POST, PUT, DELETE, PATCH) (required)
        url_template: URL template with {variable} placeholders (required)
        body_template: Request body template with {variable} placeholders (optional)
        headers: Additional headers as dict (optional)
        timeout: Request timeout in seconds (default: 30)
    """

    inputs = {"variables": Optional[Dict[str, Any]]}
    outputs = {
        "response": Dict[str, Any],
        "status_code": int,
        "body": Any,
        "headers": Dict[str, str],
    }
    tags = ["http", "network"]
    parameters = {
        "method": Parameter(
            name="method",
            type=str,
            required=True,
            description="HTTP method",
            choices=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        ),
        "url_template": Parameter(
            name="url_template",
            type=str,
            required=True,
            description="URL template with {variable} placeholders",
        ),
        "body_template": Parameter(
            name="body_template",
            type=str,
            required=False,
            description="Request body template with {variable} placeholders",
        ),
        "headers": Parameter(
            name="headers",
            type=dict,
            required=False,
            default={},
            description="Additional HTTP headers",
        ),
        "timeout": Parameter(
            name="timeout",
            type=int,
            required=False,
            default=30,
            description="Request timeout in seconds",
            validator=lambda x: x > 0 and x <= 300,
        ),
    }
    schema = {
        "label": {
            "en": "HTTP Request",
            "pl": "Żądanie HTTP"
        },
        "description": {
            "en": "Make HTTP requests to external APIs and services",
            "pl": "Wykonaj żądania HTTP do zewnętrznych API i usług"
        },
        "category": "network",
        "icon": "🌐",
        "inputs": {
            "variables": {
                "label": {"en": "Variables", "pl": "Zmienne"},
                "description": {"en": "Variables for URL and body templates", "pl": "Zmienne dla szablonów URL i treści"}
            }
        },
        "outputs": {
            "response": {
                "label": {"en": "Response", "pl": "Odpowiedź"},
                "description": {"en": "Full HTTP response object", "pl": "Pełny obiekt odpowiedzi HTTP"}
            },
            "status_code": {
                "label": {"en": "Status Code", "pl": "Kod Statusu"},
                "description": {"en": "HTTP status code (200, 404, etc.)", "pl": "Kod statusu HTTP (200, 404, itp.)"}
            },
            "body": {
                "label": {"en": "Body", "pl": "Treść"},
                "description": {"en": "Response body content", "pl": "Treść odpowiedzi"}
            },
            "headers": {
                "label": {"en": "Headers", "pl": "Nagłówki"},
                "description": {"en": "Response headers", "pl": "Nagłówki odpowiedzi"}
            }
        },
        "parameters": {
            "method": {
                "label": {"en": "HTTP Method", "pl": "Metoda HTTP"},
                "description": {"en": "HTTP request method", "pl": "Metoda żądania HTTP"},
                "choices": {
                    "GET": {"en": "GET - Retrieve data", "pl": "GET - Pobierz dane"},
                    "POST": {"en": "POST - Create resource", "pl": "POST - Utwórz zasób"},
                    "PUT": {"en": "PUT - Update resource", "pl": "PUT - Zaktualizuj zasób"},
                    "DELETE": {"en": "DELETE - Remove resource", "pl": "DELETE - Usuń zasób"},
                    "PATCH": {"en": "PATCH - Partial update", "pl": "PATCH - Częściowa aktualizacja"},
                    "HEAD": {"en": "HEAD - Get headers only", "pl": "HEAD - Pobierz tylko nagłówki"},
                    "OPTIONS": {"en": "OPTIONS - Get capabilities", "pl": "OPTIONS - Pobierz możliwości"}
                }
            },
            "url_template": {
                "label": {"en": "URL Template", "pl": "Szablon URL"},
                "description": {"en": "URL with {variable} placeholders", "pl": "URL z symbolami zastępczymi {zmienna}"},
                "placeholder": {"en": "https://api.example.com/{endpoint}", "pl": "https://api.example.com/{endpoint}"}
            },
            "body_template": {
                "label": {"en": "Body Template", "pl": "Szablon Treści"},
                "description": {"en": "Request body with {variable} placeholders", "pl": "Treść żądania z symbolami zastępczymi {zmienna}"},
                "placeholder": {"en": '{"key": "{value}"}', "pl": '{"klucz": "{wartosc}"}'}
            },
            "headers": {
                "label": {"en": "Headers", "pl": "Nagłówki"},
                "description": {"en": "Additional HTTP headers", "pl": "Dodatkowe nagłówki HTTP"}
            },
            "timeout": {
                "label": {"en": "Timeout", "pl": "Timeout"},
                "description": {"en": "Request timeout in seconds", "pl": "Timeout żądania w sekundach"}
            }
        }
    }

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Execute HTTP request with templated URL and body.

        Args:
            ctx: Execution context

        Returns:
            Dictionary with response data including status, body, headers
        """
        method = self.param("method")
        url_template = self.param("url_template")
        body_template = self.param("body_template")
        headers = self.param("headers", {})
        timeout = self.param("timeout")

        # Get variables from input or workflow inputs
        variables = ctx.input("variables", {})
        if not variables:
            variables = ctx.workflow_inputs

        # Fill URL template
        try:
            url = url_template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing URL template variable: {e}")

        # Fill body template if provided
        body = None
        if body_template:
            # Replace {variable} placeholders while preserving JSON structure
            def replace_var(match):
                var_name = match.group(1)
                if var_name not in variables:
                    raise ValueError(f"Missing body template variable: {var_name}")
                value = variables[var_name]
                # If value is string, return as-is for JSON string context
                # Otherwise serialize as JSON
                if isinstance(value, str):
                    return value
                return json.dumps(value)

            try:
                body = re.sub(r"\{(\w+)\}", replace_var, body_template)
            except ValueError as e:
                raise e

        # Make HTTP request
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, content=body, headers=headers)
            elif method == "PUT":
                response = await client.put(url, content=body, headers=headers)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            elif method == "PATCH":
                response = await client.patch(url, content=body, headers=headers)
            elif method == "HEAD":
                response = await client.head(url, headers=headers)
            elif method == "OPTIONS":
                response = await client.options(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        # Parse response body
        try:
            response_body = response.json()
        except Exception:
            response_body = response.text

        return {
            "response": {
                "status_code": response.status_code,
                "body": response_body,
                "headers": dict(response.headers),
            },
            "status_code": response.status_code,
            "body": response_body,
            "headers": dict(response.headers),
        }


class HTTPGetNode(Node):
    """Simplified HTTP GET node with URL template.

    Parameters:
        url_template: URL template with {variable} placeholders (required)
        headers: Additional headers as dict (optional)
        timeout: Request timeout in seconds (default: 30)
    """

    inputs = {"variables": Optional[Dict[str, Any]]}
    outputs = {
        "response": Dict[str, Any],
        "status_code": int,
        "body": Any,
        "headers": Dict[str, str],
    }
    tags = ["http", "network"]
    parameters = {
        "url_template": Parameter(
            name="url_template",
            type=str,
            required=True,
            description="URL template with {variable} placeholders",
        ),
        "headers": Parameter(
            name="headers",
            type=dict,
            required=False,
            default={},
            description="Additional HTTP headers",
        ),
        "timeout": Parameter(
            name="timeout",
            type=int,
            required=False,
            default=30,
            description="Request timeout in seconds",
            validator=lambda x: x > 0 and x <= 300,
        ),
    }
    schema = {
        "label": {
            "en": "HTTP GET",
            "pl": "HTTP GET"
        },
        "description": {
            "en": "Fetch data from a URL using HTTP GET method",
            "pl": "Pobierz dane z URL używając metody HTTP GET"
        },
        "category": "network",
        "icon": "⬇️",
        "inputs": {
            "variables": {
                "label": {"en": "Variables", "pl": "Zmienne"},
                "description": {"en": "Variables for URL template", "pl": "Zmienne dla szablonu URL"}
            }
        },
        "outputs": {
            "response": {
                "label": {"en": "Response", "pl": "Odpowiedź"},
                "description": {"en": "Full HTTP response", "pl": "Pełna odpowiedź HTTP"}
            },
            "status_code": {
                "label": {"en": "Status Code", "pl": "Kod Statusu"},
                "description": {"en": "HTTP status code", "pl": "Kod statusu HTTP"}
            },
            "body": {
                "label": {"en": "Body", "pl": "Treść"},
                "description": {"en": "Response body", "pl": "Treść odpowiedzi"}
            },
            "headers": {
                "label": {"en": "Headers", "pl": "Nagłówki"},
                "description": {"en": "Response headers", "pl": "Nagłówki odpowiedzi"}
            }
        },
        "parameters": {
            "url_template": {
                "label": {"en": "URL", "pl": "URL"},
                "description": {"en": "URL with {variable} placeholders", "pl": "URL z symbolami zastępczymi {zmienna}"},
                "placeholder": {"en": "https://api.example.com/data", "pl": "https://api.example.com/data"}
            },
            "headers": {
                "label": {"en": "Headers", "pl": "Nagłówki"},
                "description": {"en": "HTTP headers", "pl": "Nagłówki HTTP"}
            },
            "timeout": {
                "label": {"en": "Timeout", "pl": "Timeout"},
                "description": {"en": "Timeout in seconds", "pl": "Timeout w sekundach"}
            }
        }
    }

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Execute HTTP GET request.

        Args:
            ctx: Execution context

        Returns:
            Dictionary with response data
        """
        url_template = self.param("url_template")
        headers = self.param("headers", {})
        timeout = self.param("timeout")

        # Get variables from input or workflow inputs
        variables = ctx.input("variables", {})
        if not variables:
            variables = ctx.workflow_inputs

        # Fill URL template
        try:
            url = url_template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing URL template variable: {e}")

        # Make HTTP GET request
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers)

        # Parse response body
        try:
            response_body = response.json()
        except Exception:
            response_body = response.text

        return {
            "response": {
                "status_code": response.status_code,
                "body": response_body,
                "headers": dict(response.headers),
            },
            "status_code": response.status_code,
            "body": response_body,
            "headers": dict(response.headers),
        }


class HTTPPostNode(Node):
    """Simplified HTTP POST node with URL and body templates.

    Parameters:
        url_template: URL template with {variable} placeholders (required)
        body_template: Request body template with {variable} placeholders (required)
        headers: Additional headers as dict (optional)
        timeout: Request timeout in seconds (default: 30)
    """

    inputs = {"variables": Optional[Dict[str, Any]]}
    outputs = {
        "response": Dict[str, Any],
        "status_code": int,
        "body": Any,
        "headers": Dict[str, str],
    }
    tags = ["http", "network"]
    parameters = {
        "url_template": Parameter(
            name="url_template",
            type=str,
            required=True,
            description="URL template with {variable} placeholders",
        ),
        "body_template": Parameter(
            name="body_template",
            type=str,
            required=True,
            description="Request body template with {variable} placeholders",
        ),
        "headers": Parameter(
            name="headers",
            type=dict,
            required=False,
            default={},
            description="Additional HTTP headers",
        ),
        "timeout": Parameter(
            name="timeout",
            type=int,
            required=False,
            default=30,
            description="Request timeout in seconds",
            validator=lambda x: x > 0 and x <= 300,
        ),
    }
    schema = {
        "label": {
            "en": "HTTP POST",
            "pl": "HTTP POST"
        },
        "description": {
            "en": "Send data to a URL using HTTP POST method",
            "pl": "Wyślij dane do URL używając metody HTTP POST"
        },
        "category": "network",
        "icon": "⬆️",
        "inputs": {
            "variables": {
                "label": {"en": "Variables", "pl": "Zmienne"},
                "description": {"en": "Variables for URL and body templates", "pl": "Zmienne dla szablonów URL i treści"}
            }
        },
        "outputs": {
            "response": {
                "label": {"en": "Response", "pl": "Odpowiedź"},
                "description": {"en": "Full HTTP response", "pl": "Pełna odpowiedź HTTP"}
            },
            "status_code": {
                "label": {"en": "Status Code", "pl": "Kod Statusu"},
                "description": {"en": "HTTP status code", "pl": "Kod statusu HTTP"}
            },
            "body": {
                "label": {"en": "Body", "pl": "Treść"},
                "description": {"en": "Response body", "pl": "Treść odpowiedzi"}
            },
            "headers": {
                "label": {"en": "Headers", "pl": "Nagłówki"},
                "description": {"en": "Response headers", "pl": "Nagłówki odpowiedzi"}
            }
        },
        "parameters": {
            "url_template": {
                "label": {"en": "URL", "pl": "URL"},
                "description": {"en": "URL with {variable} placeholders", "pl": "URL z symbolami zastępczymi {zmienna}"},
                "placeholder": {"en": "https://api.example.com/create", "pl": "https://api.example.com/create"}
            },
            "body_template": {
                "label": {"en": "Body", "pl": "Treść"},
                "description": {"en": "Request body with {variable} placeholders", "pl": "Treść żądania z symbolami zastępczymi {zmienna}"},
                "placeholder": {"en": '{"name": "{name}"}', "pl": '{"nazwa": "{nazwa}"}'}
            },
            "headers": {
                "label": {"en": "Headers", "pl": "Nagłówki"},
                "description": {"en": "HTTP headers", "pl": "Nagłówki HTTP"}
            },
            "timeout": {
                "label": {"en": "Timeout", "pl": "Timeout"},
                "description": {"en": "Timeout in seconds", "pl": "Timeout w sekundach"}
            }
        }
    }

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Execute HTTP POST request.

        Args:
            ctx: Execution context

        Returns:
            Dictionary with response data
        """
        url_template = self.param("url_template")
        body_template = self.param("body_template")
        headers = self.param("headers", {})
        timeout = self.param("timeout")

        # Get variables from input or workflow inputs
        variables = ctx.input("variables", {})
        if not variables:
            variables = ctx.workflow_inputs

        # Fill URL template
        try:
            url = url_template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing URL template variable: {e}")

        # Fill body template
        # Replace {variable} placeholders while preserving JSON structure
        def replace_var(match):
            var_name = match.group(1)
            if var_name not in variables:
                raise ValueError(f"Missing body template variable: {var_name}")
            value = variables[var_name]
            # If value is string, return as-is for JSON string context
            # Otherwise serialize as JSON
            if isinstance(value, str):
                return value
            return json.dumps(value)

        try:
            body = re.sub(r"\{(\w+)\}", replace_var, body_template)
        except ValueError as e:
            raise e

        # Make HTTP POST request
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, content=body, headers=headers)

        # Parse response body
        try:
            response_body = response.json()
        except Exception:
            response_body = response.text

        return {
            "response": {
                "status_code": response.status_code,
                "body": response_body,
                "headers": dict(response.headers),
            },
            "status_code": response.status_code,
            "body": response_body,
            "headers": dict(response.headers),
        }
