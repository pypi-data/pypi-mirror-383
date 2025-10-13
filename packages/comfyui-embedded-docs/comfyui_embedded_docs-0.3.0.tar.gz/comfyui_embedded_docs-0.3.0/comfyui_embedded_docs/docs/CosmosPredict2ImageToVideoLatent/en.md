> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CosmosPredict2ImageToVideoLatent/en.md)

The CosmosPredict2ImageToVideoLatent node creates video latent representations from images for video generation. It can generate a blank video latent or incorporate start and end images to create video sequences with specified dimensions and duration. The node handles the encoding of images into the appropriate latent space format for video processing.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `vae` | VAE | Yes | - | The VAE model used for encoding images into latent space |
| `width` | INT | No | 16 to MAX_RESOLUTION | The width of the output video in pixels (default: 848, must be divisible by 16) |
| `height` | INT | No | 16 to MAX_RESOLUTION | The height of the output video in pixels (default: 480, must be divisible by 16) |
| `length` | INT | No | 1 to MAX_RESOLUTION | The number of frames in the video sequence (default: 93, step: 4) |
| `batch_size` | INT | No | 1 to 4096 | The number of video sequences to generate (default: 1) |
| `start_image` | IMAGE | No | - | Optional starting image for the video sequence |
| `end_image` | IMAGE | No | - | Optional ending image for the video sequence |

**Note:** When neither `start_image` nor `end_image` are provided, the node generates a blank video latent. When images are provided, they are encoded and positioned at the beginning and/or end of the video sequence with appropriate masking.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `samples` | LATENT | The generated video latent representation containing the encoded video sequence |
| `noise_mask` | LATENT | A mask indicating which parts of the latent should be preserved during generation |
