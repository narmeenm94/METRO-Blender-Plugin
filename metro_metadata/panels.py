"""
Blender UI panels for the METRO metadata plugin.
Displayed in the N-sidebar under the "METRO" tab.
"""

import bpy
from bpy.types import Panel

from .constants import SCENE_METADATA_KEY, SCHEMA_VERSION


# ===================================================================
# Base class for METRO panels
# ===================================================================

class METRO_PT_Base:
    """Mixin for all METRO sidebar panels."""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "METRO"


# ===================================================================
# Main header panel
# ===================================================================

class METRO_PT_Header(METRO_PT_Base, Panel):
    """METRO Metadata — standardize 3D asset metadata"""
    bl_idname = "METRO_PT_Header"
    bl_label = "METRO Metadata"

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Schema v{SCHEMA_VERSION}", icon="INFO")

        # Show injection status
        scene = context.scene
        if SCENE_METADATA_KEY in scene:
            layout.label(text="Metadata injected", icon="CHECKMARK")
        else:
            layout.label(text="No metadata injected yet", icon="ERROR")


# ===================================================================
# Auto Extract panel
# ===================================================================

class METRO_PT_AutoExtract(METRO_PT_Base, Panel):
    """Auto-extract technical metadata from scene"""
    bl_idname = "METRO_PT_AutoExtract"
    bl_label = "Auto Extract"
    bl_parent_id = "METRO_PT_Header"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        core = scene.metro_core
        tech = scene.metro_technical

        layout.operator("metro.extract_from_scene", icon="SCENE_DATA")

        # Show extracted values
        box = layout.box()
        col = box.column(align=True)
        col.label(text=f"Triangles: {core.tri_count:,}", icon="MESH_DATA")
        col.label(text=f"Vertices: {tech.vertex_count:,}", icon="VERTEXSEL")
        col.label(
            text=f"Bounding Box: {tech.bounding_box_x:.2f} x {tech.bounding_box_y:.2f} x {tech.bounding_box_z:.2f}",
            icon="OBJECT_DATA",
        )
        col.label(text=f"Materials: {tech.material_count}", icon="MATERIAL")
        col.label(
            text=f"Textures: {'Yes' if tech.has_textures else 'No'}",
            icon="TEXTURE",
        )
        col.label(
            text=f"PBR: {'Yes' if tech.supports_pbr else 'No'}",
            icon="SHADING_RENDERED",
        )


# ===================================================================
# Core Info panel
# ===================================================================

class METRO_PT_CoreInfo(METRO_PT_Base, Panel):
    """Core asset identification"""
    bl_idname = "METRO_PT_CoreInfo"
    bl_label = "Core Info"
    bl_parent_id = "METRO_PT_Header"

    def draw(self, context):
        layout = self.layout
        core = context.scene.metro_core

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(core, "asset_name")
        col.prop(core, "description")
        col.prop(core, "asset_format")
        col.prop(core, "tri_count")
        col.prop(core, "tags")
        col.prop(core, "use_case")


# ===================================================================
# Provenance panel
# ===================================================================

class METRO_PT_Provenance(METRO_PT_Base, Panel):
    """Asset provenance and origin"""
    bl_idname = "METRO_PT_Provenance"
    bl_label = "Provenance"
    bl_parent_id = "METRO_PT_Header"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prov = context.scene.metro_provenance

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(prov, "provenance_tool")
        col.prop(prov, "provenance_source_data")


# ===================================================================
# Access Control panel
# ===================================================================

class METRO_PT_AccessControl(METRO_PT_Base, Panel):
    """Access control and licensing"""
    bl_idname = "METRO_PT_AccessControl"
    bl_label = "Access Control"
    bl_parent_id = "METRO_PT_Header"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        access = context.scene.metro_access

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(access, "access_level")
        col.prop(access, "license")
        col.prop(access, "attribution_required")


# ===================================================================
# Lineage panel
# ===================================================================

class METRO_PT_Lineage(METRO_PT_Base, Panel):
    """Version lineage and derivation"""
    bl_idname = "METRO_PT_Lineage"
    bl_label = "Lineage"
    bl_parent_id = "METRO_PT_Header"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        lineage = context.scene.metro_lineage

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)

        # Lineage ID with generate button
        row = col.row(align=True)
        row.prop(lineage, "lineage_id")
        row.operator("metro.generate_lineage_id", text="", icon="FILE_REFRESH")

        col.prop(lineage, "derived_from_asset")


# ===================================================================
# Technical Details panel
# ===================================================================

class METRO_PT_Technical(METRO_PT_Base, Panel):
    """Technical and scientific metadata"""
    bl_idname = "METRO_PT_Technical"
    bl_label = "Technical Details"
    bl_parent_id = "METRO_PT_Header"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        tech = context.scene.metro_technical

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)

        # Auto-extracted (read-only display)
        col.label(text="Auto-Extracted:", icon="OUTLINER_OB_MESH")
        box = col.box()
        sub = box.column(align=True)
        sub.prop(tech, "vertex_count")
        sub.prop(tech, "material_count")
        sub.prop(tech, "has_textures")
        sub.prop(tech, "supports_pbr")

        col.separator()

        # Bounding box
        col.label(text="Bounding Box:", icon="OBJECT_DATA")
        box = col.box()
        sub = box.column(align=True)
        sub.prop(tech, "bounding_box_x")
        sub.prop(tech, "bounding_box_y")
        sub.prop(tech, "bounding_box_z")

        col.separator()

        # Manual fields
        col.label(text="Manual:", icon="GREASEPENCIL")
        col.prop(tech, "lod_levels")
        col.prop(tech, "scientific_domain")
        col.prop(tech, "source_data_format")
        col.prop(tech, "processing_parameters")


# ===================================================================
# Project & Deployment panel
# ===================================================================

class METRO_PT_Project(METRO_PT_Base, Panel):
    """Project-level and deployment metadata"""
    bl_idname = "METRO_PT_Project"
    bl_label = "Project & Deployment"
    bl_parent_id = "METRO_PT_Header"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        proj = context.scene.metro_project

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(proj, "project_phase")

        col.separator()

        # Theme
        col.label(text="Theme:", icon="COLLECTION_COLOR_05")
        col.prop(proj, "theme_scheme")
        col.prop(proj, "theme_code")

        col.separator()

        # Visualization
        col.label(text="Visualization:", icon="VIEW3D")
        col.prop(proj, "supports_vr")
        col.prop(proj, "supports_ar")

        col.separator()

        # Usage
        col.label(text="Usage:", icon="FILE_TEXT")
        col.prop(proj, "usage_constraints")
        col.prop(proj, "usage_guidelines_viewer")
        col.prop(proj, "usage_guidelines_notes")
        col.prop(proj, "deployment_notes")

        col.separator()

        # Restrictions
        col.label(text="Restrictions:", icon="LOCKED")
        col.prop(proj, "geo_restrictions")
        col.prop(proj, "access_scope")


# ===================================================================
# Actions panel
# ===================================================================

class METRO_PT_Actions(METRO_PT_Base, Panel):
    """Metadata actions — inject, export, read"""
    bl_idname = "METRO_PT_Actions"
    bl_label = "Actions"
    bl_parent_id = "METRO_PT_Header"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.scale_y = 1.3

        # Primary action — export 3D file with metadata embedded
        col.operator("metro.export_gltf", icon="EXPORT")

        col.separator()

        # Secondary actions
        col.operator("metro.inject_into_scene", icon="IMPORT")
        col.operator("metro.export_sidecar", icon="FILE_TEXT")

        col.separator()

        col.operator("metro.read_from_object", icon="EYEDROPPER")

        col.separator()

        col.operator("metro.clear_metadata", icon="TRASH")


# ===================================================================
# Registration
# ===================================================================

PANEL_CLASSES = [
    METRO_PT_Header,
    METRO_PT_AutoExtract,
    METRO_PT_CoreInfo,
    METRO_PT_Provenance,
    METRO_PT_AccessControl,
    METRO_PT_Lineage,
    METRO_PT_Technical,
    METRO_PT_Project,
    METRO_PT_Actions,
]


def register_panels():
    for cls in PANEL_CLASSES:
        bpy.utils.register_class(cls)


def unregister_panels():
    for cls in reversed(PANEL_CLASSES):
        bpy.utils.unregister_class(cls)
