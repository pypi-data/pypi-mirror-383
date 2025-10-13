> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CosmosImageToVideoLatent/en.md)

The CosmosImageToVideoLatent node creates video latent representations from input images. It generates a blank video latent and optionally encodes start and/or end images into the beginning and/or end frames of the video sequence. When images are provided, it also creates corresponding noise masks to indicate which parts of the latent should be preserved during generation.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `vae` | VAE | Yes | - | The VAE model used for encoding images into latent space |
| `width` | INT | No | 16 to MAX_RESOLUTION | The width of the output video in pixels (default: 1280) |
| `height` | INT | No | 16 to MAX_RESOLUTION | The height of the output video in pixels (default: 704) |
| `length` | INT | No | 1 to MAX_RESOLUTION | The number of frames in the video sequence (default: 121) |
| `batch_size` | INT | No | 1 to 4096 | The number of latent batches to generate (default: 1) |
| `start_image` | IMAGE | No | - | Optional image to encode at the beginning of the video sequence |
| `end_image` | IMAGE | No | - | Optional image to encode at the end of the video sequence |

**Note:** When neither `start_image` nor `end_image` are provided, the node returns a blank latent without any noise mask. When either image is provided, the corresponding sections of the latent are encoded and masked accordingly.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `latent` | LATENT | The generated video latent representation with optional encoded images and corresponding noise masks |
