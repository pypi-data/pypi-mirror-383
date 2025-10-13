> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EmptySD3LatentImage/en.md)

The EmptySD3LatentImage node creates a blank latent image tensor specifically formatted for Stable Diffusion 3 models. It generates a tensor filled with zeros that has the correct dimensions and structure expected by SD3 pipelines. This is commonly used as a starting point for image generation workflows.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `width` | INT | Yes | 16 to MAX_RESOLUTION (step: 16) | The width of the output latent image in pixels (default: 1024) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION (step: 16) | The height of the output latent image in pixels (default: 1024) |
| `batch_size` | INT | Yes | 1 to 4096 | The number of latent images to generate in a batch (default: 1) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `LATENT` | LATENT | A latent tensor containing blank samples with SD3-compatible dimensions |
