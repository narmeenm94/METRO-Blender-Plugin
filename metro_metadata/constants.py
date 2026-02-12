"""
Constants, enums, and field definitions for the METRO metadata schema.
Mirrors the METRO 3D Asset Registry API v1.0.
"""

# Schema version — used in exported JSON and scene custom properties
SCHEMA_VERSION = "1.0.0"

# Custom property key used on bpy.context.scene
SCENE_METADATA_KEY = "metro_metadata"

# Sidecar file extension
SIDECAR_EXTENSION = ".metro.json"

# ---------------------------------------------------------------------------
# Enum definitions (match API exactly)
# ---------------------------------------------------------------------------

# Blender EnumProperty items: (identifier, name, description)
ASSET_FORMAT_ITEMS = [
    ("gltf", "glTF", "GL Transmission Format"),
    ("glb", "GLB", "GL Transmission Format (Binary)"),
    ("usdz", "USDZ", "Universal Scene Description (Zip)"),
    ("blend", "Blend", "Blender native format"),
    ("fbx", "FBX", "Autodesk FBX"),
    ("obj", "OBJ", "Wavefront OBJ"),
    ("stl", "STL", "Stereolithography"),
    ("ply", "PLY", "Polygon File Format"),
]

ACCESS_LEVEL_ITEMS = [
    ("private", "Private", "Only owner can access"),
    ("group", "Group", "Authorized users/institutions"),
    ("institution", "Institution", "Same institution members"),
    ("consortium", "Consortium", "All DTRIP4H members"),
    ("approval_required", "Approval Required", "Explicit approval needed"),
    ("public", "Public", "Any authenticated user"),
]

USE_CASE_ITEMS = [
    ("NONE", "None", "No specific use case"),
    ("UC2", "UC2", "Use Case 2"),
    ("UC3", "UC3", "Use Case 3"),
    ("UC4", "UC4", "Use Case 4"),
    ("UC5", "UC5", "Use Case 5"),
]

PROJECT_PHASE_ITEMS = [
    ("NONE", "None", "Not specified"),
    ("prototype", "Prototype", "Early development / proof of concept"),
    ("development", "Development", "Active development"),
    ("production", "Production", "Production-ready"),
    ("archived", "Archived", "No longer actively maintained"),
]

# Common license identifiers
LICENSE_ITEMS = [
    ("NONE", "None", "No license specified"),
    ("CC-BY-4.0", "CC BY 4.0", "Creative Commons Attribution 4.0"),
    ("CC-BY-SA-4.0", "CC BY-SA 4.0", "Creative Commons Attribution-ShareAlike 4.0"),
    ("CC-BY-NC-4.0", "CC BY-NC 4.0", "Creative Commons Attribution-NonCommercial 4.0"),
    ("CC-BY-NC-SA-4.0", "CC BY-NC-SA 4.0", "Creative Commons Attribution-NonCommercial-ShareAlike 4.0"),
    ("CC0-1.0", "CC0 1.0", "Creative Commons Zero / Public Domain"),
    ("MIT", "MIT", "MIT License"),
    ("Apache-2.0", "Apache 2.0", "Apache License 2.0"),
    ("OTHER", "Other", "Other license (specify in description)"),
]

# ---------------------------------------------------------------------------
# Format-to-MIME mapping (matches API context.py)
# ---------------------------------------------------------------------------

FORMAT_TO_MIME = {
    "gltf": "model/gltf+json",
    "glb": "model/gltf-binary",
    "usdz": "model/vnd.usdz+zip",
    "blend": "application/x-blender",
    "fbx": "application/x-fbx",
    "obj": "model/obj",
    "stl": "model/stl",
    "ply": "application/x-ply",
}

# ---------------------------------------------------------------------------
# Field name mappings: internal (snake_case) -> API (camelCase)
# Used when building the JSON output for the sidecar / API upload.
# ---------------------------------------------------------------------------

FIELD_MAP_TO_API = {
    # Core
    "asset_name": "name",
    "description": "description",
    "asset_format": "format",
    "tri_count": "triCount",
    "tags": "tags",
    "use_case": "useCase",
    # Provenance
    "provenance_tool": "provenance.tool",
    "provenance_source_data": "provenance.sourceData",
    # Access control
    "access_level": "accessLevel",
    "license": "license",
    "attribution_required": "attributionRequired",
    # Lineage
    "lineage_id": "lineageId",
    "derived_from_asset": "derivedFromAsset",
    # Technical / extended
    "lod_levels": "lodLevels",
    "bounding_box_x": "boundingBox.x",
    "bounding_box_y": "boundingBox.y",
    "bounding_box_z": "boundingBox.z",
    "material_count": "materialProperties.materialCount",
    "has_textures": "materialProperties.hasTextures",
    "supports_pbr": "materialProperties.supportsPBR",
    "vertex_count": "qualityMetrics.vertexCount",
    "scientific_domain": "scientificDomain",
    "source_data_format": "sourceDataFormat",
    "processing_parameters": "processingParameters",
    # Project / RDF
    "project_phase": "projectPhase",
    "theme_scheme": "theme.scheme",
    "theme_code": "theme.code",
    "supports_vr": "visualizationCapabilities.supportsVR",
    "supports_ar": "visualizationCapabilities.supportsAR",
    "usage_constraints": "usageConstraints",
    "usage_guidelines_viewer": "usageGuidelines.recommended_viewer",
    "usage_guidelines_notes": "usageGuidelines.notes",
    "deployment_notes": "deploymentNotes",
    "geo_restrictions": "geoRestrictions",
    "access_scope": "accessScope",
}

# Reverse mapping: API camelCase -> internal snake_case
FIELD_MAP_FROM_API = {v: k for k, v in FIELD_MAP_TO_API.items()}

# ---------------------------------------------------------------------------
# glTF extras key names commonly used by other tools
# Helps the reader map foreign metadata into METRO fields.
# ---------------------------------------------------------------------------

GLTF_EXTRAS_ALIASES = {
    # Common glTF extras keys -> METRO field
    "title": "asset_name",
    "name": "asset_name",
    "description": "description",
    "author": "provenance_tool",
    "generator": "provenance_tool",
    "license": "license",
    "copyright": "license",
    "tags": "tags",
    "keywords": "tags",
}
