"""
METRO Blender Metadata Plugin

Standardizes 3D asset metadata to the METRO/DTRIP4H schema.
Auto-extracts technical properties from Blender, reads existing
metadata from imported files, and provides a UI panel for users
to fill in the remaining fields.

Part of DTRIP4H Work Package 9 — developed by METRO
(Metropolia Ammattikorkeakoulu OY).
"""

bl_info = {
    "name": "METRO Metadata",
    "author": "METRO (Metropolia Ammattikorkeakoulu OY)",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > METRO",
    "description": "Standardize 3D asset metadata to the METRO/DTRIP4H schema",
    "category": "Object",
    "doc_url": "https://github.com/narmeenm94/METRO-Blender-Plugin",
    "tracker_url": "https://github.com/narmeenm94/METRO-Blender-Plugin/issues",
}

from .properties import register_properties, unregister_properties
from .operators import register_operators, unregister_operators
from .panels import register_panels, unregister_panels


def register():
    """Register all add-on classes, properties, and panels."""
    register_properties()
    register_operators()
    register_panels()


def unregister():
    """Unregister all add-on classes, properties, and panels."""
    unregister_panels()
    unregister_operators()
    unregister_properties()
