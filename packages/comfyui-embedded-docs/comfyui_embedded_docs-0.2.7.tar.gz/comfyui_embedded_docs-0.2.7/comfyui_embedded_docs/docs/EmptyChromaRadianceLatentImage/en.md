> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EmptyChromaRadianceLatentImage/en.md)

The EmptyChromaRadianceLatentImage node creates a blank latent image with specified dimensions for use in chroma radiance workflows. It generates a tensor filled with zeros that serves as a starting point for latent space operations. The node allows you to define the width, height, and batch size of the empty latent image.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `width` | INT | Yes | 16 to MAX_RESOLUTION | The width of the latent image in pixels (default: 1024, must be divisible by 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | The height of the latent image in pixels (default: 1024, must be divisible by 16) |
| `batch_size` | INT | No | 1 to 4096 | The number of latent images to generate in a batch (default: 1) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `samples` | LATENT | The generated empty latent image tensor with specified dimensions |
