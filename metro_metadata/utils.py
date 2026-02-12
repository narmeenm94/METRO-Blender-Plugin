"""
Utility helpers for the METRO metadata plugin.
UUID generation, validation, and formatting helpers.
"""

import re
import uuid


# UUID v4 pattern
_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def generate_uuid():
    """Generate a new UUID v4 string."""
    return str(uuid.uuid4())


def is_valid_uuid(value):
    """Check if a string is a valid UUID v4."""
    if not value or not isinstance(value, str):
        return False
    return bool(_UUID_PATTERN.match(value))


def parse_comma_list(value):
    """
    Parse a comma-separated string into a list of stripped, non-empty strings.

    Args:
        value: str — e.g. "tag1, tag2, tag3"

    Returns:
        list[str] — e.g. ["tag1", "tag2", "tag3"]
    """
    if not value or not isinstance(value, str):
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def to_comma_string(items):
    """
    Convert a list of strings to a comma-separated string.

    Args:
        items: list[str] or str

    Returns:
        str
    """
    if isinstance(items, str):
        return items
    if isinstance(items, (list, tuple)):
        return ", ".join(str(item) for item in items if item)
    return str(items) if items else ""


def truncate(text, max_length):
    """Truncate text to max_length, adding ellipsis if needed."""
    if not text or len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def validate_name(name):
    """
    Validate an asset name per API rules (1-100 chars).

    Returns:
        (bool, str) — (is_valid, error_message)
    """
    if not name:
        return False, "Name is required"
    if len(name) > 100:
        return False, f"Name too long ({len(name)}/100 characters)"
    return True, ""


def validate_description(description):
    """
    Validate a description per API rules (0-500 chars).

    Returns:
        (bool, str) — (is_valid, error_message)
    """
    if description and len(description) > 500:
        return False, f"Description too long ({len(description)}/500 characters)"
    return True, ""


def validate_tags(tags_string):
    """
    Validate tags: up to 20 tags, each 1-50 characters.

    Args:
        tags_string: comma-separated string

    Returns:
        (bool, str) — (is_valid, error_message)
    """
    tags = parse_comma_list(tags_string)
    if len(tags) > 20:
        return False, f"Too many tags ({len(tags)}/20)"
    for tag in tags:
        if len(tag) > 50:
            return False, f"Tag '{truncate(tag, 20)}' too long ({len(tag)}/50 chars)"
    return True, ""


def validate_metadata(scene):
    """
    Validate all metadata fields on the scene.

    Args:
        scene: bpy.types.Scene

    Returns:
        list of (field_name, error_message) tuples. Empty if all valid.
    """
    errors = []

    core = scene.metro_core

    valid, msg = validate_name(core.asset_name)
    if not valid:
        errors.append(("name", msg))

    valid, msg = validate_description(core.description)
    if not valid:
        errors.append(("description", msg))

    valid, msg = validate_tags(core.tags)
    if not valid:
        errors.append(("tags", msg))

    lineage = scene.metro_lineage
    if lineage.lineage_id and not is_valid_uuid(lineage.lineage_id):
        errors.append(("lineageId", "Lineage ID must be a valid UUID v4"))

    return errors
