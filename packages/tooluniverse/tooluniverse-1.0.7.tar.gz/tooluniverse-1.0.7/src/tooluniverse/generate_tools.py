#!/usr/bin/env python3
"""Minimal tools generator - one tool, one file."""

from pathlib import Path
from typing import Dict, Any


def json_type_to_python(json_type: str) -> str:
    """Convert JSON type to Python type."""
    return {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list[Any]",
        "object": "dict[str, Any]",
    }.get(json_type, "Any")


def generate_tool_file(tool_name: str, tool_config: Dict[str, Any], output_dir: Path):
    """Generate one file for one tool."""
    schema = tool_config.get("parameter", {}) or {}
    description = tool_config.get("description", f"Execute {tool_name}")
    # Wrap long descriptions
    if len(description) > 100:
        description = description[:97] + "..."
    properties = schema.get("properties", {}) or {}
    required = schema.get("required", []) or []

    # Build parameters - required first, then optional
    required_params = []
    optional_params = []
    kwargs = []
    doc_params = []
    mutable_defaults_code = []

    for name, prop in properties.items():
        py_type = json_type_to_python(prop.get("type", "string"))
        desc = prop.get("description", "")

        if name in required:
            required_params.append(f"{name}: {py_type}")
        else:
            default = prop.get("default")
            if default is not None:
                # Handle mutable defaults to avoid B006 linting error
                if isinstance(default, (list, dict)):
                    # Use None as default and handle in function body
                    optional_params.append(f"{name}: Optional[{py_type}] = None")
                    mutable_defaults_code.append(
                        f"    if {name} is None:\n        {name} = {repr(default)}"
                    )
                else:
                    optional_params.append(
                        f"{name}: Optional[{py_type}] = {repr(default)}"
                    )
            else:
                optional_params.append(f"{name}: Optional[{py_type}] = None")

        kwargs.append(f'"{name}": {name}')
        # Wrap long descriptions
        if len(desc) > 80:
            desc = desc[:77] + "..."
        doc_params.append(f"    {name} : {py_type}\n        {desc}")

    # Combine required and optional parameters
    params = required_params + optional_params

    params_str = ",\n    ".join(params) if params else ""
    kwargs_str = ",\n                ".join(kwargs) if kwargs else ""
    doc_params_str = "\n".join(doc_params) if doc_params else "    No parameters"
    mutable_defaults_str = (
        "\n".join(mutable_defaults_code) if mutable_defaults_code else ""
    )

    # Infer return type
    return_schema = tool_config.get("return_schema", {})
    return_type = (
        json_type_to_python(return_schema.get("type", "")) if return_schema else "Any"
    )

    content = f'''"""
{tool_name}

{description}
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def {tool_name}(
    {params_str}{"," if params_str else ""}
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> {return_type}:
    """
    {description}

    Parameters
    ----------
{doc_params_str}
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    {return_type}
    """
    # Handle mutable defaults to avoid B006 linting error
{mutable_defaults_str}
    return get_shared_client().run_one_function(
        {{
            "name": "{tool_name}",
            "arguments": {{
                {kwargs_str}
            }}
        }},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate
    )


__all__ = ["{tool_name}"]
'''

    (output_dir / f"{tool_name}.py").write_text(content)


def generate_init(tool_names: list, output_dir: Path):
    """Generate __init__.py with all imports."""
    imports = [f"from .{name} import {name}" for name in sorted(tool_names)]

    # Generate the content without f-string escape sequences
    all_names = ",\n    ".join(f'"{name}"' for name in sorted(tool_names))
    content = f'''"""
ToolUniverse Tools

Type-safe Python interface to {len(tool_names)} scientific tools.
Each tool is in its own module for minimal import overhead.

Usage:
    from tooluniverse.tools import ArXiv_search_papers
    result = ArXiv_search_papers(query="machine learning")
"""

# Import exceptions from main package
from tooluniverse.exceptions import *

# Import shared client utilities
from ._shared_client import get_shared_client, reset_shared_client

# Import all tools
{chr(10).join(imports)}

__all__ = [
    "get_shared_client",
    "reset_shared_client",
    {all_names}
]
'''

    (output_dir / "__init__.py").write_text(content)


def main():
    """Generate tools."""
    from tooluniverse import ToolUniverse

    print("🔧 Generating tools...")

    tu = ToolUniverse()
    tu.load_tools()

    output = Path("src/tooluniverse/tools")
    output.mkdir(parents=True, exist_ok=True)

    # Generate all tools
    for i, (tool_name, tool_config) in enumerate(tu.all_tool_dict.items(), 1):
        generate_tool_file(tool_name, tool_config, output)
        if i % 50 == 0:
            print(f"  Generated {i} tools...")

    # Generate __init__.py
    generate_init(list(tu.all_tool_dict.keys()), output)

    print(f"✅ Generated {len(tu.all_tool_dict)} tools in {output}")


if __name__ == "__main__":
    main()
