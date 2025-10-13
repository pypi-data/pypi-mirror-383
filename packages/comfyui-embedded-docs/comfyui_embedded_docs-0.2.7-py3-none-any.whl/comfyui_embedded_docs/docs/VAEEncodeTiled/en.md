> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/VAEEncodeTiled/en.md)

The VAEEncodeTiled node processes images by breaking them into smaller tiles and encoding them using a Variational Autoencoder. This tiled approach allows handling of large images that might otherwise exceed memory limitations. The node supports both image and video VAEs, with separate tiling controls for spatial and temporal dimensions.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `pixels` | IMAGE | Yes | - | The input image data to be encoded |
| `vae` | VAE | Yes | - | The Variational Autoencoder model used for encoding |
| `tile_size` | INT | Yes | 64-4096 (step: 64) | The size of each tile for spatial processing (default: 512) |
| `overlap` | INT | Yes | 0-4096 (step: 32) | The amount of overlap between adjacent tiles (default: 64) |
| `temporal_size` | INT | Yes | 8-4096 (step: 4) | Only used for video VAEs: Amount of frames to encode at a time (default: 64) |
| `temporal_overlap` | INT | Yes | 4-4096 (step: 4) | Only used for video VAEs: Amount of frames to overlap (default: 8) |

**Note:** The `temporal_size` and `temporal_overlap` parameters are only relevant when using video VAEs and have no effect on standard image VAEs.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `LATENT` | LATENT | The encoded latent representation of the input image |
