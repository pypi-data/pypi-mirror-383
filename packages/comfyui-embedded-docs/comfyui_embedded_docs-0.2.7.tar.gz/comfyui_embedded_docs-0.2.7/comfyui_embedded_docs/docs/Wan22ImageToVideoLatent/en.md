> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Wan22ImageToVideoLatent/en.md)

The Wan22ImageToVideoLatent node creates video latent representations from images. It generates a blank video latent space with specified dimensions and can optionally encode a starting image sequence into the beginning frames. When a start image is provided, it encodes the image into the latent space and creates a corresponding noise mask for the inpainted regions.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `vae` | VAE | Yes | - | The VAE model used for encoding images into latent space |
| `width` | INT | No | 32 to MAX_RESOLUTION | The width of the output video in pixels (default: 1280, step: 32) |
| `height` | INT | No | 32 to MAX_RESOLUTION | The height of the output video in pixels (default: 704, step: 32) |
| `length` | INT | No | 1 to MAX_RESOLUTION | The number of frames in the video sequence (default: 49, step: 4) |
| `batch_size` | INT | No | 1 to 4096 | The number of batches to generate (default: 1) |
| `start_image` | IMAGE | No | - | Optional starting image sequence to encode into the video latent |

**Note:** When `start_image` is provided, the node encodes the image sequence into the beginning frames of the latent space and generates a corresponding noise mask. The width and height parameters must be divisible by 16 for proper latent space dimensions.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `samples` | LATENT | The generated video latent representation |
| `noise_mask` | LATENT | The noise mask indicating which regions should be denoised during generation |
