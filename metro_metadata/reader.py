"""
Read existing metadata from imported 3D files and map to METRO schema.

Supports:
- glTF/GLB extras (preserved as Blender custom properties on import)
- Blend file custom properties (scene-level)
- Generic object custom properties
"""

import json
import bpy

from .constants import GLTF_EXTRAS_ALIASES, SCENE_METADATA_KEY


def read_from_active_object(scene):
    """
    Read metadata from the active object's custom properties and
    from the scene's custom properties, then populate METRO property groups.

    Args:
        scene: bpy.types.Scene

    Returns:
        dict with keys:
            "mapped"  — list of field names that were auto-populated
            "raw"     — dict of unrecognized custom properties
    """
    mapped_fields = []
    raw_props = {}

    # 1. Check if scene already has metro_metadata stored
    scene_meta = _read_scene_metro_metadata(scene)
    if scene_meta:
        mapped_fields.extend(_apply_metro_dict(scene, scene_meta))

    # 2. Read from active object custom properties (glTF extras land here)
    obj = bpy.context.active_object
    if obj:
        obj_meta, obj_raw = _read_object_custom_props(obj)
        if obj_meta:
            newly_mapped = _apply_metro_dict(scene, obj_meta)
            mapped_fields.extend(newly_mapped)
        raw_props.update(obj_raw)

    # 3. Read from scene-level custom properties (non-metro keys)
    scene_raw = _read_scene_custom_props(scene)
    raw_props.update(scene_raw)

    return {
        "mapped": list(set(mapped_fields)),
        "raw": raw_props,
    }


# -------------------------------------------------------------------
# Internal: read sources
# -------------------------------------------------------------------

def _read_scene_metro_metadata(scene):
    """Read the structured metro_metadata dict from scene custom props."""
    # Try structured IDProperties first
    if SCENE_METADATA_KEY in scene:
        raw = scene[SCENE_METADATA_KEY]
        # IDPropertyGroup -> dict
        if hasattr(raw, "to_dict"):
            return raw.to_dict()
        if isinstance(raw, dict):
            return raw
        # Might be a JSON string
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                pass

    # Fall back to JSON backup key
    json_key = SCENE_METADATA_KEY + "_json"
    if json_key in scene:
        raw = scene[json_key]
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                pass

    return None


def _read_object_custom_props(obj):
    """
    Read custom properties from an object (glTF extras appear here).

    Returns:
        (metro_compatible_dict, raw_unrecognized_dict)
    """
    metro = {}
    raw = {}

    for key in obj.keys():
        if key.startswith("_") or key in ("cycles", "cycles_visibility"):
            continue

        value = obj[key]

        # Convert IDPropertyGroup/Array to Python types
        value = _idprop_to_python(value)

        # Check if it's a nested metro_metadata block
        if key == SCENE_METADATA_KEY and isinstance(value, dict):
            metro.update(value)
            continue

        # Try to map via known aliases
        metro_field = GLTF_EXTRAS_ALIASES.get(key.lower())
        if metro_field:
            metro[metro_field] = value
        else:
            raw[key] = value

    return metro, raw


def _read_scene_custom_props(scene):
    """Read non-METRO custom properties from the scene."""
    raw = {}
    skip_keys = {
        SCENE_METADATA_KEY, "metro_core", "metro_provenance",
        "metro_access", "metro_lineage", "metro_technical",
        "metro_project", "metro_ui",
    }

    for key in scene.keys():
        if key.startswith("_") or key in skip_keys:
            continue

        value = scene[key]
        value = _idprop_to_python(value)

        # Try alias mapping
        metro_field = GLTF_EXTRAS_ALIASES.get(key.lower())
        if metro_field:
            # Will be handled in apply step; skip raw
            continue

        raw[key] = value

    return raw


# -------------------------------------------------------------------
# Internal: apply to property groups
# -------------------------------------------------------------------

def _apply_metro_dict(scene, data):
    """
    Apply a dict of metadata values to the scene's METRO property groups.

    Args:
        scene: bpy.types.Scene
        data: dict with either snake_case internal keys or camelCase API keys

    Returns:
        list of field names that were successfully mapped.
    """
    mapped = []

    core = scene.metro_core
    prov = scene.metro_provenance
    access = scene.metro_access
    lineage = scene.metro_lineage
    tech = scene.metro_technical
    proj = scene.metro_project

    # Core
    mapped += _set_if("asset_name", data, core, ["name", "asset_name", "title"])
    mapped += _set_if("description", data, core, ["description"])
    mapped += _set_if("asset_format", data, core, ["format", "asset_format"])
    mapped += _set_if("tri_count", data, core, ["triCount", "tri_count", "triangleCount"])
    mapped += _set_tags(data, core)
    mapped += _set_enum("use_case", data, core, ["useCase", "use_case"])

    # Provenance
    mapped += _set_if("provenance_tool", data, prov, ["provenance_tool", "generatedWith"])
    if "provenance" in data and isinstance(data["provenance"], dict):
        p = data["provenance"]
        if "tool" in p:
            prov.provenance_tool = str(p["tool"])
            mapped.append("provenance_tool")
        if "sourceData" in p:
            src = p["sourceData"]
            if isinstance(src, list):
                prov.provenance_source_data = ", ".join(str(s) for s in src)
            else:
                prov.provenance_source_data = str(src)
            mapped.append("provenance_source_data")

    # Access
    mapped += _set_enum("access_level", data, access, ["accessLevel", "access_level"])
    mapped += _set_if("license", data, access, ["license"])
    if "attributionRequired" in data or "attribution_required" in data:
        val = data.get("attributionRequired", data.get("attribution_required"))
        access.attribution_required = bool(val)
        mapped.append("attribution_required")

    # Lineage
    mapped += _set_if("lineage_id", data, lineage, ["lineageId", "lineage_id"])
    if "derivedFromAsset" in data or "derived_from_asset" in data:
        val = data.get("derivedFromAsset", data.get("derived_from_asset"))
        if isinstance(val, list):
            lineage.derived_from_asset = ", ".join(str(v) for v in val)
        else:
            lineage.derived_from_asset = str(val) if val else ""
        mapped.append("derived_from_asset")

    # Technical
    mapped += _set_int("vertex_count", data, tech, ["vertexCount", "vertex_count"])
    mapped += _set_int("lod_levels", data, tech, ["lodLevels", "lod_levels"])
    mapped += _set_if("scientific_domain", data, tech, ["scientificDomain", "scientific_domain"])
    mapped += _set_if("source_data_format", data, tech, ["sourceDataFormat", "source_data_format"])

    # Bounding box
    if "boundingBox" in data and isinstance(data["boundingBox"], dict):
        bb = data["boundingBox"]
        tech.bounding_box_x = float(bb.get("x", 0))
        tech.bounding_box_y = float(bb.get("y", 0))
        tech.bounding_box_z = float(bb.get("z", 0))
        mapped.append("bounding_box")

    # Material properties
    if "materialProperties" in data and isinstance(data["materialProperties"], dict):
        mp = data["materialProperties"]
        tech.material_count = int(mp.get("materialCount", 0))
        tech.has_textures = bool(mp.get("hasTextures", False))
        tech.supports_pbr = bool(mp.get("supportsPBR", False))
        mapped.append("material_properties")

    # Project
    mapped += _set_enum("project_phase", data, proj, ["projectPhase", "project_phase"])
    mapped += _set_if("usage_constraints", data, proj, ["usageConstraints", "usage_constraints"])
    mapped += _set_if("deployment_notes", data, proj, ["deploymentNotes", "deployment_notes"])

    # Visualization capabilities
    if "visualizationCapabilities" in data and isinstance(data["visualizationCapabilities"], dict):
        vc = data["visualizationCapabilities"]
        proj.supports_vr = bool(vc.get("supportsVR", False))
        proj.supports_ar = bool(vc.get("supportsAR", False))
        mapped.append("visualization_capabilities")

    return mapped


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _idprop_to_python(value):
    """Convert Blender IDProperty types to plain Python types."""
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "to_list"):
        return value.to_list()
    return value


def _set_if(prop_name, data, group, keys):
    """Set a string property if any of the keys exist in data."""
    for key in keys:
        if key in data and data[key]:
            try:
                setattr(group, prop_name, str(data[key]))
                return [prop_name]
            except (TypeError, AttributeError):
                pass
    return []


def _set_int(prop_name, data, group, keys):
    """Set an integer property if any of the keys exist in data."""
    for key in keys:
        if key in data and data[key] is not None:
            try:
                setattr(group, prop_name, int(data[key]))
                return [prop_name]
            except (TypeError, ValueError, AttributeError):
                pass
    return []


def _set_enum(prop_name, data, group, keys):
    """Set an enum property if any of the keys exist and match a valid value."""
    for key in keys:
        if key in data and data[key]:
            val = str(data[key])
            try:
                setattr(group, prop_name, val)
                return [prop_name]
            except TypeError:
                # Value not in enum items — skip
                pass
    return []


def _set_tags(data, core):
    """Set tags from various formats (list, comma-separated string)."""
    for key in ("tags", "keywords", "dcat:keyword"):
        if key in data and data[key]:
            val = data[key]
            if isinstance(val, list):
                core.tags = ", ".join(str(t) for t in val)
            else:
                core.tags = str(val)
            return ["tags"]
    return []
