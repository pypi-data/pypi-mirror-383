"""Schema export example - demonstrates exporting node schemas to JSON."""

import json
from openworkflows import get_all_node_schemas

# Get all node schemas
schemas = get_all_node_schemas()

# Print summary
print(f"Found {len(schemas)} node types\n")
for schema in schemas:
    print(f"{schema['type']}: {schema['name']}")

# Export to file
with open("node_schemas.json", "w") as f:
    json.dump(schemas, f, indent=2)

print("\nExported to node_schemas.json")
