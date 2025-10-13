> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EmptyHunyuanImageLatent/en.md)

The EmptyHunyuanImageLatent node creates an empty latent tensor with specific dimensions for use with Hunyuan image generation models. It generates a blank starting point that can be processed through subsequent nodes in the workflow. The node allows you to specify the width, height, and batch size of the latent space.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `width` | INT | Yes | 64 to MAX_RESOLUTION | The width of the generated latent image in pixels (default: 2048, step: 32) |
| `height` | INT | Yes | 64 to MAX_RESOLUTION | The height of the generated latent image in pixels (default: 2048, step: 32) |
| `batch_size` | INT | Yes | 1 to 4096 | The number of latent samples to generate in a batch (default: 1) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `LATENT` | LATENT | An empty latent tensor with the specified dimensions for Hunyuan image processing |
