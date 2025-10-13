> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EmptyLTXVLatentVideo/en.md)

The EmptyLTXVLatentVideo node creates an empty latent tensor for video processing. It generates a blank starting point with specified dimensions that can be used as input for video generation workflows. The node produces a zero-filled latent representation with the configured width, height, length, and batch size.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `width` | INT | Yes | 64 to MAX_RESOLUTION | The width of the latent video tensor (default: 768, step: 32) |
| `height` | INT | Yes | 64 to MAX_RESOLUTION | The height of the latent video tensor (default: 512, step: 32) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | The number of frames in the latent video (default: 97, step: 8) |
| `batch_size` | INT | No | 1 to 4096 | The number of latent videos to generate in a batch (default: 1) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `samples` | LATENT | The generated empty latent tensor with zero values in the specified dimensions |
