"""
Blender PropertyGroup classes for METRO metadata.
Each group corresponds to a collapsible section in the UI panel.
"""

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup

from .constants import (
    ACCESS_LEVEL_ITEMS,
    ASSET_FORMAT_ITEMS,
    LICENSE_ITEMS,
    PROJECT_PHASE_ITEMS,
    USE_CASE_ITEMS,
)


# ===================================================================
# Core metadata
# ===================================================================

class METRO_PG_CoreMetadata(PropertyGroup):
    """Core asset identification fields."""

    asset_name: StringProperty(
        name="Name",
        description="Human-readable asset name (1-100 characters)",
        default="",
        maxlen=100,
    )
    description: StringProperty(
        name="Description",
        description="Detailed asset description (0-500 characters)",
        default="",
        maxlen=500,
    )
    asset_format: EnumProperty(
        name="Format",
        description="Primary file format of the 3D asset",
        items=ASSET_FORMAT_ITEMS,
        default="glb",
    )
    tri_count: IntProperty(
        name="Triangle Count",
        description="Triangle/polygon count (auto-extracted or manual)",
        default=0,
        min=0,
        max=10_000_000,
    )
    tags: StringProperty(
        name="Tags",
        description="Comma-separated tags (up to 20, each 1-50 chars)",
        default="",
        maxlen=1024,
    )
    use_case: EnumProperty(
        name="Use Case",
        description="Associated DTRIP4H use case",
        items=USE_CASE_ITEMS,
        default="NONE",
    )


# ===================================================================
# Provenance metadata
# ===================================================================

class METRO_PG_ProvenanceMetadata(PropertyGroup):
    """Asset provenance and origin information."""

    provenance_tool: StringProperty(
        name="Generation Tool",
        description="Tool name and version used to create this asset",
        default="",
        maxlen=255,
    )
    provenance_source_data: StringProperty(
        name="Source Data",
        description="Comma-separated source data references (URIs or filenames)",
        default="",
        maxlen=1024,
    )


# ===================================================================
# Access control metadata
# ===================================================================

class METRO_PG_AccessControlMetadata(PropertyGroup):
    """Access control and licensing fields."""

    access_level: EnumProperty(
        name="Access Level",
        description="Who can access this asset",
        items=ACCESS_LEVEL_ITEMS,
        default="private",
    )
    license: EnumProperty(
        name="License",
        description="License identifier",
        items=LICENSE_ITEMS,
        default="NONE",
    )
    attribution_required: BoolProperty(
        name="Attribution Required",
        description="Whether attribution is mandatory when using this asset",
        default=False,
    )


# ===================================================================
# Lineage metadata
# ===================================================================

class METRO_PG_LineageMetadata(PropertyGroup):
    """Version lineage and derivation tracking."""

    lineage_id: StringProperty(
        name="Lineage ID",
        description="Stable UUID grouping all versions of the same logical asset across nodes/URLs",
        default="",
        maxlen=36,
    )
    derived_from_asset: StringProperty(
        name="Derived From",
        description="Comma-separated URI(s) of parent asset/version (for forks/derivatives)",
        default="",
        maxlen=2048,
    )


# ===================================================================
# Technical / extended metadata
# ===================================================================

class METRO_PG_TechnicalMetadata(PropertyGroup):
    """Technical and scientific metadata."""

    # Auto-extracted fields
    vertex_count: IntProperty(
        name="Vertex Count",
        description="Total vertex count (auto-extracted)",
        default=0,
        min=0,
    )
    bounding_box_x: FloatProperty(
        name="Bounding Box X",
        description="Bounding box X dimension in Blender units",
        default=0.0,
        min=0.0,
        precision=4,
    )
    bounding_box_y: FloatProperty(
        name="Bounding Box Y",
        description="Bounding box Y dimension in Blender units",
        default=0.0,
        min=0.0,
        precision=4,
    )
    bounding_box_z: FloatProperty(
        name="Bounding Box Z",
        description="Bounding box Z dimension in Blender units",
        default=0.0,
        min=0.0,
        precision=4,
    )
    material_count: IntProperty(
        name="Material Count",
        description="Number of materials on the object (auto-extracted)",
        default=0,
        min=0,
    )
    has_textures: BoolProperty(
        name="Has Textures",
        description="Whether the object uses image textures (auto-extracted)",
        default=False,
    )
    supports_pbr: BoolProperty(
        name="Supports PBR",
        description="Whether the object uses Principled BSDF (PBR) shading (auto-extracted)",
        default=False,
    )

    # Manual fields
    lod_levels: IntProperty(
        name="LOD Levels",
        description="Number of level-of-detail variants (0 = not applicable)",
        default=0,
        min=0,
    )
    scientific_domain: StringProperty(
        name="Scientific Domain",
        description="Scientific domain (e.g., pharmaceutical-sciences, neuroscience)",
        default="",
        maxlen=100,
    )
    source_data_format: StringProperty(
        name="Source Data Format",
        description="Original input data format (e.g., csv, pdb, nc)",
        default="",
        maxlen=50,
    )
    processing_parameters: StringProperty(
        name="Processing Parameters",
        description="Generation parameters as JSON string",
        default="",
        maxlen=2048,
    )


# ===================================================================
# Project / RDF metadata
# ===================================================================

class METRO_PG_ProjectMetadata(PropertyGroup):
    """Project-level and deployment metadata."""

    project_phase: EnumProperty(
        name="Project Phase",
        description="Current project phase",
        items=PROJECT_PHASE_ITEMS,
        default="NONE",
    )
    theme_scheme: StringProperty(
        name="Theme Scheme",
        description="DCAT theme classification scheme URI",
        default="",
        maxlen=255,
    )
    theme_code: StringProperty(
        name="Theme Code",
        description="DCAT theme code",
        default="",
        maxlen=100,
    )
    supports_vr: BoolProperty(
        name="Supports VR",
        description="Whether this asset supports Virtual Reality viewing",
        default=False,
    )
    supports_ar: BoolProperty(
        name="Supports AR",
        description="Whether this asset supports Augmented Reality viewing",
        default=False,
    )
    usage_constraints: StringProperty(
        name="Usage Constraints",
        description="Usage constraints or limitations",
        default="",
        maxlen=1024,
    )
    usage_guidelines_viewer: StringProperty(
        name="Recommended Viewer",
        description="Recommended viewer application",
        default="",
        maxlen=255,
    )
    usage_guidelines_notes: StringProperty(
        name="Usage Notes",
        description="Additional usage notes or instructions",
        default="",
        maxlen=1024,
    )
    deployment_notes: StringProperty(
        name="Deployment Notes",
        description="Notes about deployment or integration requirements",
        default="",
        maxlen=1024,
    )
    geo_restrictions: StringProperty(
        name="Geographic Restrictions",
        description="Comma-separated geographic restriction codes (ISO 3166)",
        default="",
        maxlen=255,
    )
    access_scope: StringProperty(
        name="Access Scope",
        description="Comma-separated OAuth scopes required for access",
        default="",
        maxlen=512,
    )


# ===================================================================
# UI state (panel expand/collapse toggles)
# ===================================================================

class METRO_PG_UIState(PropertyGroup):
    """Tracks which UI sections are expanded/collapsed."""

    show_extract: BoolProperty(name="Show Extract", default=True)
    show_core: BoolProperty(name="Show Core", default=True)
    show_provenance: BoolProperty(name="Show Provenance", default=False)
    show_access: BoolProperty(name="Show Access Control", default=False)
    show_lineage: BoolProperty(name="Show Lineage", default=False)
    show_technical: BoolProperty(name="Show Technical", default=False)
    show_project: BoolProperty(name="Show Project", default=False)
    show_actions: BoolProperty(name="Show Actions", default=True)


# ===================================================================
# Registration
# ===================================================================

PROPERTY_CLASSES = [
    METRO_PG_CoreMetadata,
    METRO_PG_ProvenanceMetadata,
    METRO_PG_AccessControlMetadata,
    METRO_PG_LineageMetadata,
    METRO_PG_TechnicalMetadata,
    METRO_PG_ProjectMetadata,
    METRO_PG_UIState,
]


def register_properties():
    """Register all property groups and attach them to Scene."""
    for cls in PROPERTY_CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.metro_core = PointerProperty(type=METRO_PG_CoreMetadata)
    bpy.types.Scene.metro_provenance = PointerProperty(type=METRO_PG_ProvenanceMetadata)
    bpy.types.Scene.metro_access = PointerProperty(type=METRO_PG_AccessControlMetadata)
    bpy.types.Scene.metro_lineage = PointerProperty(type=METRO_PG_LineageMetadata)
    bpy.types.Scene.metro_technical = PointerProperty(type=METRO_PG_TechnicalMetadata)
    bpy.types.Scene.metro_project = PointerProperty(type=METRO_PG_ProjectMetadata)
    bpy.types.Scene.metro_ui = PointerProperty(type=METRO_PG_UIState)


def unregister_properties():
    """Unregister all property groups and remove from Scene."""
    del bpy.types.Scene.metro_ui
    del bpy.types.Scene.metro_project
    del bpy.types.Scene.metro_technical
    del bpy.types.Scene.metro_lineage
    del bpy.types.Scene.metro_access
    del bpy.types.Scene.metro_provenance
    del bpy.types.Scene.metro_core

    for cls in reversed(PROPERTY_CLASSES):
        bpy.utils.unregister_class(cls)
