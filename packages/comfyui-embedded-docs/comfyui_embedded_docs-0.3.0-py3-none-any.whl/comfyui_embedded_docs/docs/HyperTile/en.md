> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/HyperTile/en.md)

The HyperTile node applies a tiling technique to the attention mechanism in diffusion models to optimize memory usage during image generation. It divides the latent space into smaller tiles and processes them separately, then reassembles the results. This allows for working with larger image sizes without running out of memory.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The diffusion model to apply the HyperTile optimization to |
| `tile_size` | INT | No | 1-2048 | The target tile size for processing (default: 256) |
| `swap_size` | INT | No | 1-128 | Controls how the tiles are rearranged during processing (default: 2) |
| `max_depth` | INT | No | 0-10 | Maximum depth level to apply tiling (default: 0) |
| `scale_depth` | BOOLEAN | No | - | Whether to scale tile size based on depth level (default: False) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with HyperTile optimization applied |
