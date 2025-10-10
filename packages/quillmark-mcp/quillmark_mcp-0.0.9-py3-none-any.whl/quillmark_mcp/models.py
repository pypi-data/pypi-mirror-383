"""Data models for Quillmark MCP server."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class Location(BaseModel):
    """Location in a file."""

    file: str | None = None
    line: int
    column: int


class Diagnostic(BaseModel):
    """Diagnostic message (error, warning, or note)."""

    severity: Literal["ERROR", "WARNING", "NOTE"]
    message: str
    code: str | None = None
    location: Location | None = None
    hint: str | None = None


class FieldSchema(BaseModel):
    """Schema for a frontmatter field."""
    type: str | None = None
    required: bool = True
    description: str = ""
    example: Any = None
    default: Any = None


class QuillInfo(BaseModel):
    """Information about a Quill template."""

    name: str
    backend: str
    glue: str
    example: str | None = None
    description: str | None = None
    author: str | None = None
    version: str | None = None
    tags: list[str] | None = None
    frontmatter_fields: dict[str, FieldSchema] = Field(default_factory=dict)
    supported_formats: list[str] = Field(default_factory=lambda: ["PDF", "SVG"])


class QuillListItem(BaseModel):
    """Brief information about a Quill for list operations."""

    name: str
    backend: str
    description: str | None = None
    tags: list[str] | None = None


class Artifact(BaseModel):
    """Output artifact from rendering."""

    format: str
    mime_type: str
    size_bytes: int
    resource_uri: str | None = None


class RenderSuccess(BaseModel):
    """Successful render response."""

    success: Literal[True] = True
    artifacts: list[Artifact]


class RenderError(BaseModel):
    """Error response."""

    success: Literal[False] = False
    error_type: str
    error_message: str
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class ValidationSuccess(BaseModel):
    """Successful validation response."""

    valid: Literal[True] = True
    parsed_fields: dict[str, Any]
    missing_required_fields: list[str] = Field(default_factory=list)


class ValidationError(BaseModel):
    """Validation error response."""

    valid: Literal[False] = False
    parsed_fields: dict[str, Any] = Field(default_factory=dict)
    missing_required_fields: list[str] = Field(default_factory=list)
    errors: list[Diagnostic] = Field(default_factory=list)


class TemplateListItem(BaseModel):
    """Information about a markdown template."""

    name: str
    description: str
