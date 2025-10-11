"""Load quills from tonguetoquill-collection."""

from pathlib import Path

import quillmark


def get_quills_directory() -> Path:
    """Get the path to the quills directory."""
    # Get the root directory of the package
    package_dir = Path(__file__).parent.parent
    quills_dir = package_dir / "tonguetoquill-collection" / "quills"
    return quills_dir


def load_all_quills() -> dict[str, quillmark.Quill]:
    """Load all quills from the tonguetoquill-collection.

    Returns a dictionary mapping quill names to Quill objects.
    """
    quills_dir = get_quills_directory()

    if not quills_dir.exists():
        return {}

    quills = {}

    for quill_dir in quills_dir.iterdir():
        if not quill_dir.is_dir():
            continue

        # Check if this directory has a Quill.toml file
        quill_toml = quill_dir / "Quill.toml"
        if not quill_toml.exists():
            continue

        # Load quill using quillmark API
        quill = quillmark.Quill.from_path(str(quill_dir))
        quills[quill.name] = quill

    return quills
