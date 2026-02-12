"""
Blender operators for METRO metadata actions:
- Extract from scene
- Inject into scene
- Read from active object
- Export sidecar JSON
- Generate lineage UUID
- Clear all metadata
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from .extractor import extract_from_scene
from .reader import read_from_active_object
from .injector import inject_into_scene, export_sidecar_json
from .utils import generate_uuid, validate_metadata


# ===================================================================
# Extract from Scene
# ===================================================================

class METRO_OT_ExtractFromScene(Operator):
    """Auto-extract technical metadata from all mesh objects in the scene"""

    bl_idname = "metro.extract_from_scene"
    bl_label = "Extract from Scene"
    bl_description = "Auto-extract triangle count, bounding box, materials, textures, and PBR info from the scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        totals = extract_from_scene(scene)

        self.report(
            {"INFO"},
            f"Extracted: {totals['tri_count']:,} tris, "
            f"{totals['vertex_count']:,} verts, "
            f"{totals['material_count']} materials, "
            f"bbox ({totals['bbox_x']:.2f} x {totals['bbox_y']:.2f} x {totals['bbox_z']:.2f})"
        )
        return {"FINISHED"}


# ===================================================================
# Inject into Scene
# ===================================================================

class METRO_OT_InjectIntoScene(Operator):
    """Store METRO metadata as scene custom properties"""

    bl_idname = "metro.inject_into_scene"
    bl_label = "Inject into Scene"
    bl_description = (
        "Store all metadata as a scene custom property. "
        "Persists in .blend files and exports via glTF extras"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene

        # Validate first
        errors = validate_metadata(scene)
        if errors:
            for field, msg in errors:
                self.report({"WARNING"}, f"{field}: {msg}")
            self.report({"ERROR"}, "Fix validation errors before injecting")
            return {"CANCELLED"}

        data = inject_into_scene(scene)
        field_count = len([k for k in data.keys() if not k.startswith("_")])
        self.report({"INFO"}, f"Injected {field_count} metadata fields into scene")
        return {"FINISHED"}


# ===================================================================
# Read from Active Object
# ===================================================================

class METRO_OT_ReadFromObject(Operator):
    """Read metadata from the active object's custom properties and map to METRO schema"""

    bl_idname = "metro.read_from_object"
    bl_label = "Read from Active Object"
    bl_description = (
        "Read metadata from glTF extras or custom properties on the "
        "active object and auto-populate METRO fields"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene
        result = read_from_active_object(scene)

        mapped = result["mapped"]
        raw = result["raw"]

        if mapped:
            self.report({"INFO"}, f"Mapped {len(mapped)} fields: {', '.join(mapped[:5])}")
        else:
            self.report({"WARNING"}, "No recognized metadata found")

        if raw:
            self.report(
                {"INFO"},
                f"{len(raw)} unrecognized properties: {', '.join(list(raw.keys())[:5])}"
            )

        return {"FINISHED"}


# ===================================================================
# Export Sidecar JSON
# ===================================================================

class METRO_OT_ExportSidecar(Operator):
    """Export metadata as a .metro.json sidecar file"""

    bl_idname = "metro.export_sidecar"
    bl_label = "Export .metro.json"
    bl_description = "Export metadata as a standalone JSON file compatible with the METRO 3D Asset Registry API"
    bl_options = {"REGISTER"}

    filepath: StringProperty(
        name="File Path",
        description="Path for the sidecar JSON file",
        default="",
        subtype="FILE_PATH",
    )

    def invoke(self, context, event):
        # Pre-fill with .blend path if available
        if bpy.data.filepath:
            import os
            base = os.path.splitext(bpy.data.filepath)[0]
            self.filepath = base + ".metro.json"
        else:
            self.filepath = "untitled.metro.json"

        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        scene = context.scene

        # Validate first
        errors = validate_metadata(scene)
        if errors:
            for field, msg in errors:
                self.report({"WARNING"}, f"{field}: {msg}")
            self.report({"ERROR"}, "Fix validation errors before exporting")
            return {"CANCELLED"}

        try:
            path = export_sidecar_json(scene, filepath=self.filepath)
            self.report({"INFO"}, f"Exported sidecar to: {path}")
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        except OSError as e:
            self.report({"ERROR"}, f"Failed to write file: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}


# ===================================================================
# Generate Lineage UUID
# ===================================================================

class METRO_OT_GenerateLineageID(Operator):
    """Generate a new UUID v4 for the Lineage ID field"""

    bl_idname = "metro.generate_lineage_id"
    bl_label = "Generate UUID"
    bl_description = "Generate a new UUID v4 for grouping asset versions across nodes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.metro_lineage.lineage_id = generate_uuid()
        self.report({"INFO"}, "Generated new Lineage ID")
        return {"FINISHED"}


# ===================================================================
# Clear All Metadata
# ===================================================================

class METRO_OT_ClearMetadata(Operator):
    """Clear all METRO metadata fields"""

    bl_idname = "metro.clear_metadata"
    bl_label = "Clear All Metadata"
    bl_description = "Reset all METRO metadata fields to their defaults"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scene = context.scene

        # Reset each property group by iterating over its properties
        for group_name in (
            "metro_core", "metro_provenance", "metro_access",
            "metro_lineage", "metro_technical", "metro_project",
        ):
            group = getattr(scene, group_name, None)
            if group is None:
                continue
            for prop_name in group.__annotations__:
                try:
                    group.property_unset(prop_name)
                except (TypeError, AttributeError):
                    pass

        self.report({"INFO"}, "All METRO metadata cleared")
        return {"FINISHED"}


# ===================================================================
# Registration
# ===================================================================

OPERATOR_CLASSES = [
    METRO_OT_ExtractFromScene,
    METRO_OT_InjectIntoScene,
    METRO_OT_ReadFromObject,
    METRO_OT_ExportSidecar,
    METRO_OT_GenerateLineageID,
    METRO_OT_ClearMetadata,
]


def register_operators():
    for cls in OPERATOR_CLASSES:
        bpy.utils.register_class(cls)


def unregister_operators():
    for cls in reversed(OPERATOR_CLASSES):
        bpy.utils.unregister_class(cls)
