> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ImageRotate/en.md)

The ImageRotate node rotates an input image by specified angles. It supports four rotation options: no rotation, 90 degrees clockwise, 180 degrees, and 270 degrees clockwise. The rotation is performed using efficient tensor operations that maintain the image data integrity.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input image to be rotated |
| `rotation` | STRING | Yes | "none"<br>"90 degrees"<br>"180 degrees"<br>"270 degrees" | The rotation angle to apply to the image |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `image` | IMAGE | The rotated output image |
