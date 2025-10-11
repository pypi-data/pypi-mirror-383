# Multilingual Node Schema Implementation

## Summary

Added optional multilingual schema support to OpenWorkflows for frontend rendering. The system is simple, non-intrusive, and uses plain Python dictionaries.

## Changes Made

### 1. Core Infrastructure

**`openworkflows/node.py`**
- Added optional `schema: Optional[Dict[str, Any]] = None` attribute to `Node` base class
- No breaking changes - all existing nodes work without modification

**`openworkflows/registry.py`**
- Added `get_node_info(name: str)` function to export node metadata including schema
- Returns dict with: type, inputs, outputs, parameters, tags, and schema

### 2. Schema Structure

Simple dictionary format with multilingual strings:

```python
schema = {
    "label": {"en": "Node Name", "pl": "Nazwa Węzła"},
    "description": {"en": "Description...", "pl": "Opis..."},
    "category": "category_name",  # For grouping in UI
    "icon": "🔤",  # Emoji or icon identifier

    "inputs": {
        "handle_name": {
            "label": {"en": "Input", "pl": "Wejście"},
            "description": {"en": "...", "pl": "..."},
            "placeholder": {"en": "...", "pl": "..."}
        }
    },

    "outputs": {
        "handle_name": {
            "label": {"en": "Output", "pl": "Wyjście"},
            "description": {"en": "...", "pl": "..."}
        }
    },

    "parameters": {
        "param_name": {
            "label": {"en": "Parameter", "pl": "Parametr"},
            "description": {"en": "...", "pl": "..."},
            "choices": {  # For choice parameters
                "value1": {"en": "Label 1", "pl": "Etykieta 1"}
            }
        }
    }
}
```

### 3. Nodes with Schemas

Added English and Polish translations to all built-in nodes:

- ✅ **InputNode** (`input`) - 📥
- ✅ **OutputNode** (`output`) - 📤
- ✅ **TemplateNode** (`template`) - 📝
- ✅ **TransformNode** (`transform`) - 🔄
- ✅ **MergeNode** (`merge`) - 🔗
- ✅ **GenerateTextNode** (`generate_text`) - 🤖
- ✅ **HTTPRequestNode** (`http_request`) - 🌐
- ✅ **HTTPGetNode** (`http_get`) - ⬇️
- ✅ **HTTPPostNode** (`http_post`) - ⬆️
- ✅ **TranscribeAudioNode** (`transcribe_audio`) - 🎤
- ✅ **TranscribeAudioBatchNode** (`transcribe_audio_batch`) - 🎙️

## Usage Examples

### Getting Node Info for Frontend

```python
from openworkflows import registry

# Get single node info
info = registry.get_node_info("transform")
print(info["schema"]["label"]["pl"])  # "Przekształć"
print(info["schema"]["icon"])  # "🔄"

# Get all nodes
all_nodes = registry.list_nodes()
for node_name in all_nodes:
    info = registry.get_node_info(node_name)
    if info and info.get("schema"):
        label = info["schema"]["label"]["en"]
        print(f"{node_name}: {label}")
```

### Creating Custom Node with Schema

```python
from openworkflows import Node, register_node

@register_node("my_node")
class MyNode(Node):
    inputs = {"text": str}
    outputs = {"result": str}

    schema = {
        "label": {
            "en": "My Custom Node",
            "pl": "Mój Własny Węzeł"
        },
        "description": {
            "en": "Does something cool",
            "pl": "Robi coś fajnego"
        },
        "category": "custom",
        "icon": "⚡",
        "inputs": {
            "text": {
                "label": {"en": "Input Text", "pl": "Tekst Wejściowy"}
            }
        },
        "outputs": {
            "result": {
                "label": {"en": "Result", "pl": "Wynik"}
            }
        }
    }

    async def execute(self, ctx):
        return {"result": ctx.input("text").upper()}
```

## Testing

Run the test script to see the implementation in action:

```bash
uv run python test_schema.py
```

This displays:
- Node metadata with schemas
- Multilingual labels (EN/PL)
- Icons and categories
- Complete list of all registered nodes

## Benefits

✅ **Non-intrusive** - Optional, no breaking changes
✅ **Simple** - Plain dicts, no complex classes
✅ **Flexible** - Add only what you need
✅ **Extensible** - Easy to add more languages
✅ **Frontend-friendly** - Direct JSON serialization

## Frontend Integration

The frontend can:
1. Call `get_node_info()` to get node metadata
2. Use the `schema` dict for rendering
3. Implement fallback logic for missing translations
4. Auto-generate labels from handle names if schema is missing

## Future Enhancements

- Add more languages (ES, FR, DE, etc.)
- Add `examples` field for usage examples
- Add `tags` field with multilingual labels
- Add validation schemas for frontend form generation
