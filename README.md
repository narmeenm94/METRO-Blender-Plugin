# METRO Blender Metadata Plugin

Blender add-on for standardizing 3D asset metadata to the METRO/DTRIP4H schema. Ensures all 3D assets used across the DTRIP4H research infrastructure follow a consistent, searchable metadata structure.

Part of [DTRIP4H](https://dtrip4h.eu/) Work Package 9 — developed by METRO (Metropolia Ammattikorkeakoulu OY).

---

## What it does

- **Auto-extracts** technical metadata from Blender scenes: triangle count, bounding box, material count, texture detection, PBR support, vertex count
- **Reads existing metadata** from imported glTF/GLB files (via extras) and maps it to the METRO standard
- **Provides a UI panel** (N-sidebar "METRO" tab) for filling in all metadata fields: core info, provenance, access control, lineage, technical details, and project metadata
- **Injects metadata** into Blender scene custom properties so it persists in .blend files and exports via glTF extras
- **Exports sidecar JSON** (.metro.json) compatible with the METRO 3D Asset Registry API

## Supported Blender Versions

- Blender 3.6 LTS
- Blender 4.0, 4.1, 4.2+

## Installation

1. Download or clone this repository
2. Zip the `metro_metadata/` folder (the folder itself, not its contents)
3. In Blender: **Edit > Preferences > Add-ons > Install**
4. Select the zip file
5. Enable "METRO Metadata" in the add-ons list

Or for development — symlink or copy the `metro_metadata/` folder into your Blender add-ons directory:

- **Windows**: `%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\`
- **macOS**: `~/Library/Application Support/Blender/<version>/scripts/addons/`
- **Linux**: `~/.config/blender/<version>/scripts/addons/`

## Usage

1. Open the **N-sidebar** in the 3D Viewport (press `N`)
2. Click the **METRO** tab
3. Click **Extract from Scene** to auto-populate technical fields
4. Fill in the remaining metadata (name, description, access level, license, etc.)
5. Click **Inject into Scene** to store metadata as custom properties
6. Optionally click **Export .metro.json** to create a sidecar file

### Reading Metadata from Imported Files

After importing a glTF/GLB file, click **Read from Active Object** to scan for existing metadata and map it to the METRO schema. Recognized fields auto-populate the panel; unrecognized fields are shown for manual review.

### Metadata Categories

| Category | Fields |
|----------|--------|
| **Core** | Name, description, format, triangle count, tags, use case |
| **Provenance** | Generation tool, source data references |
| **Access Control** | Access level, license, attribution required |
| **Lineage** | Lineage ID (stable UUID across versions), derived-from asset URIs |
| **Technical** | LOD levels, bounding box, materials, textures, PBR, vertex count, scientific domain, source format |
| **Project** | Project phase, theme, VR/AR support, usage constraints, deployment notes, geographic restrictions |

### Export Formats

- **Scene custom properties**: Persists in .blend files, auto-exports via glTF extras
- **Sidecar .metro.json**: Standalone JSON file compatible with the METRO 3D Asset Registry API
- **glTF extras**: When exporting to glTF/GLB, metadata is embedded in the extras field

## Schema Compatibility

The metadata structure matches the [METRO 3D Asset Registry API](https://github.com/narmeenm94/3D-Asset-Registry-API) schema (v1.0). Assets tagged with this plugin can be uploaded directly to any DTRIP4H node running the registry API.

## Funding

This project has received funding from the European Union's Horizon Europe research and innovation programme under grant agreement No. [EU101188432].

---

© 2025 METRO (Metropolia Ammattikorkeakoulu OY)
