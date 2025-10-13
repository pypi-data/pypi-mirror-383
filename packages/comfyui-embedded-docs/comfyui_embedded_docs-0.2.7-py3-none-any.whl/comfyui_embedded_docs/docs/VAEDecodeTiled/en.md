> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/VAEDecodeTiled/en.md)

The VAEDecodeTiled node decodes latent representations into images using a tiled approach to handle large images efficiently. It processes the input in smaller tiles to manage memory usage while maintaining image quality. The node also supports video VAEs by processing temporal frames in chunks with overlap for smooth transitions.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `samples` | LATENT | Yes | - | The latent representation to be decoded into images |
| `vae` | VAE | Yes | - | The VAE model used for decoding the latent samples |
| `tile_size` | INT | Yes | 64-4096 (step: 32) | The size of each tile for processing (default: 512) |
| `overlap` | INT | Yes | 0-4096 (step: 32) | The amount of overlap between adjacent tiles (default: 64) |
| `temporal_size` | INT | Yes | 8-4096 (step: 4) | Only used for video VAEs: Amount of frames to decode at a time (default: 64) |
| `temporal_overlap` | INT | Yes | 4-4096 (step: 4) | Only used for video VAEs: Amount of frames to overlap (default: 8) |

**Note:** The node automatically adjusts overlap values if they exceed practical limits. If `tile_size` is less than 4 times the `overlap`, the overlap is reduced to one quarter of the tile size. Similarly, if `temporal_size` is less than twice the `temporal_overlap`, the temporal overlap is halved.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | The decoded image or images generated from the latent representation |
