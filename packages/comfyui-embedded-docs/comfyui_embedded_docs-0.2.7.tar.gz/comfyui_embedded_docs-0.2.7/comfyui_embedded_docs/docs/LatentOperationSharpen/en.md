> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentOperationSharpen/en.md)

The LatentOperationSharpen node applies a sharpening effect to latent representations using a Gaussian kernel. It works by normalizing the latent data, applying a convolution with a custom sharpening kernel, and then restoring the original luminance. This enhances the details and edges in the latent space representation.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `sharpen_radius` | INT | No | 1-31 | The radius of the sharpening kernel (default: 9) |
| `sigma` | FLOAT | No | 0.1-10.0 | The standard deviation for the Gaussian kernel (default: 1.0) |
| `alpha` | FLOAT | No | 0.0-5.0 | The sharpening intensity factor (default: 0.1) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `operation` | LATENT_OPERATION | Returns a sharpening operation that can be applied to latent data |
