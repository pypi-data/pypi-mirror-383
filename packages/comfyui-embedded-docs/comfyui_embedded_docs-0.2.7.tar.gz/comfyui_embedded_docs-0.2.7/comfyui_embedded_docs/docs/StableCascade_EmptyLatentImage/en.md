> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StableCascade_EmptyLatentImage/en.md)

The StableCascade_EmptyLatentImage node creates empty latent tensors for Stable Cascade models. It generates two separate latent representations - one for stage C and another for stage B - with appropriate dimensions based on the input resolution and compression settings. This node provides the starting point for the Stable Cascade generation pipeline.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `width` | INT | Yes | 256 to MAX_RESOLUTION | The width of the output image in pixels (default: 1024, step: 8) |
| `height` | INT | Yes | 256 to MAX_RESOLUTION | The height of the output image in pixels (default: 1024, step: 8) |
| `compression` | INT | Yes | 4 to 128 | The compression factor that determines the latent dimensions for stage C (default: 42, step: 1) |
| `batch_size` | INT | No | 1 to 4096 | The number of latent samples to generate in a batch (default: 1) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `stage_c` | LATENT | The stage C latent tensor with dimensions [batch_size, 16, height//compression, width//compression] |
| `stage_b` | LATENT | The stage B latent tensor with dimensions [batch_size, 4, height//4, width//4] |
