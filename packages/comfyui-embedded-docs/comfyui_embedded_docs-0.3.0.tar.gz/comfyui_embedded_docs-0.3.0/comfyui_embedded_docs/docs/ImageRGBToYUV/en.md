> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ImageRGBToYUV/en.md)

The ImageRGBToYUV node converts RGB color images to the YUV color space. It takes an RGB image as input and separates it into three distinct channels: Y (luminance), U (blue projection), and V (red projection). Each output channel is returned as a separate grayscale image representing the corresponding YUV component.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input RGB image to be converted to YUV color space |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `Y` | IMAGE | The luminance (brightness) component of the YUV color space |
| `U` | IMAGE | The blue projection component of the YUV color space |
| `V` | IMAGE | The red projection component of the YUV color space |
