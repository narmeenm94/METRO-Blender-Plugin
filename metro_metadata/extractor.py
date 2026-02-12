"""
Auto-extraction of technical metadata from Blender scenes and objects.

Reads triangle count, bounding box, materials, textures, PBR support,
and vertex count directly from Blender's Python API.
"""

import os
import bpy
import bmesh
from mathutils import Vector


def extract_from_scene(scene):
    """
    Extract metadata from all mesh objects in the scene and populate
    the scene's METRO property groups.

    Args:
        scene: bpy.types.Scene — the scene to extract from.

    Returns:
        dict with extracted values for reporting.
    """
    core = scene.metro_core
    tech = scene.metro_technical

    totals = _aggregate_scene_meshes(scene)

    # Populate core
    core.tri_count = totals["tri_count"]

    # Populate technical
    tech.vertex_count = totals["vertex_count"]
    tech.bounding_box_x = totals["bbox_x"]
    tech.bounding_box_y = totals["bbox_y"]
    tech.bounding_box_z = totals["bbox_z"]
    tech.material_count = totals["material_count"]
    tech.has_textures = totals["has_textures"]
    tech.supports_pbr = totals["supports_pbr"]

    # Auto-detect format from blend file name
    if bpy.data.filepath:
        core.asset_format = "blend"

    # Auto-fill name from file or scene if empty
    if not core.asset_name:
        if bpy.data.filepath:
            core.asset_name = os.path.splitext(
                os.path.basename(bpy.data.filepath)
            )[0]
        else:
            core.asset_name = scene.name

    return totals


def extract_from_object(obj):
    """
    Extract metadata from a single mesh object.

    Args:
        obj: bpy.types.Object — must be a MESH object.

    Returns:
        dict with extracted values, or None if not a mesh.
    """
    if obj is None or obj.type != "MESH":
        return None

    return {
        "tri_count": _count_triangles(obj),
        "vertex_count": len(obj.data.vertices),
        "bbox_x": obj.dimensions.x,
        "bbox_y": obj.dimensions.y,
        "bbox_z": obj.dimensions.z,
        "material_count": len(obj.data.materials),
        "has_textures": _has_textures(obj),
        "supports_pbr": _supports_pbr(obj),
    }


# -------------------------------------------------------------------
# Internal helpers
# -------------------------------------------------------------------

def _aggregate_scene_meshes(scene):
    """Aggregate metadata across all mesh objects in the scene."""
    total_tris = 0
    total_verts = 0
    total_materials = set()
    any_textures = False
    any_pbr = False

    # Scene-level bounding box: min/max across all objects
    min_co = [float("inf")] * 3
    max_co = [float("-inf")] * 3

    mesh_objects = [
        obj for obj in scene.objects
        if obj.type == "MESH" and obj.visible_get()
    ]

    if not mesh_objects:
        return {
            "tri_count": 0,
            "vertex_count": 0,
            "bbox_x": 0.0,
            "bbox_y": 0.0,
            "bbox_z": 0.0,
            "material_count": 0,
            "has_textures": False,
            "supports_pbr": False,
        }

    for obj in mesh_objects:
        total_tris += _count_triangles(obj)
        total_verts += len(obj.data.vertices)

        # Materials
        for mat_slot in obj.material_slots:
            if mat_slot.material:
                total_materials.add(mat_slot.material.name)

        any_textures = any_textures or _has_textures(obj)
        any_pbr = any_pbr or _supports_pbr(obj)

        # World-space bounding box
        for corner in obj.bound_box:
            world_co = obj.matrix_world @ Vector(corner)
            for i in range(3):
                min_co[i] = min(min_co[i], world_co[i])
                max_co[i] = max(max_co[i], world_co[i])

    return {
        "tri_count": total_tris,
        "vertex_count": total_verts,
        "bbox_x": round(max_co[0] - min_co[0], 4),
        "bbox_y": round(max_co[1] - min_co[1], 4),
        "bbox_z": round(max_co[2] - min_co[2], 4),
        "material_count": len(total_materials),
        "has_textures": any_textures,
        "supports_pbr": any_pbr,
    }


def _count_triangles(obj):
    """
    Count triangles by temporarily triangulating the mesh via bmesh.
    Non-destructive — does not modify the actual mesh.
    """
    if obj.type != "MESH":
        return 0

    # Use the evaluated (modifiers applied) mesh if possible
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()

    if mesh is None:
        return 0

    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        tri_count = len(bm.faces)
    finally:
        bm.free()
        eval_obj.to_mesh_clear()

    return tri_count


def _has_textures(obj):
    """Check if any material on the object uses image textures."""
    for mat_slot in obj.material_slots:
        mat = mat_slot.material
        if mat and mat.use_nodes and mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    return True
    return False


def _supports_pbr(obj):
    """Check if any material on the object uses Principled BSDF."""
    for mat_slot in obj.material_slots:
        mat = mat_slot.material
        if mat and mat.use_nodes and mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    return True
    return False
