> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ImageYUVToRGB/en.md)

The ImageYUVToRGB node converts YUV color space images to RGB color space. It takes three separate input images representing the Y (luma), U (blue projection), and V (red projection) channels and combines them into a single RGB image using color space conversion.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `Y` | IMAGE | Yes | - | The Y (luminance) channel input image |
| `U` | IMAGE | Yes | - | The U (blue projection) channel input image |
| `V` | IMAGE | Yes | - | The V (red projection) channel input image |

**Note:** All three input images (Y, U, and V) must be provided together and should have compatible dimensions for proper conversion.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | IMAGE | The converted RGB image |
