> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/HunyuanImageToVideo/en.md)

The HunyuanImageToVideo node converts images into video latent representations using the Hunyuan video model. It takes conditioning inputs and optional starting images to generate video latents that can be further processed by video generation models. The node supports different guidance types for controlling how the starting image influences the video generation process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | Positive conditioning input for guiding the video generation |
| `vae` | VAE | Yes | - | VAE model used for encoding images into latent space |
| `width` | INT | Yes | 16 to MAX_RESOLUTION | Width of the output video in pixels (default: 848, step: 16) |
| `height` | INT | Yes | 16 to MAX_RESOLUTION | Height of the output video in pixels (default: 480, step: 16) |
| `length` | INT | Yes | 1 to MAX_RESOLUTION | Number of frames in the output video (default: 53, step: 4) |
| `batch_size` | INT | Yes | 1 to 4096 | Number of videos to generate simultaneously (default: 1) |
| `guidance_type` | COMBO | Yes | "v1 (concat)"<br>"v2 (replace)"<br>"custom" | Method for incorporating the starting image into video generation |
| `start_image` | IMAGE | No | - | Optional starting image to initialize the video generation |

**Note:** When `start_image` is provided, the node uses different guidance methods based on the selected `guidance_type`:

- "v1 (concat)": Concatenates the image latent with the video latent
- "v2 (replace)": Replaces initial video frames with the image latent
- "custom": Uses the image as a reference latent for guidance

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Modified positive conditioning with image guidance applied when start_image is provided |
| `latent` | LATENT | Video latent representation ready for further processing by video generation models |
