> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StableZero123_Conditioning/en.md)

The StableZero123_Conditioning node processes an input image and camera angles to generate conditioning data and latent representations for 3D model generation. It uses a CLIP vision model to encode the image features, combines them with camera embedding information based on elevation and azimuth angles, and produces positive and negative conditioning along with a latent representation for downstream 3D generation tasks.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip_vision` | CLIP_VISION | Yes | - | The CLIP vision model used to encode image features |
| `init_image` | IMAGE | Yes | - | The input image to be processed and encoded |
| `vae` | VAE | Yes | - | The VAE model used for encoding pixels to latent space |
| `width` | INT | No | 16 to MAX_RESOLUTION | Output width for the latent representation (default: 256, must be divisible by 8) |
| `height` | INT | No | 16 to MAX_RESOLUTION | Output height for the latent representation (default: 256, must be divisible by 8) |
| `batch_size` | INT | No | 1 to 4096 | Number of samples to generate in the batch (default: 1) |
| `elevation` | FLOAT | No | -180.0 to 180.0 | Camera elevation angle in degrees (default: 0.0) |
| `azimuth` | FLOAT | No | -180.0 to 180.0 | Camera azimuth angle in degrees (default: 0.0) |

**Note:** The `width` and `height` parameters must be divisible by 8 as the node automatically divides them by 8 to create the latent representation dimensions.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Positive conditioning data combining image features and camera embeddings |
| `negative` | CONDITIONING | Negative conditioning data with zero-initialized features |
| `latent` | LATENT | Latent representation with dimensions [batch_size, 4, height//8, width//8] |
