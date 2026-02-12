"""
Inject METRO metadata into Blender scene custom properties and
export a sidecar .metro.json file.

Scene custom properties persist in .blend files and are automatically
included in glTF extras on export, so no glTF export hook is needed.
"""

import json
import os

import bpy

from .constants import (
    FORMAT_TO_MIME,
    SCHEMA_VERSION,
    SCENE_METADATA_KEY,
    SIDECAR_EXTENSION,
)


def collect_metadata(scene):
    """
    Collect all METRO metadata from the scene's property groups
    into a single dict structured for the API.

    Args:
        scene: bpy.types.Scene

    Returns:
        dict — API-compatible metadata.
    """
    core = scene.metro_core
    prov = scene.metro_provenance
    access = scene.metro_access
    lineage = scene.metro_lineage
    tech = scene.metro_technical
    proj = scene.metro_project

    data = {
        "_schema_version": SCHEMA_VERSION,
    }

    # --- Core ---
    if core.asset_name:
        data["name"] = core.asset_name
    if core.description:
        data["description"] = core.description
    data["format"] = core.asset_format
    if core.tri_count > 0:
        data["triCount"] = core.tri_count
    if core.tags.strip():
        data["tags"] = [t.strip() for t in core.tags.split(",") if t.strip()]
    if core.use_case != "NONE":
        data["useCase"] = core.use_case

    # --- Provenance ---
    provenance = {}
    if prov.provenance_tool:
        provenance["tool"] = prov.provenance_tool
    if prov.provenance_source_data.strip():
        provenance["sourceData"] = [
            s.strip() for s in prov.provenance_source_data.split(",") if s.strip()
        ]
    if provenance:
        data["provenance"] = provenance

    # --- Access control ---
    data["accessLevel"] = access.access_level
    if access.license != "NONE":
        data["license"] = access.license
    data["attributionRequired"] = access.attribution_required

    # --- Lineage ---
    if lineage.lineage_id:
        data["lineageId"] = lineage.lineage_id
    if lineage.derived_from_asset.strip():
        uris = [u.strip() for u in lineage.derived_from_asset.split(",") if u.strip()]
        data["derivedFromAsset"] = uris if len(uris) > 1 else uris[0]

    # --- Technical ---
    if tech.lod_levels > 0:
        data["lodLevels"] = tech.lod_levels

    if tech.bounding_box_x > 0 or tech.bounding_box_y > 0 or tech.bounding_box_z > 0:
        data["boundingBox"] = {
            "x": round(tech.bounding_box_x, 4),
            "y": round(tech.bounding_box_y, 4),
            "z": round(tech.bounding_box_z, 4),
        }

    if tech.material_count > 0 or tech.has_textures or tech.supports_pbr:
        data["materialProperties"] = {
            "materialCount": tech.material_count,
            "hasTextures": tech.has_textures,
            "supportsPBR": tech.supports_pbr,
        }

    if tech.vertex_count > 0:
        data["qualityMetrics"] = {
            "vertexCount": tech.vertex_count,
        }

    if tech.scientific_domain:
        data["scientificDomain"] = tech.scientific_domain
    if tech.source_data_format:
        data["sourceDataFormat"] = tech.source_data_format
    if tech.processing_parameters.strip():
        try:
            data["processingParameters"] = json.loads(tech.processing_parameters)
        except (json.JSONDecodeError, ValueError):
            data["processingParameters"] = tech.processing_parameters

    # --- Project ---
    if proj.project_phase != "NONE":
        data["projectPhase"] = proj.project_phase

    if proj.theme_scheme or proj.theme_code:
        theme = {}
        if proj.theme_scheme:
            theme["scheme"] = proj.theme_scheme
        if proj.theme_code:
            theme["code"] = proj.theme_code
        data["theme"] = theme

    if proj.supports_vr or proj.supports_ar:
        data["visualizationCapabilities"] = {
            "supportsVR": proj.supports_vr,
            "supportsAR": proj.supports_ar,
        }

    if proj.usage_constraints:
        data["usageConstraints"] = proj.usage_constraints

    if proj.usage_guidelines_viewer or proj.usage_guidelines_notes:
        guidelines = {}
        if proj.usage_guidelines_viewer:
            guidelines["recommended_viewer"] = proj.usage_guidelines_viewer
        if proj.usage_guidelines_notes:
            guidelines["notes"] = proj.usage_guidelines_notes
        data["usageGuidelines"] = guidelines

    if proj.deployment_notes:
        data["deploymentNotes"] = proj.deployment_notes

    if proj.geo_restrictions.strip():
        data["geoRestrictions"] = [
            g.strip() for g in proj.geo_restrictions.split(",") if g.strip()
        ]

    if proj.access_scope.strip():
        data["accessScope"] = [
            s.strip() for s in proj.access_scope.split(",") if s.strip()
        ]

    # --- Encoding format (derived) ---
    fmt = core.asset_format
    if fmt in FORMAT_TO_MIME:
        data["encodingFormat"] = FORMAT_TO_MIME[fmt]

    return data


def inject_into_scene(scene):
    """
    Store the collected metadata as a scene custom property.
    This persists in .blend files and exports via glTF extras.

    Args:
        scene: bpy.types.Scene

    Returns:
        dict — the metadata that was injected.
    """
    data = collect_metadata(scene)

    # Store as JSON string in scene custom property
    # (IDProperties don't support nested dicts well, JSON string is safest)
    scene[SCENE_METADATA_KEY] = json.dumps(data, indent=2, ensure_ascii=False)

    return data


def export_sidecar_json(scene, filepath=None):
    """
    Export metadata as a .metro.json sidecar file.

    Args:
        scene: bpy.types.Scene
        filepath: Optional explicit path. If None, derives from .blend file path.

    Returns:
        str — path of the exported file.

    Raises:
        ValueError if no filepath can be determined.
    """
    data = collect_metadata(scene)

    if filepath is None:
        blend_path = bpy.data.filepath
        if not blend_path:
            raise ValueError(
                "No .blend file saved. Save the file first or specify an export path."
            )
        base = os.path.splitext(blend_path)[0]
        filepath = base + SIDECAR_EXTENSION

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath
