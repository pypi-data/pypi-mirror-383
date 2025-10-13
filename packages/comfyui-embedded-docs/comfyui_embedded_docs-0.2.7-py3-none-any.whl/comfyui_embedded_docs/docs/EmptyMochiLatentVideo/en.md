> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/EmptyMochiLatentVideo/en.md)

The EmptyMochiLatentVideo node creates an empty latent video tensor with specified dimensions. It generates a zero-filled latent representation that can be used as a starting point for video generation workflows. The node allows you to define the width, height, length, and batch size for the latent video tensor.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `width` | INT | Yes | 16 to MAX_RESOLUTION | The width of the latent video in pixels (default: 848, must be divisible by 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | The height of the latent video in pixels (default: 480, must be divisible by 16) |
| `length` | INT | Yes | 7 to MAX_RESOLUTION | The number of frames in the latent video (default: 25) |
| `batch_size` | INT | No | 1 to 4096 | The number of latent videos to generate in a batch (default: 1) |

**Note:** The actual latent dimensions are calculated as width/8 and height/8, and the temporal dimension is calculated as ((length - 1) // 6) + 1.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `samples` | LATENT | An empty latent video tensor with the specified dimensions, containing all zeros |
