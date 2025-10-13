> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/VoxelToMeshBasic/en.md)

The VoxelToMeshBasic node converts 3D voxel data into mesh geometry. It processes voxel volumes by applying a threshold value to determine which parts of the volume become solid surfaces in the resulting mesh. The node outputs a complete mesh structure with vertices and faces that can be used for 3D rendering and modeling.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `voxel` | VOXEL | Yes | - | The 3D voxel data to convert into a mesh |
| `threshold` | FLOAT | Yes | -1.0 to 1.0 | The threshold value used to determine which voxels become part of the mesh surface (default: 0.6) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `MESH` | MESH | The generated 3D mesh containing vertices and faces |
