> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StableZero123_Conditioning_Batched/en.md)

The StableZero123_Conditioning_Batched node processes an input image and generates conditioning data for 3D model generation. It encodes the image using CLIP vision and VAE models, then creates camera embeddings based on elevation and azimuth angles to produce positive and negative conditioning along with latent representations for batch processing.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip_vision` | CLIP_VISION | Yes | - | The CLIP vision model used for encoding the input image |
| `init_image` | IMAGE | Yes | - | The initial input image to be processed and encoded |
| `vae` | VAE | Yes | - | The VAE model used for encoding image pixels into latent space |
| `width` | INT | No | 16 to MAX_RESOLUTION | The output width for the processed image (default: 256, must be divisible by 8) |
| `height` | INT | No | 16 to MAX_RESOLUTION | The output height for the processed image (default: 256, must be divisible by 8) |
| `batch_size` | INT | No | 1 to 4096 | The number of conditioning samples to generate in the batch (default: 1) |
| `elevation` | FLOAT | No | -180.0 to 180.0 | The initial camera elevation angle in degrees (default: 0.0) |
| `azimuth` | FLOAT | No | -180.0 to 180.0 | The initial camera azimuth angle in degrees (default: 0.0) |
| `elevation_batch_increment` | FLOAT | No | -180.0 to 180.0 | The amount to increment elevation for each batch item (default: 0.0) |
| `azimuth_batch_increment` | FLOAT | No | -180.0 to 180.0 | The amount to increment azimuth for each batch item (default: 0.0) |

**Note:** The `width` and `height` parameters must be divisible by 8 as the node internally divides these dimensions by 8 for latent space generation.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The positive conditioning data containing image embeddings and camera parameters |
| `negative` | CONDITIONING | The negative conditioning data with zero-initialized embeddings |
| `latent` | LATENT | The latent representation of the processed image with batch indexing information |
