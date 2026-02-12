"""
glTF export/import hooks for embedding METRO metadata in glTF/GLB files.

Uses Blender's official glTF extension API:
- glTF2ExportUserExtension: writes metadata into glTF scene extras on export
- glTF2ImportUserExtension: reads metadata from glTF scene extras on import

This means metadata travels INSIDE the 3D file — no sidecar needed.
When the file is uploaded to the METRO API, the API reads the extras
and auto-populates all metadata fields.
"""

import json
import bpy

from .injector import collect_metadata
from .reader import _apply_metro_dict


# ===================================================================
# glTF Export Hook
# ===================================================================

class glTF2ExportUserExtension:
    """
    Called by Blender's glTF exporter to inject custom data.

    Writes the full METRO metadata dict into the glTF scene's extras
    under the key "metro_metadata". This embeds the metadata directly
    into the exported .glTF/.glb file.
    """

    def __init__(self):
        # Required by Blender's glTF exporter API
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension
        self.properties = bpy.context.scene.metro_core

    def gather_scene_hook(self, export_settings, gltf_scene, blender_scene):
        """Called for each scene during glTF export."""
        if gltf_scene.extras is None:
            gltf_scene.extras = {}

        # Collect all METRO metadata from the scene's property groups
        metadata = collect_metadata(blender_scene)

        if metadata and metadata.get("name"):
            gltf_scene.extras["metro_metadata"] = metadata

    def gather_node_hook(self, export_settings, gltf_node, blender_object):
        """
        Called for each node (object) during glTF export.
        We store per-object technical data if the object is a mesh.
        """
        if blender_object is None or blender_object.type != "MESH":
            return

        # Only add per-object data if there are multiple mesh objects,
        # otherwise the scene-level data is sufficient.
        mesh_count = sum(
            1 for obj in bpy.context.scene.objects
            if obj.type == "MESH" and obj.visible_get()
        )
        if mesh_count <= 1:
            return

        # Add basic per-object stats
        if gltf_node.extras is None:
            gltf_node.extras = {}

        from .extractor import extract_from_object
        obj_data = extract_from_object(blender_object)
        if obj_data:
            gltf_node.extras["metro_object_stats"] = {
                "triCount": obj_data["tri_count"],
                "vertexCount": obj_data["vertex_count"],
                "boundingBox": {
                    "x": round(obj_data["bbox_x"], 4),
                    "y": round(obj_data["bbox_y"], 4),
                    "z": round(obj_data["bbox_z"], 4),
                },
            }


# ===================================================================
# glTF Import Hook
# ===================================================================

class glTF2ImportUserExtension:
    """
    Called by Blender's glTF importer to read custom data.

    Reads METRO metadata from glTF scene extras and populates
    the Blender scene's METRO property groups.
    """

    def __init__(self):
        self.properties = bpy.context.scene.metro_core

    def gather_import_scene_after_hook(self, gltf_scene, blender_scene, gltf):
        """Called after a glTF scene has been imported."""
        if gltf_scene is None:
            return

        extras = getattr(gltf_scene, "extras", None)
        if extras is None:
            return

        # Check for METRO metadata in scene extras
        metro_data = None

        if isinstance(extras, dict):
            metro_data = extras.get("metro_metadata")
        elif isinstance(extras, str):
            try:
                parsed = json.loads(extras)
                if isinstance(parsed, dict):
                    metro_data = parsed.get("metro_metadata")
            except (json.JSONDecodeError, ValueError):
                pass

        if metro_data and isinstance(metro_data, dict):
            _apply_metro_dict(blender_scene, metro_data)

            # Report to the user
            print(f"[METRO] Imported metadata: {len(metro_data)} fields from glTF extras")
