> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EmptyCosmosLatentVideo/en.md)

The EmptyCosmosLatentVideo node creates an empty latent video tensor with specified dimensions. It generates a zero-filled latent representation that can be used as a starting point for video generation workflows, with configurable width, height, length, and batch size parameters.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `width` | INT | Yes | 16 to MAX_RESOLUTION | The width of the latent video in pixels (default: 1280, must be divisible by 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | The height of the latent video in pixels (default: 704, must be divisible by 16) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | The number of frames in the latent video (default: 121) |
| `batch_size` | INT | No | 1 to 4096 | The number of latent videos to generate in a batch (default: 1) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `samples` | LATENT | The generated empty latent video tensor with zero values |
