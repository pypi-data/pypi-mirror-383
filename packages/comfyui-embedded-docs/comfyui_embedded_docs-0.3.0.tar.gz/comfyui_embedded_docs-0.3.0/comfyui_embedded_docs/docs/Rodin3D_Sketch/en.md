> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Rodin3D_Sketch/en.md)

This node generates 3D assets using the Rodin API. It takes input images and converts them into 3D models through an external service. The node handles the entire process from task creation to downloading the final 3D model files.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `Images` | IMAGE | Yes | - | Input images to be converted into 3D models |
| `Seed` | INT | No | 0-65535 | Random seed value for generation (default: 0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `3D Model Path` | STRING | File path to the generated 3D model |
