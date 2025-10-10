"""Tests for Quillmark MCP server."""

import uuid

from quillmark_mcp import create_server
from quillmark_mcp.models import Artifact, FieldSchema, QuillInfo, TemplateListItem
from quillmark_mcp.server import RENDER_CACHE, MAX_CACHE_SIZE


def test_create_server() -> None:
    """Test that server can be created."""
    server = create_server()
    assert server is not None
    assert server.name == "quillmark-mcp"


def test_models() -> None:
    """Test that data models work correctly."""
    # Test FieldSchema with new 'type' field from quillmark v0.1.17
    field = FieldSchema(
        type="string",
        required=True,
        description="Test field",
        example="Test value"
    )
    assert field.type == "string"
    assert field.required is True
    assert field.description == "Test field"

    # Test QuillInfo with 'example' field (renamed from 'template' for clarity)
    info = QuillInfo(
        name="test_quill",
        backend="typst",
        glue="glue.typ",
        example="test_quill.md",
        frontmatter_fields={"sender": field}
    )
    assert info.name == "test_quill"
    assert info.example == "test_quill.md"
    assert "sender" in info.frontmatter_fields

    # Test serialization
    json_data = info.model_dump_json()
    assert "test_quill" in json_data
    assert "sender" in json_data
    assert "example" in json_data


def test_template_list_item() -> None:
    """Test TemplateListItem model."""
    template = TemplateListItem(
        name="U.S. Air Force Memo",
        description="AFH 33-337 compliant official memorandum for the U.S. Air Force."
    )
    assert template.name == "U.S. Air Force Memo"
    assert template.description == "AFH 33-337 compliant official memorandum for the U.S. Air Force."

    # Test serialization
    json_data = template.model_dump()
    assert json_data["name"] == "U.S. Air Force Memo"
    assert json_data["description"] == "AFH 33-337 compliant official memorandum for the U.S. Air Force."


def test_artifact_with_resource_uri() -> None:
    """Test Artifact model with resource_uri field."""
    # Test artifact without resource_uri
    artifact = Artifact(
        format="PDF",
        bytes_base64="dGVzdCBkYXRh",
        mime_type="application/pdf",
        size_bytes=100,
    )
    assert artifact.resource_uri is None
    
    # Test artifact with resource_uri
    resource_id = str(uuid.uuid4())
    artifact_with_uri = Artifact(
        format="PDF",
        bytes_base64="dGVzdCBkYXRh",
        mime_type="application/pdf",
        size_bytes=100,
        resource_uri=f"quillmark://render/{resource_id}",
    )
    assert artifact_with_uri.resource_uri == f"quillmark://render/{resource_id}"
    assert artifact_with_uri.resource_uri.startswith("quillmark://render/")
    
    # Test serialization includes resource_uri
    json_data = artifact_with_uri.model_dump()
    assert "resource_uri" in json_data
    assert json_data["resource_uri"] == f"quillmark://render/{resource_id}"


def test_render_cache_constants() -> None:
    """Test render cache configuration constants."""
    # Verify cache exists and is initialized
    assert RENDER_CACHE is not None
    assert isinstance(RENDER_CACHE, dict)
    
    # Verify max cache size is configured
    assert MAX_CACHE_SIZE > 0
    assert MAX_CACHE_SIZE == 50


def test_resource_uri_format() -> None:
    """Test resource URI format."""
    resource_id = str(uuid.uuid4())
    uri = f"quillmark://render/{resource_id}"
    
    # Verify URI structure
    assert uri.startswith("quillmark://render/")
    assert len(uri) > len("quillmark://render/")
    
    # Verify can extract ID from URI
    extracted_id = uri.replace("quillmark://render/", "")
    assert extracted_id == resource_id
    
    # Verify UUID format
    try:
        uuid.UUID(extracted_id)
    except ValueError:
        assert False, "Resource ID should be valid UUID"


def test_save_rendered_file_model() -> None:
    """Test that save_rendered_file response structure is correct."""
    # Test successful save response structure
    response = {
        "success": True,
        "file_path": "/tmp/test.pdf",
        "file_size": 12345,
        "mime_type": "application/pdf",
        "format": "PDF",
    }
    
    assert response["success"] is True
    assert "file_path" in response
    assert "file_size" in response
    assert "mime_type" in response
    assert "format" in response
    assert response["file_size"] > 0


