"""Quillmark MCP Server."""

import base64
import uuid
from typing import Any

import quillmark
from mcp.server import Server
from mcp.types import Prompt, PromptMessage, Resource, TextContent, Tool

from .models import (
    Artifact,
    Diagnostic,
    FieldSchema,
    QuillInfo,
    QuillListItem,
    RenderError,
    RenderSuccess,
    TemplateListItem,
    ValidationError,
    ValidationSuccess,
)
from .quill_loader import load_all_quills

# Load quills from tonguetoquill-collection
QUILLS = load_all_quills()

# Initialize Quillmark engine and register quills
QUILLMARK_ENGINE = quillmark.Quillmark()
for quill in QUILLS.values():
    QUILLMARK_ENGINE.register_quill(quill)

# Render cache: maps resource ID to (bytes, mime_type)
RENDER_CACHE: dict[str, tuple[bytes, str]] = {}
MAX_CACHE_SIZE = 50  # Maximum number of documents to cache

# Usage instructions prompt
USAGE_PROMPT = """You are a writing assistant that helps users draft, workshop, and render their documents.
Use the Quillmark markdown-parameterized typesetted document rendering tools to draft and render these documents.
Provide the user with creative and technical support.

1. User will prompt for a document to be drafted or rendered.
2. Call list_markdown_templates() to get a list of available markdown templates.
3. Suggest a markdown template to the user based on their prompt.
4. User will select a markdown template.
5. Call get_markdown_template(<template_name>) based on the user's selected markdown template.
    - Extract the <quill_name> from `QUILL: <quill_name>` in the returned markdown template's frontmatter.
6. Call get_quill_info(<quill_name>) based on the user's selected markdown template to learn about the quill's fields and usage.
7. Create and edit the markdown draft using the markdown template and quill information.
    - Ask the user for any missing information needed to complete the markdown draft.
    - Continuously improve the markdown draft based on user feedback.
8. After each revision, call render_document(<markdown_draft>) to render the markdown draft to PDF or SVG.
9. When the user is satisfied, offer to save the rendered file to their filesystem using save_rendered_file() with the resource_uri from the render response."""


def create_server() -> Server:
    """Create and configure the Quillmark MCP server."""
    server = Server("quillmark-mcp")

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """List available prompts."""
        return [
            Prompt(
                name="writing-assistant",
                description="Instructions for using Quillmark as a writing assistant",
                arguments=[],
            )
        ]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> PromptMessage:
        """Get a prompt by name."""
        if name == "writing-assistant":
            return PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=USAGE_PROMPT,
                ),
            )
        else:
            raise ValueError(f"Unknown prompt: {name}")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available MCP tools."""
        return [
            Tool(
                name="list_quills",
                description="List all registered Quill templates available on the server",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="get_quill_info",
                description="Get detailed information about a specific Quill template",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "quill_name": {
                            "type": "string",
                            "description": "Name of the Quill template",
                        }
                    },
                    "required": ["quill_name"],
                },
            ),
            Tool(
                name="get_markdown_template",
                description=(
                    "Get the markdown template content by template name "
                    "from list_markdown_templates"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "template_name": {
                            "type": "string",
                            "description": "Name of the template from list_markdown_templates",
                        }
                    },
                    "required": ["template_name"],
                },
            ),
            Tool(
                name="list_markdown_templates",
                description="List available markdown templates from the templates.json manifest",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="render_document",
                description="Render a markdown document to PDF or SVG",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "quill_name": {
                            "type": "string",
                            "description": "Quill name to use (optional if QUILL in frontmatter)",
                        },
                        "markdown": {
                            "type": "string",
                            "description": "Markdown content with frontmatter",
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["PDF", "SVG"],
                            "default": "PDF",
                            "description": "Output format",
                        },
                        "validate_only": {
                            "type": "boolean",
                            "default": False,
                            "description": "Only validate without rendering",
                        },
                    },
                    "required": ["markdown"],
                },
            ),
            Tool(
                name="validate_frontmatter",
                description="Validate frontmatter against a Quill's schema",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "quill_name": {
                            "type": "string",
                            "description": (
                                "Quill name for validation (optional if QUILL in frontmatter)"
                            ),
                        },
                        "markdown": {
                            "type": "string",
                            "description": "Markdown content with frontmatter",
                        },
                    },
                    "required": ["markdown"],
                },
            ),
            Tool(
                name="save_rendered_file",
                description=(
                    "Save a rendered document from cache to a local file. "
                    "Use the resource_uri from render_document response."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_uri": {
                            "type": "string",
                            "description": "Resource URI from render_document (e.g., quillmark://render/{uuid})",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Absolute path where the file should be saved",
                        },
                    },
                    "required": ["resource_uri", "file_path"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        if name == "list_quills":
            return await handle_list_quills(arguments)
        elif name == "get_quill_info":
            return await handle_get_quill_info(arguments)
        elif name == "get_markdown_template":
            return await handle_get_markdown_template(arguments)
        elif name == "list_markdown_templates":
            return await handle_list_markdown_templates(arguments)
        elif name == "render_document":
            return await handle_render_document(arguments)
        elif name == "validate_frontmatter":
            return await handle_validate_frontmatter(arguments)
        elif name == "save_rendered_file":
            return await handle_save_rendered_file(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List all cached rendered documents as resources."""
        resources = []
        for render_id, (artifact_bytes, mime_type) in RENDER_CACHE.items():
            # Create descriptive name based on mime type
            extension = "pdf" if mime_type == "application/pdf" else "svg"
            name = f"Rendered document ({extension})"
            
            resource = Resource(
                uri=f"quillmark://render/{render_id}",
                name=name,
                mimeType=mime_type,
            )
            resources.append(resource)
        return resources

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a cached rendered document resource."""
        # Convert AnyUrl to string if needed
        uri_str = str(uri)

        # Parse URI to extract render ID
        if not uri_str.startswith("quillmark://render/"):
            raise ValueError(f"Invalid resource URI: {uri_str}")

        render_id = uri_str.replace("quillmark://render/", "")
        
        # Check if resource exists
        if render_id not in RENDER_CACHE:
            raise ValueError(f"Resource not found: {uri}")
        
        # Get bytes and return as base64
        artifact_bytes, _ = RENDER_CACHE[render_id]
        return base64.b64encode(artifact_bytes).decode("utf-8")

    return server


async def handle_list_quills(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle list_quills tool call."""
    quills = []
    for quill in QUILLS.values():
        # Get metadata fields
        metadata = quill.metadata or {}
        item = QuillListItem(
            name=quill.name,
            backend=quill.backend,
            description=metadata.get("description"),
            tags=metadata.get("tags"),
        )
        quills.append(item)

    result = {"quills": [q.model_dump(exclude_none=True) for q in quills]}
    return [TextContent(type="text", text=str(result))]


async def handle_get_quill_info(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle get_quill_info tool call."""
    quill_name = arguments["quill_name"]

    if quill_name not in QUILLS:
        error = RenderError(
            error_type="InvalidQuillName",
            error_message=f"Quill '{quill_name}' not found",
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    quill = QUILLS[quill_name]
    metadata = quill.metadata or {}

    # Convert field_schemas to FieldSchema objects
    # field_schemas now have standardized structure with
    # 'type', 'description', 'required', 'example', 'default'
    fields = {
        name: FieldSchema(**schema) for name, schema in quill.field_schemas.items()
    }

    assert quill.backend is not None, "Quill backend should not be None"

    info = QuillInfo(
        name=quill.name,
        backend=quill.backend,
        glue=metadata.get("glue", "glue.typ"),
        example=quill.example,
        description=metadata.get("description"),
        author=metadata.get("author"),
        version=metadata.get("version"),
        tags=metadata.get("tags"),
        frontmatter_fields=fields,
    )

    return [TextContent(type="text", text=info.model_dump_json(exclude_none=True))]


async def handle_get_markdown_template(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle get_markdown_template tool call."""
    import json
    from pathlib import Path

    template_name = arguments["template_name"]

    # Get the templates.json file path
    package_dir = Path(__file__).parent.parent
    templates_json = package_dir / "tonguetoquill-collection" / "templates" / "templates.json"

    if not templates_json.exists():
        error = RenderError(
            error_type="TemplateNotFound",
            error_message="templates.json not found",
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    # Read and parse templates.json
    with open(templates_json) as f:
        templates_data = json.load(f)

    # Find the template by name
    template_info = None
    for t in templates_data:
        if t["name"] == template_name:
            template_info = t
            break

    if not template_info:
        error = RenderError(
            error_type="TemplateNotFound",
            error_message=f"Template '{template_name}' not found",
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    # Read the template file
    template_file = package_dir / "tonguetoquill-collection" / "templates" / template_info["file"]
    if not template_file.exists():
        error = RenderError(
            error_type="TemplateFileNotFound",
            error_message=f"Template file '{template_info['file']}' not found",
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    with open(template_file) as f:
        template_content = f.read()

    result = {
        "template_name": template_name,
        "markdown": template_content,
    }

    return [TextContent(type="text", text=str(result))]


async def handle_list_markdown_templates(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle list_markdown_templates tool call."""
    import json
    from pathlib import Path

    # Get the templates.json file path
    package_dir = Path(__file__).parent.parent
    templates_json = package_dir / "tonguetoquill-collection" / "templates" / "templates.json"

    if not templates_json.exists():
        # Return empty list if file doesn't exist
        result: dict[str, list[dict[str, str]]] = {"templates": []}
        return [TextContent(type="text", text=str(result))]

    # Read and parse templates.json
    with open(templates_json) as f:
        templates_data = json.load(f)

    # Convert to TemplateListItem objects
    templates = [
        TemplateListItem(name=t["name"], description=t["description"])
        for t in templates_data
    ]

    result = {"templates": [t.model_dump() for t in templates]}
    return [TextContent(type="text", text=str(result))]


async def handle_render_document(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle render_document tool call."""
    markdown = arguments["markdown"]
    output_format = arguments.get("output_format", "PDF")
    validate_only = arguments.get("validate_only", False)

    quill_name = arguments.get("quill_name")
    if not quill_name:
        # Try to extract quill name from markdown using quillmark
        try:
            parsed = quillmark.ParsedDocument.from_markdown(markdown)
            quill_name = parsed.quill_tag()
        except quillmark.ParseError:
            pass

    if not quill_name:
        error = RenderError(
            error_type="ValidationError",
            error_message="No quill_name provided and no QUILL directive in frontmatter",
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    if quill_name not in QUILLS:
        error = RenderError(
            error_type="InvalidQuillName",
            error_message=f"Quill '{quill_name}' not found",
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    validation_result = await _validate_frontmatter(markdown, quill_name)
    if isinstance(validation_result, ValidationError):
        error = RenderError(
            error_type="ValidationError",
            error_message="Frontmatter validation failed",
            diagnostics=validation_result.errors,
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    if validate_only:
        return [TextContent(type="text", text=validation_result.model_dump_json())]

    # Use quillmark for actual rendering
    try:
        # Parse the markdown document
        parsed = quillmark.ParsedDocument.from_markdown(markdown)

        # Create workflow for the quill
        workflow = QUILLMARK_ENGINE.workflow_from_quill_name(quill_name)

        # Map output format
        qm_format = (
            quillmark.OutputFormat.PDF
            if output_format == "PDF"
            else quillmark.OutputFormat.SVG
        )

        # Render the document
        render_result = workflow.render(parsed, qm_format)

        # Convert quillmark artifacts to MCP artifacts
        artifacts = []
        for qm_artifact in render_result.artifacts:
            artifact_bytes = bytes(qm_artifact.bytes)
            mime_type = "application/pdf" if output_format == "PDF" else "image/svg+xml"
            
            # Generate UUID for this artifact
            render_id = str(uuid.uuid4())
            
            # Enforce cache size limit (FIFO eviction)
            if len(RENDER_CACHE) >= MAX_CACHE_SIZE:
                # Remove oldest entry (first key in dict)
                oldest_key = next(iter(RENDER_CACHE))
                del RENDER_CACHE[oldest_key]
            
            # Store in cache
            RENDER_CACHE[render_id] = (artifact_bytes, mime_type)
            
            # Create resource URI
            resource_uri = f"quillmark://render/{render_id}"
            
            artifact = Artifact(
                format=output_format,
                mime_type=mime_type,
                size_bytes=len(artifact_bytes),
                resource_uri=resource_uri,
            )
            artifacts.append(artifact)

        success = RenderSuccess(artifacts=artifacts)
        return [TextContent(type="text", text=success.model_dump_json())]

    except quillmark.ParseError as e:
        error = RenderError(
            error_type="ParseError",
            error_message=f"YAML parsing failed: {str(e)}",
            diagnostics=[
                Diagnostic(
                    severity="ERROR",
                    message=str(e),
                    code="parse_error",
                )
            ]
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    except quillmark.TemplateError as e:
        error = RenderError(
            error_type="TemplateError",
            error_message=f"Template processing failed: {str(e)}",
            diagnostics=[
                Diagnostic(
                    severity="ERROR",
                    message=str(e),
                    code="template_error",
                )
            ]
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    except quillmark.CompilationError as e:
        error = RenderError(
            error_type="CompilationError",
            error_message=f"Backend compilation failed: {str(e)}",
            diagnostics=[
                Diagnostic(
                    severity="ERROR",
                    message=str(e),
                    code="compilation_error",
                )
            ]
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    except quillmark.QuillmarkError as e:
        error = RenderError(
            error_type="QuillmarkError",
            error_message=f"Quillmark error: {str(e)}",
            diagnostics=[
                Diagnostic(
                    severity="ERROR",
                    message=str(e),
                    code="quillmark_error",
                )
            ]
        )
        return [TextContent(type="text", text=error.model_dump_json())]


async def handle_validate_frontmatter(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle validate_frontmatter tool call."""
    markdown = arguments["markdown"]
    quill_name = arguments.get("quill_name")

    if not quill_name:
        # Try to extract quill name from markdown using quillmark
        try:
            parsed = quillmark.ParsedDocument.from_markdown(markdown)
            quill_name = parsed.quill_tag()
        except quillmark.ParseError:
            pass

    if not quill_name:
        error = ValidationError(
            errors=[
                Diagnostic(
                    severity="ERROR",
                    message="No quill_name provided and no QUILL directive in frontmatter",
                    code="missing_quill",
                )
            ]
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    if quill_name not in QUILLS:
        error = ValidationError(
            errors=[
                Diagnostic(
                    severity="ERROR",
                    message=f"Quill '{quill_name}' not found",
                    code="invalid_quill",
                )
            ]
        )
        return [TextContent(type="text", text=error.model_dump_json())]

    result = await _validate_frontmatter(markdown, quill_name)
    return [TextContent(type="text", text=result.model_dump_json())]


async def handle_save_rendered_file(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle save_rendered_file tool call."""
    from pathlib import Path
    
    resource_uri = arguments["resource_uri"]
    file_path = arguments["file_path"]
    
    # Validate resource URI format
    if not resource_uri.startswith("quillmark://render/"):
        error = RenderError(
            error_type="InvalidResourceURI",
            error_message=f"Invalid resource URI format: {resource_uri}",
        )
        return [TextContent(type="text", text=error.model_dump_json())]
    
    # Extract render ID from URI
    render_id = resource_uri.replace("quillmark://render/", "")
    
    # Check if resource exists in cache
    if render_id not in RENDER_CACHE:
        error = RenderError(
            error_type="ResourceNotFound",
            error_message=f"Resource not found in cache: {resource_uri}",
        )
        return [TextContent(type="text", text=error.model_dump_json())]
    
    # Get the document bytes and mime type from cache
    artifact_bytes, mime_type = RENDER_CACHE[render_id]
    
    # Validate and prepare file path
    try:
        output_path = Path(file_path).expanduser().resolve()
        
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        output_path.write_bytes(artifact_bytes)
        
        # Prepare success response
        file_extension = "pdf" if mime_type == "application/pdf" else "svg"
        result = {
            "success": True,
            "file_path": str(output_path),
            "file_size": len(artifact_bytes),
            "mime_type": mime_type,
            "format": file_extension.upper(),
        }
        
        return [TextContent(type="text", text=str(result))]
        
    except PermissionError as e:
        error = RenderError(
            error_type="PermissionError",
            error_message=f"Permission denied writing to {file_path}: {str(e)}",
        )
        return [TextContent(type="text", text=error.model_dump_json())]
    
    except OSError as e:
        error = RenderError(
            error_type="FileSystemError",
            error_message=f"Failed to write file {file_path}: {str(e)}",
        )
        return [TextContent(type="text", text=error.model_dump_json())]
    
    except Exception as e:
        error = RenderError(
            error_type="UnknownError",
            error_message=f"Unexpected error saving file: {str(e)}",
        )
        return [TextContent(type="text", text=error.model_dump_json())]


async def _validate_frontmatter(
    markdown: str, quill_name: str
) -> ValidationSuccess | ValidationError:
    """Validate frontmatter against quill schema."""
    quill = QUILLS[quill_name]
    required_fields = quill.field_schemas

    # Use quillmark's ParsedDocument to parse frontmatter
    try:
        parsed = quillmark.ParsedDocument.from_markdown(markdown)
        parsed_fields = parsed.fields
    except quillmark.ParseError as e:
        return ValidationError(
            errors=[
                Diagnostic(
                    severity="ERROR",
                    message=f"Failed to parse frontmatter: {str(e)}",
                    code="parse_error",
                )
            ]
        )

    missing_fields = []
    errors = []

    for field_name, field_schema in required_fields.items():
        if field_schema.get("required", False) and field_name not in parsed_fields:
            missing_fields.append(field_name)
            errors.append(
                Diagnostic(
                    severity="ERROR",
                    message=f"Required field '{field_name}' is missing",
                    code="missing_field",
                    hint=f"Add '{field_name}: <value>' to your frontmatter",
                )
            )

    if errors:
        return ValidationError(
            parsed_fields=parsed_fields,
            missing_required_fields=missing_fields,
            errors=errors,
        )

    return ValidationSuccess(
        parsed_fields=parsed_fields,
        missing_required_fields=[],
    )