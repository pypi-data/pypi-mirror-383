> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ImageAddNoise/en.md)

The ImageAddNoise node adds random noise to an input image. It uses a specified random seed to generate consistent noise patterns and allows controlling the intensity of the noise effect. The resulting image maintains the same dimensions as the input but with added visual texture.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input image to which noise will be added |
| `seed` | INT | Yes | 0 to 18446744073709551615 | The random seed used for creating the noise (default: 0) |
| `strength` | FLOAT | Yes | 0.0 to 1.0 | Controls the intensity of the noise effect (default: 0.5) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `image` | IMAGE | The output image with added noise applied |
